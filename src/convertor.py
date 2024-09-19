from moviepy.editor import *
import os
import cv2
import equalizers
import tools

def create_video_from_folder(folder, gif_file=None, part=None, num_cores=1):
    print(f"Start creating from: 📂{folder} Part # -{part}-", )

    # Путь к аудио-файлу
    audio_file = [os.path.join(folder, music) \
                    for music in os.listdir(folder) if music.endswith(('.mp3'))][0] # os.path.join(folder, "music.mp3")

    # Проверяем, существует ли аудио-файл
    if not os.path.isfile(audio_file):
        print(f"❌Audio file not found in {folder}")
        return

    # Список изображений в папке
    images = [os.path.join(folder, img) for img in sorted(os.listdir(folder)) if img.endswith(('.png', '.jpg', '.jpeg', '.jfif'))]

    # Длительность аудио-файла
    audio = AudioFileClip(audio_file)
    audio_duration = audio.duration
    print(f"CONVERTOR :: 🎶Audio ⌛duration: {audio_duration} secs")
    
    tools.suggest_frequency_bands(audio_file)
    
    start, end = tools.get_segment_duration(audio_duration, part, num_cores)
    print(f"PART {part}: ⏱ [{start:.0f}...{end:.0f}] secs")

    # Длительность каждого изображения (в секундах)
    image_duration = 20  # Измените на желаемую длительность
    
    # Создаем слайд-шоу с повторением и затемнением
    print("⏩Create looping slideshow with fade transition")
    slideshow = tools.create_slideshow_with_fade(images, audio_duration=audio_duration, 
                                           image_duration=image_duration, fade_duration=0.1)

    # Проверяем наличие GIF-файла и накладываем его на видео
    final_video = tools.add_gif(gif_file, audio_duration, slideshow)

    # Добавляем аудио к видео
    final_video = final_video.set_audio(audio)

    # Создаем эквалайзерный клип
    print("⏩Create equalizer visualization")
    # Настройка диапазонов частот для каждой из четырех суб-точек с усилением
    frequency_bands = [
        {'band': (20, 100), 'amplification': 2.0},
        {'band': (100, 300), 'amplification': 4.0},
        {'band': (300, 500), 'amplification': 3.0},
        {'band': (500, 8000), 'amplification': 40.0},
    ]
    # equalizer_clip = equalizers.create_equalizer_clip_bars_upper(audio_file, duration=audio_duration, 
    #                     size=final_video.size, colormap=cv2.COLORMAP_AUTUMN,
    #                     equalizer_width_percent=30, max_bar_height_percent=30)
    equalizer_clip = equalizers.create_equalizer_clip(audio_file, duration=audio_duration,
                        size=final_video.size, 
                        colormap=cv2.COLORMAP_JET, circle_radius=400,
                          center_dot_size=35, edge_dot_size=5,
                          colormap_positions=[0.0, 0.33, 0.66, 1.0],
                          num_dots=30,
                          circle_vertical_position_percent=7,
                          amplitude_threshold=0.5,
                          debug_mode=False,
                          frequency_bands=frequency_bands)

    
    equalizer_clip = equalizer_clip.set_opacity(0.2)  # Опционально: установить прозрачность

    # Накладываем эквалайзер поверх финального видео
    print("➕Add equalizer visualization")
    final_video = CompositeVideoClip([final_video, equalizer_clip])

    # fastest for tests:
    mode = 'test'
    
    if mode == 'test':
        print("Mode: 🧪Test")
        final_video = final_video.resize(0.5)
        if num_cores > 1:
            final_video = final_video.subclip(start, end)
        elif audio_duration > 35:
            final_video = final_video.subclip(25, 45) # Start at 0 seconds and end at 10 seconds
        fps = 6 # 6, 24, 60
        preset = 'ultrafast' # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo
        codec = 'libx264' # libx264, libx265, mpeg4, vp8, vp9, prores, mjpeg, rawvideo, libvpx, libvpx-vp9, libtheora
    elif mode == 'quality_test':
        print("Mode: 🧪👍 Quality Test")
        # final_video = final_video.resize(0.5)
        if num_cores > 1:
            final_video = final_video.subclip(start, end)
        elif audio_duration > 35:
            final_video = final_video.subclip(25, 45) # Start at 0 seconds and end at 10 seconds
        fps = 60
        preset = 'faster' # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo
        codec = 'libx264' # libx264, libx265, mpeg4, vp8, vp9, prores, mjpeg, rawvideo, libvpx, libvpx-vp9, libtheora
    elif mode == 'final_fast':
        print("Mode: 👍Final fast 🏃💨")
        if num_cores > 1:
            final_video = final_video.subclip(start, end)
        fps = 60 # 6, 24, 60
        preset = 'faster' # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo
        codec = 'libx264' # libx264, libx265, mpeg4, vp8, vp9, prores, mjpeg, rawvideo, libvpx, libvpx-vp9, libtheora
    else:
        if num_cores > 1:
            final_video = final_video.subclip(start, end)
        print("Mode: 👍Final")
        fps = 24 # 24, 60
        preset = 'medium' # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo
        codec= 'libx264' # libx264, libx265, mpeg4, vp8, vp9, prores, mjpeg, rawvideo, libvpx, libvpx-vp9, libtheora
        bitrate=None

    # print("❗❗❗Cut the last 5 seconds WARNING !!! Remove after use ❗❗❗")
    # final_video = final_video.subclip(0, video.duration - 5)  # Start at 0 seconds and end 5 seconds before the end


    # Сохраняем финальное видео
    output_file = f"{folder}_output_video_{part}_{start:.0f}-{end:.0f}.mp4"
    final_video.write_videofile(output_file, fps=fps, threads=os.cpu_count(), codec=codec, preset=preset) # ,bitrate=bitrate
    print(f"Video created: {output_file}")

