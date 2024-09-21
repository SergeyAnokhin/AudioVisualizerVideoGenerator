from console_tools import ice, prefix_color
from model import Profile
import numpy as np
import librosa
from moviepy.editor import *
import os
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import TextClip, VideoClip
from moviepy.video.fx.all import fadein, fadeout
from moviepy.editor import ImageClip, concatenate_videoclips


def create_text_image(text, font_size, color, bg_color, size):
    # img = create_text_image("Your Text Here", 50, "white", "black", (800, 600))
    # img.save("text_image.png")
    # clip = ImageClip("text_image.png").set_duration(5)

    img = Image.new("RGB", size, bg_color)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", font_size)
    w, h = draw.textsize(text, font=font)
    draw.text(((size[0] - w) / 2, (size[1] - h) / 2), text, fill=color, font=font)
    return img


def create_text_clip(
    text,
    duration,
    start_time=0,
    end_time=None,
    position=(50, 50),
    position_units="percent",
    font="Arial",
    font_size=50,
    font_color="white",
    stroke_color="black",
    stroke_width=2,
    fade_duration=0.5,
    video_size=(1280, 720),
):
    """
    Создает видеоклип с текстом на прозрачном фоне.

    Параметры:
    - text (str): Текст для отображения.
    - duration (float): Длительность клипа в секундах.
    - start_time (float): Время начала отображения текста в секундах.
    - end_time (float): Время окончания отображения текста в секундах. Если None, используется start_time + duration.
    - position (tuple): Позиция текста (x, y). Значения в процентах или пикселях, в зависимости от position_units.
    - position_units (str): Единицы измерения позиции ('percent' или 'pixels').
    - font (str): Название шрифта.
    - font_size (int): Размер шрифта.
    - font_color (str или tuple): Цвет шрифта.
    - stroke_color (str или tuple): Цвет обводки текста.
    - stroke_width (int): Толщина обводки текста.
    - fade_duration (float): Длительность эффектов появления и исчезновения в секундах.
    - video_size (tuple): Размер видео (width, height) для расчета позиции в пикселях.

    Возвращает:
    - text_clip (VideoClip): Клип с текстом и прозрачным фоном.
    """
    if end_time is None:
        end_time = start_time + duration

    # Создаем текстовый клип
    text_clip = TextClip(
        text,
        fontsize=font_size,
        font=font,
        color=font_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
        method="caption",
        size=None,
    )

    # Устанавливаем длительность
    text_clip = text_clip.set_duration(end_time - start_time)

    # Применяем эффекты появления и исчезновения
    if fade_duration > 0:
        text_clip = text_clip.fx(fadein, fade_duration).fx(fadeout, fade_duration)

    # Преобразуем позицию из процентов в пиксели, если необходимо
    if position_units == "percent":
        x = int(position[0] * video_size[0] / 100)
        y = int(position[1] * video_size[1] / 100)
        pos = (x, y)
    else:
        pos = position

    text_clip = text_clip.set_position(pos)

    # Устанавливаем время начала отображения
    text_clip = text_clip.set_start(start_time)

    return text_clip


def create_text_clip_pil(
    text,
    duration,
    start_time=0,
    end_time=None,
    position=(50, 50),
    position_units="percent",
    font="Arial",
    font_size=50,
    font_color="white",
    stroke_color="black",
    stroke_width=2,
    fade_duration=0.5,
    video_size=(1280, 720),
):
    """
    Создает видеоклип с текстом на прозрачном фоне, используя PIL.

    Параметры:
    - те же, что и у функции create_text_clip.

    Возвращает:
    - text_clip (VideoClip): Клип с текстом и прозрачным фоном.
    """
    if end_time is None:
        end_time = start_time + duration

    # Размер видео
    width, height = video_size

    # Загружаем шрифт
    try:
        font_obj = ImageFont.truetype(font, font_size)
    except IOError:
        font_obj = ImageFont.load_default()

    # Создаем функцию для генерации кадров
    def make_frame(t):
        # Создаем прозрачное изображение
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Измеряем размер текста
        text_size = draw.textsize(text, font=font_obj, stroke_width=stroke_width)

        # Преобразуем позицию из процентов в пиксели, если необходимо
        if position_units == "percent":
            x = int(position[0] * width / 100)
            y = int(position[1] * height / 100)
        else:
            x, y = position

        # Центрируем текст относительно заданной позиции
        text_x = x - text_size[0] // 2
        text_y = y - text_size[1] // 2

        # Рисуем текст с обводкой
        draw.text(
            (text_x, text_y),
            text,
            font=font_obj,
            fill=font_color,
            stroke_width=stroke_width,
            stroke_fill=stroke_color,
        )

        # Преобразуем изображение в массив numpy
        frame = np.array(img)

        return frame

    # Создаем видео клип
    text_clip = VideoClip(make_frame, duration=end_time - start_time)

    # Применяем эффекты появления и исчезновения
    if fade_duration > 0:
        text_clip = text_clip.fx(fadein, fade_duration).fx(fadeout, fade_duration)

    # Устанавливаем время начала отображения
    text_clip = text_clip.set_start(start_time)

    return text_clip


