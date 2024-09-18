from moviepy.editor import *
import os
import equalizers

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
    image_duration = 2  # Измените на желаемую длительность

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

    # # Проверяем наличие GIF-файла и накладываем его на видео
    # if gif_file and os.path.isfile(gif_file):
    #     print("✔Gif file found")
    #     # Загружаем GIF и зацикливаем на всю длительность аудио
    #     gif_clip = (VideoFileClip(gif_file, has_mask=True)
    #                 .loop(duration=audio_duration)
    #                 # .resize(0.5)  # Масштабирование (0.5 = 50% от исходного размера)
    #                 .set_position(("left", "bottom")))  # Позиция (можно изменить на нужную)

    #     # Делаем фон GIF прозрачным (удаляем определенный цвет)
    #     gif_clip = gif_clip.fx(vfx.mask_color, color=[0, 0, 0], thr=100, s=5)

    #     # Накладываем GIF поверх слайд-шоу
    #     final_video = CompositeVideoClip([slideshow, gif_clip])
    # else:
    final_video = slideshow

    # Добавляем аудио к видео
    final_video = final_video.set_audio(audio)

    # Создаем эквалайзерный клип
    print("⏩Create equalizer visualization")
    equalizer_clip = equalizers.create_equalizer_clip(audio_file, duration=audio_duration, size=final_video.size)
    equalizer_clip = equalizer_clip.set_opacity(0.2)  # Опционально: установить прозрачность

    # Накладываем эквалайзер поверх финального видео
    print("➕Add equalizer visualization")
    final_video = CompositeVideoClip([final_video, equalizer_clip])

    # Сохраняем финальное видео
    output_file = f"{folder}_output_video.mp4"
    final_video.write_videofile(output_file, fps=6, threads=os.cpu_count())
    print(f"Video created: {output_file}")
