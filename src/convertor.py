from moviepy.editor import *
import os
import cv2
import equalizers
from PIL import Image

def create_video_from_folder(folder, gif_file=None):
    print("Start creating from: 📂", folder)

    # Путь к аудио-файлу
    audio_file = os.path.join(folder, "music.mp3")

    # Проверяем, существует ли аудио-файл
    if not os.path.isfile(audio_file):
        print(f"❌Audio file not found in {folder}")
        return

    # Список изображений в папке
    images = [os.path.join(folder, img) for img in sorted(os.listdir(folder)) if img.endswith(('.png', '.jpg', '.jpeg'))]

    # Длительность аудио-файла
    audio = AudioFileClip(audio_file)
    audio_duration = audio.duration

    # Длительность каждого изображения (в секундах)
    image_duration = 10  # Измените на желаемую длительность

    # Создаем список клипов из изображений
    image_clips = [] 
    for img in images:
        clip = ImageClip(img).set_duration(image_duration)
        print("Load image: 🖼", img)
        image_clips.append(clip)

    # Если нет изображений, используем черный фон
    if not image_clips:
        image_clips = [ColorClip(size=(1280, 720), color=(0, 0, 0)).set_duration(image_duration)]

    # Объединяем клипы в одно слайд-шоу
    slideshow = concatenate_videoclips(image_clips, method="compose")

    # Зацикливаем слайд-шоу на всю длительность аудио
    slideshow = slideshow.loop(duration=audio_duration)

    inspect_clip("slideshow", slideshow)

    # Проверяем наличие GIF-файла и накладываем его на видео
    if gif_file and os.path.isfile(gif_file):
        print("✔Gif file found")

        has_mask = False # has_transparency(gif_file)
        # Загружаем GIF и зацикливаем на всю длительность аудио
        gif_clip = (VideoFileClip(gif_file, has_mask)
                    .loop(duration=audio_duration)
                    # .resize(0.5)  # Масштабирование (0.5 = 50% от исходного размера)
                    .set_position(("left", "bottom")))  # Позиция (можно изменить на нужную)

        # Делаем фон GIF прозрачным (удаляем определенный цвет)
        gif_clip = gif_clip.fx(vfx.mask_color, color=[0, 0, 0], thr=100, s=5)

        inspect_clip("gif_clip", gif_clip)

        # Накладываем GIF поверх слайд-шоу
        final_video = CompositeVideoClip([slideshow, gif_clip])
    else:
        final_video = slideshow

    # Добавляем аудио к видео
    final_video = final_video.set_audio(audio)

    # Создаем эквалайзерный клип
    print("⏩Create equalizer visualization")
    equalizer_clip = equalizers.create_equalizer_clip(audio_file, duration=audio_duration, 
                        size=final_video.size, colormap=cv2.COLORMAP_AUTUMN,
                        equalizer_width_percent=30, max_bar_height_percent=30)
    equalizer_clip = equalizer_clip.set_opacity(0.2)  # Опционально: установить прозрачность

    inspect_clip("final_video", final_video)
    inspect_clip("equalizer_clip", equalizer_clip)


    # Накладываем эквалайзер поверх финального видео
    print("➕Add equalizer visualization")
    final_video = CompositeVideoClip([final_video, equalizer_clip])

    # fastest for tests:
    is_test = True
    if is_test:
        print("Mode: 🧪Test")
        final_video = final_video.resize(0.5)
        # final_video = final_video.subclip(10, 30) # Start at 0 seconds and end at 10 seconds
        fps = 6
        preset = 'ultrafast' # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo
        codec = 'libx264' # libx264, libx265, mpeg4, vp8, vp9, prores, mjpeg, rawvideo, libvpx, libvpx-vp9, libtheora
        bitrate='100k' # 500k, 1M
    else:
        print("Mode: 👍Final")
        fps = 24
        preset = 'medium' # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo
        codec= 'libx265' # libx264, libx265, mpeg4, vp8, vp9, prores, mjpeg, rawvideo, libvpx, libvpx-vp9, libtheora
        bitrate=None

    # print("❗❗❗Cut the last 5 seconds WARNING !!! Remove after use ❗❗❗")
    # final_video = final_video.subclip(0, video.duration - 5)  # Start at 0 seconds and end 5 seconds before the end


    # Сохраняем финальное видео
    output_file = f"{folder}_output_video.mp4"
    final_video.write_videofile(output_file, fps=fps, threads=os.cpu_count(), codec=codec, preset=preset) # ,bitrate=bitrate
    print(f"Video created: {output_file}")







def inspect_clip(name, clip, debug=False):
    if not debug:
        return
    
    # Get the size (resolution) of the clip
    print(f"===== Inspect clip: {name} ========")
    size = clip.size
    print(f"Size (width, height): {size}")
    
    # Get the duration of the clip
    duration = clip.duration
    print(f"Duration: {duration} seconds")
    
    # Check if the clip has an alpha mask (transparency)
    has_transparency = clip.mask is not None
    print(f"Has transparency (alpha channel): {has_transparency}")
    
    # Get the number of color channels by inspecting a frame
    frame = clip.get_frame(0)  # Get the first frame of the clip
    num_channels = frame.shape[2] if len(frame.shape) == 3 else 1  # Check if the frame has color channels
    print(f"Number of color channels: {num_channels} (ℹ: 3 for RGB, 4 for RGBA)")
    
    # Print if the clip has transparency based on number of channels
    if num_channels == 4:
        print("This clip is RGBA (has transparency).")
    else:
        print("This clip is RGB (no transparency).")
    print("==============================")

# Example usage with a clip:
# Assuming you have a clip object
# inspect_clip(clip)


def has_transparency(gif_path):
    img = Image.open(gif_path)
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        return True
    return False