# Папка со шрифтами в Windows
FONTS_FOLDERS = ["C:\\Windows\\Fonts"]  # Можно добавить другие папки по необходимости


# python -c "import tools; tools.find_fonts('Arial')"
def find_fonts(keyword=None):
    found_fonts = []

    # Перебираем все папки со шрифтами
    for folder in FONTS_FOLDERS:
        # Перебираем все файлы в папке
        for font_file in os.listdir(folder):
            # Проверяем, является ли файл шрифтом
            if font_file.endswith((".ttf", ".otf")):
                # Если передано ключевое слово, проверяем, содержится ли оно в названии файла
                if keyword is None or keyword.lower() in font_file.lower():
                    font_path = os.path.join(folder, font_file)
                    # Сохраняем информацию о шрифте и доступности для библиотек
                    font_info = {
                        "font_file": font_file,
                        "font_path": font_path,
                        "usable_in_moviepy": True,  # Для MoviePy используем просто название
                        "usable_in_pil": True,  # Для PIL нужен полный путь
                    }
                    found_fonts.append(font_info)

    # Выводим результаты
    if found_fonts:
        for font in found_fonts:
            print(f"Найден шрифт: {font['font_file']}")
            print(f"Полный путь: {font['font_path']}")
            print(
                f"Может использоваться с MoviePy: {'Да' if font['usable_in_moviepy'] else 'Нет'}"
            )
            print(
                f"Может использоваться с PIL: {'Да' if font['usable_in_pil'] else 'Нет'}"
            )
            print("-" * 40)
    else:
        print("Шрифты не найдены.")


def get_audio_file(folder):
    # Путь к аудио-файлу
    audio_file = [
        os.path.join(folder, music)
        for music in os.listdir(folder)
        if music.endswith((".mp3"))
    ][
        0
    ]  # os.path.join(folder, "music.mp3")

    # Проверяем, существует ли аудио-файл
    if not os.path.isfile(audio_file):
        print(f"❌Audio file not found in {folder}")
        return

    return audio_file


def get_directory_from_path(file_path):
    # Получаем только путь к директории
    directory_path = os.path.dirname(file_path)
    return directory_path


def get_filename_without_extension(file_path):
    # Получаем только имя файла с расширением
    file_name_with_extension = os.path.basename(file_path)
    # Убираем расширение
    file_name_without_extension = os.path.splitext(file_name_with_extension)[0]
    return file_name_without_extension


