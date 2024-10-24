import cv2
from console_tools import prefix_color
from console_tools import ice
from model import Crop, Profile, TextConfig
from moviepy.editor import *
import os
import convertor
from multiprocessing import Pool
import argparse
import tools

# start :
# > conda activate audio_env
# > python.exe .\convert.py

#   Id CommandLine
#   -- -----------
#    1 conda init
#    2 cd D:\Src\AudioVisualizerVideoGenerator\src
#    4 which python.exe
#    7 conda install moviepy
#    9 conda activate audio_env
#   11 conda install moviepy
#   15 conda install opencv-python
#   17 pip install opencv-python
#   18 python.exe .\convert.py

@prefix_color("ProcFOLDERS", "magenta")
def process_folders(base_folder, args: argparse.Namespace, num_workers=1):
    # Поиск всех папок, начинающихся с "Clip"
    folders = [os.path.join(base_folder, folder) \
               for folder in sorted(os.listdir(base_folder)) \
               if folder.startswith("Clip") and len(folder) == 5]

    ice(f'📁Folders found: {folders}')

    # Path to the GIF file (if needed)
    gif_file = os.path.join(base_folder, "static", "animated3.gif")  # Ensure the path is correct

    # Determine the number of CPU cores or use the specified number of workers
    num_cores = num_workers if num_workers else os.cpu_count()
    ice(f"Using CPU cores: 🖥 {num_cores}. Total CPUs: 🖥 {os.cpu_count()}")
    
    profiles = {
        "test": Profile(
            name="🧪Test",
            fps=6,
            resize=0.5,
            # crop=Crop(start=0, end=15),
            preset="faster"
        ),
        "quality_test": Profile(
            name="🧪👍 Quality Test",
            fps=60,
            crop=Crop(start=25, end=30),
            preset="medium"
        ),
        "final_fast": Profile(
            name="👍Final fast 🏃💨",
            fps=24,
            crop=None,
            preset="faster"
        ),
        "final": Profile(
            name="👍Final",
            fps=60,
            # crop=Crop(start=0, end=170),
            preset="medium"
        )
    }

    profileId = args.profile or  "final_fast"
    profile = profiles[profileId]
    ice(f'Used profile : {profile.name}')
    colormap_name = args.colormap or "COLORMAP_JET"
    colormap = getattr(cv2, colormap_name, cv2.COLORMAP_JET)
    ice(f'Used colormap : {args.colormap}')    
    image_duration = args.image_duration or 20
    ice(f'Slideshow image_duration : {image_duration}')
    text = TextConfig(args)
    ice(f'TextConfig : {text}')

    for folder in folders:
        process_folder(folder, num_cores, profile, gif_file, colormap, image_duration, text)
                

@prefix_color("ProcFOLDER", "yellow")
def process_folder(folder, num_cores, profile, gif_file, colormap, image_duration, text: TextConfig):

    ice(f'-------- Folder: 📁{folder} -------------------------')
    # process_folder_obsolete(folder, num_cores, gif_file, profile)

    ice(f'Use workers: 🖥️{num_cores}')
    parts = list(range(num_cores))  # Creating a list of parts from 0 to num_cores - 1

    audio_file = tools.get_audio_file(folder)
    # Проверяем, существует ли аудио-файл
    if not os.path.isfile(audio_file):
        print(f"❌Audio file not found in {folder}")
        return

    ice(f'🎧Audio found: {audio_file}')
    clip_name = tools.get_filename_without_extension(audio_file)
    output_file = os.path.join(folder, f"{clip_name}.mp4")

    # Prepare arguments for create_video_from_folder
    args = []
    outputfiles = []
    for part in parts:
        outputfile = os.path.join(folder, f"output_part_{part}.mp4")
        outputfiles.append(outputfile)
        args.append((audio_file, profile, gif_file, part, num_cores, False, outputfile, colormap, image_duration, text))
    # (folder, profile: Profile, gif_file=None, part=None, num_cores=1, is_audio=True, output_file=None):

    if num_cores > 1:
        # Process the folder in parallel
        with Pool(processes=num_cores) as pool:
            pool.starmap(convertor.create_video_from_folder, args)
            
        # # Output file path
        tools.merge_videos_with_audio(outputfiles, audio_file, output_file, profile)
    else:
        convertor.create_video_from_folder(audio_file, profile, gif_file, None, num_cores, True, output_file, colormap, image_duration, text)


# def process_folder_obsolete(folder, num_cores, gif_file, profile):

#     # Determine parts based on the number of cores
#     parts = list(range(num_cores))  # Creating a list of parts from 0 to num_cores - 1

#     # Prepare arguments for create_video_from_folder
#     args = [(folder, gif_file, part, num_cores, profile) for part in parts]

#     if num_cores > 1:
#         # Process the folder in parallel
#         with Pool(processes=num_cores) as pool:
#             pool.starmap(convertor.create_video_from_folder, args)
#         # folder = 'path/to/your/videos'
#         video_files = sorted([os.path.join(base_folder, f) for f in os.listdir(base_folder) if f.endswith('.mp4') and f.startswith('Clip1')])

#         # # Output file path
#         output_file = os.path.join(folder, "Clip1_output_video.mp4")
                
#         convertor.merge_videos(output_file, video_files)
#     else:
#         convertor.create_video_from_folder(folder, gif_file, 0, num_cores, profile)
        

# Основной запуск
if __name__ == "__main__":

    # Установить переменную окружения динамически на основе количества доступных ядер
    os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())

    parser = argparse.ArgumentParser(description="Create video clip from music file and add slideshow with music visualization")

    #  python .\convert.py --worker 1 --profile test --colormap COLORMAP_SPRING --image_duration 60 --text "КУДА УХОДЯТ|||ДЕНЬГИ?" --text_shot 1
    # Определение аргументов
    parser.add_argument('--workers', type=int, required=False, help='Workers used for parall running')
    parser.add_argument('--profile', type=str, required=False, help='Used performance profile: test, quality test, final_fast, final')
    parser.add_argument('--colormap', type=str, required=False, help='Using colormap by OpenCV lib') # https://learnopencv.com/applycolormap-for-pseudocoloring-in-opencv-c-python/
    parser.add_argument('--text', type=str, required=False, help='Add text to clip') 
    parser.add_argument('--text_shot', type=bool, required=False, help='Only save in screenshort, not in clip') 
    parser.add_argument('--image_duration', type=int, required=False, help='slideshow: image duration') 
    args = parser.parse_args()

    base_folder = "../"  # Укажите путь к основной папке, содержащей папки Clip
    num_workers = args.workers or 2  # Количество параллельных процессов

    process_folders(base_folder, args, num_workers)