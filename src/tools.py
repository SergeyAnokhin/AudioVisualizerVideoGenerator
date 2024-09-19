import numpy as np
import librosa
from moviepy.editor import *
import os
from PIL import Image


def get_audio_file(folder):
    # Путь к аудио-файлу
    audio_file = [os.path.join(folder, music) \
                    for music in os.listdir(folder) if music.endswith(('.mp3'))][0] # os.path.join(folder, "music.mp3")

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

def suggest_frequency_bands(audio_file, num_bands=4, sr=None, n_fft=2048, hop_length=None):
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
        freq_mask = (frequencies >= freq_bins[i]) & (frequencies < freq_bins[i+1])
        if np.any(freq_mask):
            flux = np.sum(spectral_flux[freq_mask])
            flux_per_band.append((flux, freq_bins[i], freq_bins[i+1]))

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


def merge_videos_with_audio(video_files, audio_file, output_file):
    """
    Объединяет список видеофайлов и добавляет к ним аудио, затем сохраняет результат в выходной файл.
    
    :param video_files: Список путей к видеофайлам (без аудио).
    :param audio_file: Путь к аудиофайлу (MP3).
    :param output_file: Путь к выходному видеофайлу.
    """
    print(f"🚀 Начинается процесс объединения {len(video_files)} видеофайлов.")
    
    # Загружаем видеофайлы
    clips = []
    for idx, file in enumerate(video_files):
        print(f"📂 Загрузка видеофайла {idx + 1}/{len(video_files)}: {file}")
        clip = VideoFileClip(file)
        clips.append(clip)
    
    print("✅ Все видеофайлы успешно загружены.")

    # Объединяем видеофайлы
    print("🔗 Объединение видеофайлов...")
    final_clip = concatenate_videoclips(clips, method="compose")
    print("🎬 Видео успешно объединено.")

    # Загружаем аудио файл
    print(f"🎵 Загрузка аудиофайла: {audio_file}")
    audio = AudioFileClip(audio_file)
    print("✅ Аудиофайл успешно загружен.")

    # Добавляем аудио к финальному видео
    print("🎶 Добавление аудио к объединенному видео...")
    final_clip = final_clip.set_audio(audio)
    print("✅ Аудио успешно добавлено к видео.")

    # Сохраняем итоговый файл
    print(f"💾 Сохранение итогового файла: {output_file}")
    final_clip.write_videofile(output_file, codec="libx264", preset="ultrafast", threads=4)
    print(f"🎉 Файл успешно сохранен: {output_file}")


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

def add_gif(gif_file, audio_duration, slideshow):
    if gif_file and os.path.isfile(gif_file):
        print("✔Gif file found")

        has_mask = False # has_transparency(gif_file)
        # Загружаем GIF и зацикливаем на всю длительность аудио
        gif_clip = (VideoFileClip(gif_file, has_mask)
                    .loop(duration=(14.0 * 2.0)) # two times # duration=audio_duration)
                    # .resize(0.5)  # Масштабирование (0.5 = 50% от исходного размера)
                    .set_position(("left", "bottom")))  # Позиция (можно изменить на нужную)

        # Делаем фон GIF прозрачным (удаляем определенный цвет)
        gif_clip = gif_clip.fx(vfx.mask_color, color=[0, 0, 0], thr=100, s=5)

        inspect_clip("gif_clip", gif_clip)

        # Накладываем GIF поверх слайд-шоу
        final_video = CompositeVideoClip([slideshow, gif_clip])
    else:
        final_video = slideshow
    return final_video

def create_slideshow_with_fade_OLD(images, audio_duration, image_duration=2, fade_duration=0.1):
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

from moviepy.editor import ImageClip, concatenate_videoclips

def create_slideshow_with_fade(images, audio_duration, image_duration=2, fade_duration=0.1):
    image_clips = []
    
    print(f"SLIDES🖼 :: Total images: {len(images)} :: 🔁Looping at ⌛duration: {audio_duration} secs")
    # Создаем клипы для каждого изображения с эффектами затемнения и появления
    for img in images:
        clip = ImageClip(img).set_duration(image_duration)
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
    print(f"SLIDES🖼 :: Replicated images: {len(replicated_clips)} :: 🔁Repeated: {num_repeats} times")
    
    # Конкатенируем размноженные клипы в финальное слайдшоу
    full_slideshow = concatenate_videoclips(replicated_clips, method="compose")
    
    # Обрезаем слайдшоу, чтобы оно соответствовало длительности аудио
    final_slideshow = full_slideshow.subclip(0, audio_duration)
    
    return final_slideshow



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


# # Assuming 'final_video' is your video clip and 'audio_duration' is the duration of the audio
# text = "ВОТ БЫ БЫЛА"  # The text you want to add

# # Add text overlay to the video
# final_video_with_text = add_text_overlay(final_video, text, duration=audio_duration)

# # Save the final video with text
# final_video_with_text.write_videofile("output_with_text.mp4", fps=24)

def add_text_overlay(video_clip, text, duration, fontsize=50, color='white', transparency=0.6):
    # Create the text clip
    text_clip = (TextClip(text, fontsize=fontsize, color=color, font='Arial-Bold')
                 .set_duration(duration)
                 .set_position(('center', 'bottom'))  # Position at the center bottom of the video
                 .set_opacity(transparency))  # Set transparency

    # Overlay the text on the video
    video_with_text = CompositeVideoClip([video_clip, text_clip])

    return video_with_text