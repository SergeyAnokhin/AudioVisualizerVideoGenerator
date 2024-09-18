from moviepy.editor import *
import os
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import librosa
import cv2

def create_equalizer_clip(audio_file, duration, fps=24, size=(1280, 720)):
    # Загружаем аудио файл
    y, sr = librosa.load(audio_file, sr=None, mono=False)

    # Убедимся, что аудио стерео
    if y.ndim == 1:
        y = np.array([y, y])

    # Параметры для обработки аудио
    hop_length = int(sr / fps)
    n_fft = 2048

    # Получаем амплитудные спектры для левого и правого каналов
    S_left = np.abs(librosa.stft(y[0], n_fft=n_fft, hop_length=hop_length))
    S_right = np.abs(librosa.stft(y[1], n_fft=n_fft, hop_length=hop_length))

    # Усредняем по частотам для получения амплитудных огибающих
    left_env = np.mean(S_left, axis=0)
    right_env = np.mean(S_right, axis=0)

    # Нормализуем амплитуды
    left_env /= np.max(left_env)
    right_env /= np.max(right_env)

    # Убеждаемся, что количество кадров соответствует длительности и fps
    num_frames = int(duration * fps)
    left_env = np.interp(np.linspace(0, len(left_env), num_frames), np.arange(len(left_env)), left_env)
    right_env = np.interp(np.linspace(0, len(right_env), num_frames), np.arange(len(right_env)), right_env)

    def make_frame(t):
        frame = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        frame[:] = (0, 0, 0)  # Черный фон

        frame_idx = int(t * fps)
        if frame_idx >= num_frames:
            frame_idx = num_frames - 1

        # Параметры для рисования
        center_left = (int(size[0]*0.25), int(size[1]*0.5))
        center_right = (int(size[0]*0.75), int(size[1]*0.5))
        radius = 50  # Радиус центрального круга
        num_bars = 30  # Количество столбиков вокруг круга
        max_bar_length = 100  # Максимальная длина столбика

        # Рисуем центральные круги
        cv2.circle(frame, center_left, radius, (255, 255, 255), thickness=-1)
        cv2.circle(frame, center_right, radius, (255, 255, 255), thickness=-1)

        # Углы для столбиков
        angles = np.linspace(0, 2*np.pi, num_bars, endpoint=False)

        # Столбики левого канала
        amplitude = left_env[frame_idx]
        for angle in angles:
            x1 = int(center_left[0] + radius * np.cos(angle))
            y1 = int(center_left[1] + radius * np.sin(angle))
            bar_length = int(amplitude * max_bar_length)
            x2 = int(center_left[0] + (radius + bar_length) * np.cos(angle))
            y2 = int(center_left[1] + (radius + bar_length) * np.sin(angle))
            color = (0, 255, 0)  # Зеленый цвет для левого канала
            cv2.line(frame, (x1, y1), (x2, y2), color, thickness=4)

        # Столбики правого канала
        amplitude = right_env[frame_idx]
        for angle in angles:
            x1 = int(center_right[0] + radius * np.cos(angle))
            y1 = int(center_right[1] + radius * np.sin(angle))
            bar_length = int(amplitude * max_bar_length)
            x2 = int(center_right[0] + (radius + bar_length) * np.cos(angle))
            y2 = int(center_right[1] + (radius + bar_length) * np.sin(angle))
            color = (0, 0, 255)  # Красный цвет для правого канала
            cv2.line(frame, (x1, y1), (x2, y2), color, thickness=4)

        return frame

    equalizer_clip = VideoClip(make_frame, duration=duration).set_fps(fps)
    return equalizer_clip



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
    equalizer_clip = create_equalizer_clip(audio_file, duration=audio_duration, size=final_video.size)
    equalizer_clip = equalizer_clip.set_opacity(0.99)  # Опционально: установить прозрачность

    # Накладываем эквалайзер поверх финального видео
    print("➕Add equalizer visualization")
    final_video = CompositeVideoClip([final_video, equalizer_clip])

    # Сохраняем финальное видео
    output_file = f"{folder}_output_video.mp4"
    final_video.write_videofile(output_file, fps=12, threads=os.cpu_count())
    print(f"Video created: {output_file}")


def process_folders(base_folder, num_workers=1):
    # Поиск всех папок, начинающихся с "Clip"
    folders = [os.path.join(base_folder, folder) \
               for folder in sorted(os.listdir(base_folder)) \
               if folder.startswith("Clip") and len(folder) == 5]

    print('Folders found: ', folders)

    # Путь к GIF-файлу (если есть)
    gif_file = base_folder + "static/animated2.gif"  # Вы можете указать путь к вашему GIF-файлу

    # Используем параллельную обработку
    # with ProcessPoolExecutor(max_workers=num_workers) as executor:
    #     executor.map(create_video_from_folder, folders, [gif_file]*len(folders))
    create_video_from_folder(folders[0], gif_file)


# Основной запуск
if __name__ == "__main__":

    # Установить переменную окружения динамически на основе количества доступных ядер
    print("Use all CPU cores: ", os.cpu_count())
    os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())

    base_folder = "../"  # Укажите путь к основной папке, содержащей папки Clip
    num_workers = 1  # Количество параллельных процессов

    process_folders(base_folder, num_workers)