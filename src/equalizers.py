from moviepy.editor import *
import numpy as np
import cv2
import librosa

    # cv2.COLORMAP_AUTUMN
    # cv2.COLORMAP_BONE
    # cv2.COLORMAP_COOL
    # cv2.COLORMAP_HOT
    # cv2.COLORMAP_HSV
    # cv2.COLORMAP_JET
    # cv2.COLORMAP_OCEAN
    # cv2.COLORMAP_PINK
    # cv2.COLORMAP_RAINBOW
    # cv2.COLORMAP_SPRING
    # cv2.COLORMAP_SUMMER
    # cv2.COLORMAP_WINTER

def create_equalizer_clip(audio_file, duration, fps=24, size=(1280, 720),
                          colormap=cv2.COLORMAP_JET, equalizer_width_percent=10,
                          max_bar_height_percent=90, num_bars=60):
    # Загружаем аудио файл
    y, sr = librosa.load(audio_file, sr=None, mono=False)

    # Убедимся, что аудио стерео
    if y.ndim == 1:
        y = np.array([y, y])

    # Параметры для обработки аудио
    hop_length = int(sr / fps)
    n_fft = 4096  # Увеличиваем FFT для лучшего разрешения по частоте

    # Получаем спектрограммы для левого и правого каналов
    S_left = np.abs(librosa.stft(y[0], n_fft=n_fft, hop_length=hop_length))
    S_right = np.abs(librosa.stft(y[1], n_fft=n_fft, hop_length=hop_length))

    # Частотная шкала
    frequencies = librosa.fft_frequencies(sr=sr, n_fft=n_fft)

    # Определяем границы частот для каждого столбика (логарифмическая шкала)
    freq_bins = np.logspace(np.log10(frequencies[1]), np.log10(frequencies[-1]), num=num_bars+1)

    # Функция для агрегирования спектрограммы по частотным диапазонам
    def aggregate_spectrum(S, freq_bins):
        spectrum_bars = np.zeros((len(S[0]), num_bars))
        for i in range(num_bars):
            freq_mask = (frequencies >= freq_bins[i]) & (frequencies < freq_bins[i+1])
            if np.any(freq_mask):
                spectrum_bars[:, i] = S[freq_mask, :].mean(axis=0)
        return spectrum_bars

    # Агрегируем спектры по частотным диапазонам
    left_bars = aggregate_spectrum(S_left, freq_bins)
    right_bars = aggregate_spectrum(S_right, freq_bins)

    # Нормализуем амплитуды
    max_amp = max(left_bars.max(), right_bars.max())
    left_bars /= max_amp
    right_bars /= max_amp

    # Убеждаемся, что количество кадров соответствует длительности и fps
    num_frames = int(duration * fps)
    times = np.linspace(0, left_bars.shape[0]-1, num_frames).astype(int)
    left_bars = left_bars[times, :]
    right_bars = right_bars[times, :]

    # Вычисляем параметры один раз перед циклом
    equalizer_width = int(size[0] * (equalizer_width_percent / 100))  # Ширина каждого эквалайзера
    bar_width = equalizer_width // num_bars  # Ширина одного столбика

    # Максимальная высота столбика в пикселях
    max_bar_height = int(size[1] * (max_bar_height_percent / 100))

    # Начальные позиции для левого и правого эквалайзеров
    left_start_x = 0  # Левый эквалайзер прижат к левому краю
    right_start_x = size[0] - equalizer_width  # Правый эквалайзер прижат к правому краю

    def make_frame(t):
        # Создаем пустой кадр RGB
        frame = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        # Создаем маску (одноканальный кадр)
        mask = np.zeros((size[1], size[0]), dtype=np.uint8)

        frame_idx = int(t * fps)
        if frame_idx >= num_frames:
            frame_idx = num_frames - 1

        # Рисуем столбики для левого канала (низкие частоты по краям)
        for i in range(num_bars):
            amplitude = left_bars[frame_idx, num_bars - i - 1]  # Инвертируем индекс для частот
            bar_height = int(amplitude * max_bar_height)
            x = left_start_x + i * bar_width
            y = 0  # Начало от верхнего края
            color_intensity = int(amplitude * 255)
            color_bgr = cv2.applyColorMap(
                np.array([[color_intensity]], dtype=np.uint8), colormap)[0][0]
            color_rgb = (int(color_bgr[2]), int(color_bgr[1]), int(color_bgr[0]))  # Конвертация BGR в RGB
            # Рисуем столбик на кадре
            cv2.rectangle(frame, (x, y), (x + bar_width - 2, y + bar_height), color_rgb, -1)
            # Рисуем столбик на маске (белый цвет - непрозрачный)
            cv2.rectangle(mask, (x, y), (x + bar_width - 2, y + bar_height), 255, -1)

        # Рисуем столбики для правого канала (столбики идут от правого края к центру)
        for i in range(num_bars):
            amplitude = right_bars[frame_idx, i]
            bar_height = int(amplitude * max_bar_height)
            x = right_start_x + (num_bars - i - 1) * bar_width
            y = 0
            color_intensity = int(amplitude * 255)
            color_bgr = cv2.applyColorMap(
                np.array([[color_intensity]], dtype=np.uint8), colormap)[0][0]
            color_rgb = (int(color_bgr[2]), int(color_bgr[1]), int(color_bgr[0]))  # Конвертация BGR в RGB
            # Рисуем столбик на кадре
            cv2.rectangle(frame, (x, y), (x + bar_width - 2, y + bar_height), color_rgb, -1)
            # Рисуем столбик на маске
            cv2.rectangle(mask, (x, y), (x + bar_width - 2, y + bar_height), 255, -1)

        return frame, mask / 255.0  # Возвращаем кадр и маску (маска должна быть от 0 до 1)

    # Создаем VideoClip для кадра и маски
    def make_frame_rgb(t):
        frame, _ = make_frame(t)
        return frame

    def make_frame_mask(t):
        _, mask = make_frame(t)
        return mask

    # Создаем видео клип для кадра
    equalizer_clip = VideoClip(make_frame_rgb, duration=duration).set_fps(fps)
    # Создаем маску
    mask_clip = VideoClip(make_frame_mask, ismask=True, duration=duration).set_fps(fps)
    # Устанавливаем маску для клипа
    equalizer_clip = equalizer_clip.set_mask(mask_clip)

    return equalizer_clip

