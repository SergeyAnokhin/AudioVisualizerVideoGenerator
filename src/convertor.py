from moviepy.editor import *
import os
import cv2
import equalizers
from PIL import Image

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
    images = [os.path.join(folder, img) for img in sorted(os.listdir(folder)) if img.endswith(('.png', '.jpg', '.jpeg'))]

    # Длительность аудио-файла
    audio = AudioFileClip(audio_file)
    audio_duration = audio.duration

    start, end = get_segment_duration(audio_duration, part, num_cores)
    print(f"PART {part}: ⏱ [{start:.0f}...{end:.0f}] secs")

    # Длительность каждого изображения (в секундах)
    image_duration = 10  # Измените на желаемую длительность
    
    # Создаем слайд-шоу с повторением и затемнением
    print("⏩Create looping slideshow with fade transition")
    slideshow = create_slideshow_with_fade(images, audio_duration=audio_duration, 
                                           image_duration=image_duration, fade_duration=0.1)


    inspect_clip("slideshow", slideshow)

    # Проверяем наличие GIF-файла и накладываем его на видео
    final_video = add_gif(gif_file, audio_duration, slideshow)

    # Добавляем аудио к видео
    final_video = final_video.set_audio(audio)

    # Создаем эквалайзерный клип
    print("⏩Create equalizer visualization")
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
                          amplitude_threshold=0.2,
                          amplification=10.0)

    
    equalizer_clip = equalizer_clip.set_opacity(0.2)  # Опционально: установить прозрачность

    inspect_clip("final_video", final_video)
    inspect_clip("equalizer_clip", equalizer_clip)


    # Накладываем эквалайзер поверх финального видео
    print("➕Add equalizer visualization")
    final_video = CompositeVideoClip([final_video, equalizer_clip])

    # fastest for tests:
    mode = 'quality_test'
    
    if mode == 'test':
        print("Mode: 🧪Test")
        final_video = final_video.resize(0.5)
        if num_cores > 1:
            final_video = final_video.subclip(start, end)
        else:
            final_video = final_video.subclip(25, 35) # Start at 0 seconds and end at 10 seconds
        fps = 6
        preset = 'ultrafast' # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo
        codec = 'libx264' # libx264, libx265, mpeg4, vp8, vp9, prores, mjpeg, rawvideo, libvpx, libvpx-vp9, libtheora
    elif mode == 'quality_test':
        print("Mode: 🧪👍 Quality Test")
        # final_video = final_video.resize(0.5)
        if num_cores > 1:
            final_video = final_video.subclip(start, end)
        else:
            final_video = final_video.subclip(25, 35) # Start at 0 seconds and end at 10 seconds
        fps = 60
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
    end_time = start_time + segment_length - 1
    
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
    return final_video

def create_slideshow_with_fade(images, audio_duration, image_duration=2, fade_duration=0.1):
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
    looped_slideshow = slideshow.loop(duration=audio_duration)

    return looped_slideshow


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