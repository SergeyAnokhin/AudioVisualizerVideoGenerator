from moviepy.editor import *
import numpy as np
import librosa
import cv2

import numpy as np
import cv2
import librosa
from moviepy.editor import VideoClip

def create_equalizer_clip(audio_file, duration, fps=24, size=(1280, 720),
                          colormap=cv2.COLORMAP_JET, equalizer_width_percent=20,
                          num_bars=60):
    
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

    # Определяем количество столбиков (можете настроить)
    # num_bars = 60

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

    def make_frame(t):
        # Создаем пустой кадр
        frame = np.zeros((size[1], size[0], 3), dtype=np.uint8)

        frame_idx = int(t * fps)
        if frame_idx >= num_frames:
            frame_idx = num_frames - 1

        # Параметры для рисования
        equalizer_width = int(size[0] * (equalizer_width_percent / 100))  # Ширина каждого эквалайзера
        bar_width = equalizer_width // num_bars  # Ширина одного столбика
        max_bar_height = int(size[1] * 0.3)  # 0.9 Максимальная высота столбика

        # Начальные позиции для левого и правого эквалайзера
        left_start_x = int(size[0] * 0.1 - equalizer_width / 2) # 0.25
        right_start_x = int(size[0] * 0.90 - equalizer_width / 2) # 0.75

        # Рисуем столбики для левого канала (низкие частоты по краям)
        for i in range(num_bars):
            amplitude = left_bars[frame_idx, num_bars - i - 1]  # Инвертируем индекс для частот
            bar_height = int(amplitude * max_bar_height)
            x = left_start_x + i * bar_width
            y = 0  # Начало от верхнего края
            color_intensity = int(amplitude * 255)
            color = tuple(map(int, cv2.applyColorMap(
                np.array([[color_intensity]], dtype=np.uint8), colormap)[0][0]))
            cv2.rectangle(frame, (x, y), (x + bar_width - 2, y + bar_height), color, -1)

        # Рисуем столбики для правого канала
        for i in range(num_bars):
            amplitude = right_bars[frame_idx, i]
            bar_height = int(amplitude * max_bar_height)
            x = right_start_x + i * bar_width
            y = 0
            color_intensity = int(amplitude * 255)
            color = tuple(map(int, cv2.applyColorMap(
                np.array([[color_intensity]], dtype=np.uint8), colormap)[0][0]))
            cv2.rectangle(frame, (x, y), (x + bar_width - 2, y + bar_height), color, -1)

        return frame

    equalizer_clip = VideoClip(make_frame, duration=duration).set_fps(fps)
    return equalizer_clip



def equalizer_two_circle(audio_file, duration, fps=24, size=(1280, 720)):
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