def suggest_frequency_bands(
    audio_file, num_bands=4, sr=None, n_fft=2048, hop_length=None
):
    # Загружаем аудио файл
    y, sr = librosa.load(audio_file, sr=sr, mono=True)

    if hop_length is None:
        hop_length = n_fft // 4

    # Вычисляем спектрограмму
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))

    # Получаем частотные значения
    frequencies = librosa.fft_frequencies(sr=sr, n_fft=n_fft)

    # Вычисляем изменение амплитуды по времени для каждой частоты (спектральный флюкс)
    spectral_flux = np.var(S, axis=1)

    # Разбиваем частотный спектр на равные интервалы
    num_freqs = len(frequencies)
    freq_bins = np.linspace(frequencies[0], frequencies[-1], num=500)

    # Суммируем спектральный флюкс в каждом частотном диапазоне
    flux_per_band = []
    for i in range(len(freq_bins) - 1):
        freq_mask = (frequencies >= freq_bins[i]) & (frequencies < freq_bins[i + 1])
        if np.any(freq_mask):
            flux = np.sum(spectral_flux[freq_mask])
            flux_per_band.append((flux, freq_bins[i], freq_bins[i + 1]))

    # Сортируем диапазоны по величине спектрального флюкса (изменчивости)
    flux_per_band.sort(reverse=True, key=lambda x: x[0])

    # Выбираем топ `num_bands` диапазонов
    top_bands = flux_per_band[:num_bands]

    # Сортируем выбранные диапазоны по возрастанию частоты
    top_bands.sort(key=lambda x: x[1])

    # Формируем список диапазонов
    suggested_bands = [(round(band[1]), round(band[2])) for band in top_bands]

    print("Предлагаемые частотные диапазоны:")
    for idx, band in enumerate(suggested_bands):
        print(f"Диапазон {idx+1}: {band[0]} - {band[1]} Гц")

    return suggested_bands


@prefix_color("MERGE", "bright_black")
def merge_videos_with_audio(
    video_files, audio_file, output_file, profile: Profile, threads=4
):
    """
    Объединяет список видеофайлов и добавляет к ним аудио, затем сохраняет результат в выходной файл.

    :param video_files: Список путей к видеофайлам (без аудио).
    :param audio_file: Путь к аудиофайлу (MP3).
    :param output_file: Путь к выходному видеофайлу.
    """
    ice(f"🚀 Начинается процесс объединения {len(video_files)} видеофайлов.")

    # Загружаем видеофайлы
    clips = []
    for idx, file in enumerate(video_files):
        ice(f"📂 Загрузка видеофайла {idx + 1}/{len(video_files)}: {file}")
        clip = VideoFileClip(file)
        clips.append(clip)

    ice("✅ Все видеофайлы успешно загружены.")

    # Объединяем видеофайлы
    ice("🔗 Объединение видеофайлов...")
    final_clip = concatenate_videoclips(clips, method="compose")
    ice("🎬 Видео успешно объединено.")

    # Загружаем аудио файл
    ice(f"🎵 Загрузка аудиофайла: {audio_file}")
    audio = AudioFileClip(audio_file)
    ice("✅ Аудиофайл успешно загружен.")

    # Добавляем аудио к финальному видео
    ice("🎶 Добавление аудио к объединенному видео...")
    final_clip = final_clip.set_audio(audio)
    ice("✅ Аудио успешно добавлено к видео.")

    # Сохраняем итоговый файл
    ice(f"💾 Сохранение итогового файла: {output_file}")
    final_clip.write_videofile(
        output_file, codec=profile.codec, preset=profile.preset, threads=threads
    )
    ice(f"🎉 Файл успешно сохранен: {output_file}")

    # Удаление временных файлов
    for file in video_files:
        if os.path.exists(file):
            os.remove(file)
            ice(f"Удалён временный файл: {file}")


def merge_videos(output_file, video_files):

    # folder = 'path/to/your/videos'
    # video_files = sorted([os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.mp4')])

    # # Output file path
    # output_file = os.path.join(folder, "merged_output_video.mp4")

    # Load all video clips
    clips = [VideoFileClip(file) for file in video_files]

    # Concatenate all clips into one
    final_clip = concatenate_videoclips(clips, method="compose")

    # Write the result to a file
    final_clip.write_videofile(output_file, codec="libx264", threads=4)


def get_segment_duration(total_duration, segment_number, total_segments):
    # Вычисляем длительность одного сегмента
    segment_length = total_duration // total_segments

    # Определяем начало и конец сегмента
    start_time = segment_number * segment_length
    end_time = start_time + segment_length

    # Если это последний сегмент, корректируем конечное время
    if segment_number == total_segments + 1:
        end_time = total_duration - 1

    return start_time, end_time

