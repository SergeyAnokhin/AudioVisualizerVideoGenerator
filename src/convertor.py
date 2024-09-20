from moviepy.editor import *
import os
import cv2
import equalizers
from model import Profile
import tools

def create_video_from_folder(audio_file, profile: Profile, gif_file=None, part=None, num_cores=1, is_audio=True,
                             output_file=None, colormap = cv2.COLORMAP_JET):
    folder = tools.get_directory_from_path(audio_file)
    part_str = f"({part})" if part != None else ""
    print(f"CONVERTOR{part_str} :: Start creating from: 📂{folder}", )

    # Список изображений в папке
    images = [os.path.join(folder, img) for img in sorted(os.listdir(folder)) if img.endswith(('.png', '.jpg', '.jpeg', '.jfif'))]

    # Длительность аудио-файла
    audio = AudioFileClip(audio_file)
    audio_duration = audio.duration
    print(f"CONVERTOR{part_str} :: 🎶Audio ⌛duration: {audio_duration} secs")
    
    # tools.suggest_frequency_bands(audio_file)
    
    start, end = 0, audio_duration
    if profile and profile.crop != None and not profile.crop.is_empty():
        start = profile.crop.start
        end = min(profile.crop.end or audio_duration, audio_duration)
        print(f"CONVERTOR{part_str} :: Profile ✂️{part}: ⏱ [{start:3.0f}...{end:3.0f}] secs")
    elif part != None:
        start, end = tools.get_segment_duration(audio_duration, part, num_cores)
        print(f"CONVERTOR{part_str} :: Part ✂️{part}: ⏱ [{start:3.0f}...{end:3.0f}] secs")

    # Длительность каждого изображения (в секундах)
    image_duration = 20  # Измените на желаемую длительность
    
    # Создаем слайд-шоу с повторением и затемнением
    print(f"CONVERTOR{part_str} :: ⏩Create looping slideshow with fade transition")
    imageClips = [ImageClip(img) for img in images]
    imageClips = tools.adjust_image_clips(imageClips, 1024, mode='crop')
    slideshow = tools.create_slideshow_with_fade(imageClips, audio_duration=audio_duration, 
                                           image_duration=image_duration, fade_duration=0.1)

    # Проверяем наличие GIF-файла и накладываем его на видео
    final_video = tools.add_gif(gif_file, audio_duration, slideshow)

    # Добавляем аудио к видео
    final_video = final_video.set_audio(audio)

    # Создаем эквалайзерный клип
    print(f"CONVERTOR{part_str} :: ⏩Create equalizer visualization")
    # Настройка диапазонов частот для каждой из четырех суб-точек с усилением
    frequency_bands = [
        {'band': (20, 80), 'amplification': 2.0},
        {'band': (80, 255), 'amplification': 14.0}, # humain voice band
        {'band': (255, 500), 'amplification': 3.0},
        {'band': (500, 8000), 'amplification': 40.0},
    ]
    # all color maps : https://learnopencv.com/applycolormap-for-pseudocoloring-in-opencv-c-python/
    equalizer_clip = equalizers.create_equalizer_clip(audio_file, duration=audio_duration,
                        size=final_video.size, 
                        colormap=colormap, circle_radius=300,
                          center_dot_size=35, edge_dot_size=5,
                          colormap_positions=[0.0, 0.33, 0.66, 1.0],
                          num_dots=30,
                          circle_vertical_position_percent=7,
                          amplitude_threshold=0.6,
                          debug_mode=False, fps=profile.fps,
                          frequency_bands=frequency_bands)

    # Делаем фон прозрачным (удаляем определенный цвет)
    equalizer_clip = equalizer_clip.fx(vfx.mask_color, color=[0, 0, 0], thr=100, s=5)   
    equalizer_clip = equalizer_clip.set_opacity(0.2)  # Опционально: установить прозрачность

    tools.inspect_clip("final_video", final_video)
    tools.inspect_clip("equalizer_clip", equalizer_clip)
    # Накладываем эквалайзер поверх финального видео
    print(f"CONVERTOR{part_str} :: ➕Add equalizer visualization")
    final_video = CompositeVideoClip([final_video, equalizer_clip])

    # # Создаем текстовый клип
    # text_clip = tools.create_text_clip(
    #     text="Ваш текст здесь",
    #     duration=10,             # Текст будет отображаться 10 секунд
    #     start_time=5,            # Начнет отображаться с 5-й секунды
    #     position=(50, 80),       # Позиция текста в процентах (50% по ширине, 80% по высоте)
    #     position_units='percent',
    #     font='Roboto-Bold',
    #     font_size=70,
    #     font_color='yellow',
    #     stroke_color='black',
    #     stroke_width=3,
    #     fade_duration=1          # Плавное появление и исчезновение в течение 1 секунды
    # )

    # # Создаем композицию
    # final_video = CompositeVideoClip([final_video, text_clip])

    if profile.resize and profile.resize != 1:
        print(f"CONVERTOR{part_str} :: Video resized with factor {profile.resize}")
        final_video = final_video.resize(profile.resize)

    if start > 0 or end < audio_duration:
        print(f"CONVERTOR{part_str} :: ❗❗❗ Video croped ✂️{start:3.0f}-{end:3.0f}✂️")
        final_video = final_video.subclip(start, end)

    # Сохраняем финальное видео
    final_video.write_videofile(output_file, fps=profile.fps, threads=1, \
        codec=profile.codec, preset=profile.preset, audio=is_audio) # ,bitrate=bitrate
    print(f"CONVERTOR{part_str} :: Video created: {output_file}")
