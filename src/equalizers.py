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

import numpy as np
import cv2
import librosa
from moviepy.editor import VideoClip

def create_equalizer_clip(audio_file, duration, fps=24, size=(1280, 720),
                          colormap=cv2.COLORMAP_JET, circle_radius=100,
                          center_dot_size=15, edge_dot_size=5,
                          colormap_positions=[0.0, 0.33, 0.66, 1.0],
                          num_dots=10,
                          circle_vertical_position_percent=10,
                          amplitude_threshold=0.05,
                          frequency_bands=None,
                          debug_mode=False):
    if frequency_bands is None:
        frequency_bands = [
            {'band': (20, 150), 'amplification': 1.0},
            {'band': (150, 500), 'amplification': 1.0},
            {'band': (500, 2000), 'amplification': 1.0},
            {'band': (2000, 8000), 'amplification': 1.0},
        ]
    # Загружаем аудио файл
    y, sr = librosa.load(audio_file, sr=None, mono=False)

    # Убедимся, что аудио стерео
    if y.ndim == 1:
        y = np.array([y, y])

    # Параметры для обработки аудио
    hop_length = int(sr / fps)
    n_fft = 2048

    # Получаем спектрограммы для левого и правого каналов
    S_left = np.abs(librosa.stft(y[0], n_fft=n_fft, hop_length=hop_length))
    S_right = np.abs(librosa.stft(y[1], n_fft=n_fft, hop_length=hop_length))

    # Частотная шкала
    frequencies = librosa.fft_frequencies(sr=sr, n_fft=n_fft)

    # Функция для агрегирования спектрограммы по частотным диапазонам
    def aggregate_band_amplitude(S, band):
        freq_mask = (frequencies >= band[0]) & (frequencies < band[1])
        if np.any(freq_mask):
            return np.mean(S[freq_mask, :], axis=0)
        else:
            return np.zeros(S.shape[1])

    # Извлекаем амплитуды для каждого диапазона частот с учетом усиления
    band_amplitudes_left = []
    band_amplitudes_right = []
    for band_info in frequency_bands:
        band = band_info['band']
        amplification = band_info.get('amplification', 1.0)
        amp_left = aggregate_band_amplitude(S_left, band) * amplification
        amp_right = aggregate_band_amplitude(S_right, band) * amplification
        band_amplitudes_left.append(amp_left)
        band_amplitudes_right.append(amp_right)

    # Нормализуем амплитуды
    max_amp = max([band.max() for band in band_amplitudes_left + band_amplitudes_right])
    if max_amp == 0:
        max_amp = 1e-6  # Избегаем деления на ноль
    band_amplitudes_left = [band / max_amp for band in band_amplitudes_left]
    band_amplitudes_right = [band / max_amp for band in band_amplitudes_right]

    # Ограничиваем амплитуды в диапазоне [0, 1]
    band_amplitudes_left = [np.clip(band, 0, 1) for band in band_amplitudes_left]
    band_amplitudes_right = [np.clip(band, 0, 1) for band in band_amplitudes_right]

    # Убеждаемся, что количество кадров соответствует длительности и fps
    num_frames = int(duration * fps)
    interpolated_bands_left = [np.interp(np.linspace(0, len(band) - 1, num_frames),
                                         np.arange(len(band)), band)
                               for band in band_amplitudes_left]
    interpolated_bands_right = [np.interp(np.linspace(0, len(band) - 1, num_frames),
                                          np.arange(len(band)), band)
                                for band in band_amplitudes_right]

    # Вычисляем позиции точек внутри окружности
    def compute_dot_positions(center):
        positions = []
        for i in range(num_dots):
            for j in range(num_dots):
                # Нормализованные позиции между -1 и 1
                x_norm = -1 + 2 * i / (num_dots - 1)
                y_norm = -1 + 2 * j / (num_dots - 1)
                # Проверяем, что точка внутри окружности
                if x_norm**2 + y_norm**2 <= 1:
                    x = center[0] + x_norm * circle_radius
                    y = center[1] + y_norm * circle_radius
                    positions.append((int(x), int(y), x_norm, y_norm))
        return positions

    # Позиции окружностей
    vertical_pos = size[1] * (circle_vertical_position_percent / 100)

    left_center = (int(size[0] * 0.1), int(vertical_pos))   # Левый динамик
    right_center = (int(size[0] * 0.9), int(vertical_pos))  # Правый динамик

    left_positions = compute_dot_positions(left_center)
    right_positions = compute_dot_positions(right_center)

    # Генерируем цвета из колormap по заданным позициям
    colormap_colors = [cv2.applyColorMap(
        np.array([[int(pos * 255)]], dtype=np.uint8), colormap)[0][0]
        for pos in colormap_positions]
    # Конвертируем BGR в RGB
    colormap_colors = [(int(c[2]), int(c[1]), int(c[0])) for c in colormap_colors]

    # Для отладочной информации будем сохранять размеры точек
    debug_info = []

    def make_frame(t):
        # Получаем индекс текущего кадра
        frame_idx = int(t * fps)
        if frame_idx >= num_frames:
            frame_idx = num_frames - 1

        # Создаем пустой кадр
        frame = np.zeros((size[1], size[0], 3), dtype=np.uint8)

        # Функция для рисования точек
        def draw_dots(positions, band_amplitudes, channel_name):
            # Для отладочной информации
            frame_debug_info = []

            for x, y, x_norm, y_norm in positions:
                # Вычисляем базовый размер точки на основе позиции
                distance = np.sqrt(x_norm**2 + y_norm**2)
                dot_size = edge_dot_size + (center_dot_size - edge_dot_size) * (1 - distance)


                # Рисуем четыре мини-точки с разными цветами
                for idx, color in enumerate(colormap_colors):
                    amp = band_amplitudes[idx][frame_idx]  # Амплитуда из соответствующего диапазона частот
                    # Увеличиваем диапазон изменения размера точек
                    current_dot_size = dot_size * (0.0 + 4.0 * amp)  # Регулируем размер по амплитуде
                    current_dot_size = max(1, int(current_dot_size))

                    offset = (idx - 1.5) * current_dot_size / 3  # Позиционируем мини-точки вокруг основной точки
                    xi = int(x + offset)
                    yi = int(y + offset)
                    if 0 <= xi < size[0] and 0 <= yi < size[1]:
                        cv2.circle(frame, (xi, yi), current_dot_size // 2, color, -1)

                # Сохраняем информацию для отладки только для левого канала
                if channel_name == 'Left' and debug_mode:
                    frame_debug_info.append({
                        'position': (x, y),
                        'distance': distance,
                        'dot_size': dot_size,
                        'amplitudes': [band[frame_idx] for band in band_amplitudes],
                        'current_dot_size': current_dot_size // 2
                    })

            if channel_name == 'Left' and debug_mode:
                debug_info.append(frame_debug_info)

        # Если включен режим отладки, выводим информацию на кадр и через print
        if debug_mode:
            # Отображаем текстовую информацию на кадре
            debug_texts = []
            for idx, band_info in enumerate(frequency_bands):
                freq_range = f"{band_info['band'][0]:6.0f}-{band_info['band'][1]:6.0f} Hz"
                amplitude = interpolated_bands_left[idx][frame_idx]
                amplitude_percent = f"{amplitude * 100:6.0f}%"
                dot_size = 0
                if len(debug_info) > 0:
                    dot_size = debug_info[-1][0]['current_dot_size']
                debug_texts.append(f"Band {idx+1} ({freq_range}): {amplitude_percent} Size: {dot_size:2.0f}")
                print(f"Band {idx+1} ({freq_range}): {amplitude_percent} Size: {dot_size:2.0f}")

            # Позиция для вывода текста
            text_x = size[0] // 2 - 200
            text_y = int(vertical_pos)

            # Опции шрифта
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            color = (255, 255, 255)
            thickness = 2

            # Рисуем прямоугольник позади текста для контраста
            rect_width = 400
            rect_height = 30 * len(debug_texts)
            overlay = frame.copy()
            cv2.rectangle(overlay, (text_x - 10, text_y - 30),
                          (text_x + rect_width, text_y + rect_height),
                          (0, 0, 0), -1)
            alpha = 0.5  # Прозрачность
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

            # Отображаем текстовую информацию
            for i, text in enumerate(debug_texts):
                y_position = text_y + i * 30
                cv2.putText(frame, text, (text_x, y_position), font,
                            font_scale, color, thickness, cv2.LINE_AA)

            # Выводим отладочную информацию через print
            print(f"Frame {frame_idx}/{num_frames}:")
            for info in debug_texts:
                print(info)

        # Проверяем порог амплитуды
        if all(band[frame_idx] < amplitude_threshold for band in interpolated_bands_left):
            # Возвращаем пустой прозрачный кадр
            return frame


        # Рисуем точки для левого канала
        draw_dots(left_positions, interpolated_bands_left, 'Left')
        # Рисуем точки для правого канала (можно не рисовать, если интересует только левый)
        draw_dots(right_positions, interpolated_bands_right, 'Right')

        return frame

    # Создаем видео клип для кадра
    equalizer_clip = VideoClip(make_frame, duration=duration).set_fps(fps)

    return equalizer_clip



def create_equalizer_clip_bars_upper(audio_file, duration, fps=24, size=(1280, 720),
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