@prefix_color("GIF_ADD", "black")
def add_gif(gif_file, audio_duration, slideshow, resize=1):
    if gif_file and os.path.isfile(gif_file):
        ice("GIF: ✔Gif file found")

        has_mask = False  # has_transparency(gif_file)
        # Загружаем GIF и зацикливаем на всю длительность аудио
        gif_clip = (
            VideoFileClip(gif_file, has_mask)
            .loop(duration=(14.0 * 2.0))  # two times # duration=audio_duration)
            .resize(resize * 0.5)  # Масштабирование (0.5 = 50% от исходного размера)
            .set_position(("left", "bottom"))
        )  # Позиция (можно изменить на нужную)

        # Делаем фон GIF прозрачным (удаляем определенный цвет)
        gif_clip = gif_clip.fx(vfx.mask_color, color=[0, 0, 0], thr=100, s=5)

        inspect_clip("gif_clip", gif_clip)

        # Накладываем GIF поверх слайд-шоу
        final_video = CompositeVideoClip([slideshow, gif_clip])
    else:
        final_video = slideshow
    return final_video


def create_slideshow_with_fade_OLD(
    images, audio_duration, image_duration=2, fade_duration=0.1
):
    image_clips = []

    # Create individual image clips with fade in and fade out
    for img in images:
        clip = ImageClip(img).set_duration(image_duration)
        # Apply fade in and fade out effect
        clip = clip.crossfadein(fade_duration).crossfadeout(fade_duration)
        image_clips.append(clip)

    # Concatenate images to form a slideshow
    slideshow = concatenate_videoclips(image_clips, method="compose")

    # Loop the slideshow to match the audio duration
    print(f"SLIDES🖼 :: 🔁Looping at ⌛duration: {audio_duration}")
    looped_slideshow = slideshow.loop(duration=audio_duration)

    return looped_slideshow


@prefix_color("SLIDES🖼", "bright_green")
def create_slideshow_with_fade(
    imageClips: list, audio_duration, image_duration=2, fade_duration=0.1
):
    image_clips = []

    ice(
        f"Total images: {len(imageClips)} :: 🔁Looping at ⌛duration: {audio_duration:3.0f} secs"
    )
    # Создаем клипы для каждого изображения с эффектами затемнения и появления
    for img in imageClips:
        clip = img.set_duration(image_duration)
        # Применяем эффекты плавного появления и исчезновения
        clip = clip.fadein(fade_duration).fadeout(fade_duration)
        image_clips.append(clip)

    # Конкатенируем изображения в слайдшоу
    slideshow = concatenate_videoclips(image_clips, method="compose")

    # Вычисляем длительность одного слайдшоу
    slideshow_duration = slideshow.duration

    # Вычисляем, сколько раз нужно повторить слайдшоу
    num_repeats = int(audio_duration // slideshow_duration) + 1

    # Размножаем массив клипов
    replicated_clips = image_clips * num_repeats
    ice(
        f"Replicated images: {len(replicated_clips)} :: 🔁Repeated: {num_repeats} times"
    )

    # Конкатенируем размноженные клипы в финальное слайдшоу
    full_slideshow = concatenate_videoclips(replicated_clips, method="compose")

    # Обрезаем слайдшоу, чтобы оно соответствовало длительности аудио
    final_slideshow = full_slideshow.subclip(0, audio_duration)

    return final_slideshow

def resize_is_needed(clip, target_height):
    if target_height != clip.size[1]:
        clip_resized = clip.resize(height=target_height)
        ice(f"↔️↕️Resized : w{clip.size[0]} x h{clip.size[1]} => w{standard_width} x h{standard_height}")
    else:
        clip_resized = clip
    return clip_resized
    

@prefix_color("IMAGE_ADJUST", "blue")
def adjust_image_clips(image_clips, target_height, mode="crop"):
    """
    Adjusts a list of ImageClips to have the same size.

    Parameters:
    - image_clips (list of ImageClip): List of images to process.
    - target_height (int): The target vertical size (height) in pixels.
    - mode (str): Determines how to handle images with differing aspect ratios.
        - 'crop': Crop the images to fit the standard width.
        - 'pad': Pad the images with black bars to fit the standard width.

    Returns:
    - adjusted_clips (list of ImageClip): List of adjusted ImageClips with the same size.
    """
    adjusted_clips = []

    if not image_clips:
        return adjusted_clips  # Return empty list if input is empty

    # Adjust the first image to determine the standard width
    first_clip = image_clips[0]
    first_clip_resized = resize_is_needed(first_clip, target_height)
    standard_width, standard_height = first_clip_resized.size

    # # Process the first clip
    # if mode == 'crop':
    #     # Crop the first clip if necessary (though width should already match standard_width)
    #     first_clip_final = first_clip_resized.crop(width=standard_width, height=target_height)
    # elif mode == 'pad':
    #     # Pad the first clip if necessary (should not be needed for first clip)
    #     first_clip_final = first_clip_resized.on_color(size=(standard_width, target_height),
    #                                                    color=(0, 0, 0),
    #                                                    col_opacity=1)
    # else:
    #     raise ValueError("Invalid mode. Use 'crop' or 'pad'.")

    adjusted_clips.append(first_clip_resized)

    # Process the rest of the images
    for clip in image_clips[1:]:
        # Resize clip to target height while maintaining aspect ratio
        clip_resized = resize_is_needed(clip, target_height)
        clip_width, clip_height = clip_resized.size

        if clip_width > standard_width:
            if mode == "crop":
                # Crop the clip horizontally to match the standard width
                x_center = clip_width / 2
                x1 = x_center - standard_width / 2
                x2 = x_center + standard_width / 2
                clip_final = clip_resized.crop(x1=x1, x2=x2)
                ice(
                    f"Crop to ⏬smaller : w{clip_final.size[0]} x h{clip_final.size[1]}"
                )
            elif mode == "pad":
                # Since clip is wider than standard width, we need to crop
                x_center = clip_width / 2
                x1 = x_center - standard_width / 2
                x2 = x_center + standard_width / 2
                clip_final = clip_resized.crop(x1=x1, x2=x2)
                ice(f"Pad to ⏬smaller : w{clip_final.size[0]} x h{clip_final.size[1]}")
        elif clip_width < standard_width:
            if mode == "crop":
                # Since clip is narrower than standard width, we need to stretch or pad
                # For crop mode, we can center the clip on a black background
                clip_final = clip_resized.on_color(
                    size=(standard_width, target_height),
                    color=(0, 0, 0),
                    col_opacity=1,
                    pos=("center", "center"),
                )
                ice(f"Crop to ⏫bigger : w{clip_final.size[0]} x h{clip_final.size[1]}")
            elif mode == "pad":
                # Pad the clip horizontally to match the standard width
                clip_final = clip_resized.on_color(
                    size=(standard_width, target_height),
                    color=(0, 0, 0),
                    col_opacity=1,
                    pos=("center", "center"),
                )
                ice(f"Pad to ⏫bigger : w{clip_final.size[0]} x h{clip_final.size[1]}")
        else:
            # Width matches the standard width
            clip_final = clip_resized

        adjusted_clips.append(clip_final)

    return adjusted_clips


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
    num_channels = (
        frame.shape[2] if len(frame.shape) == 3 else 1
    )  # Check if the frame has color channels
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
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        return True
    return False


# # Assuming 'final_video' is your video clip and 'audio_duration' is the duration of the audio
# text = "ВОТ БЫ БЫЛА"  # The text you want to add

# # Add text overlay to the video
# final_video_with_text = add_text_overlay(final_video, text, duration=audio_duration)

# # Save the final video with text
# final_video_with_text.write_videofile("output_with_text.mp4", fps=24)


def add_text_overlay(
    video_clip, text, duration, fontsize=50, color="white", transparency=0.6
):
    # Create the text clip
    text_clip = (
        TextClip(text, fontsize=fontsize, color=color, font="Arial-Bold")
        .set_duration(duration)
        .set_position(
            ("center", "bottom")
        )  # Position at the center bottom of the video
        .set_opacity(transparency)
    )  # Set transparency

    # Overlay the text on the video
    video_with_text = CompositeVideoClip([video_clip, text_clip])

    return video_with_text
