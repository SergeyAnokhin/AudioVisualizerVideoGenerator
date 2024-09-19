from model import Crop, Profile
from moviepy.editor import *
import os
import convertor
from multiprocessing import Pool

import tools

# start :
# > conda activate audio_env
# > python.exe .\convert.py

#   Id CommandLine
#   -- -----------
#    1 conda init
#    2 cd D:\Src\AudioVisualizerVideoGenerator\src
#    3 where python.exe
#    4 which python.exe
#    5 python .\convert.py
#    6 D:\Prog\miniconda3\envs\audio_env\python.exe .\convert.py
#    7 conda install moviepy
#    8 D:\Prog\miniconda3\envs\audio_env\python.exe .\convert.py
#    9 conda activate audio_env
#   10 D:\Prog\miniconda3\envs\audio_env\python.exe .\convert.py
#   11 conda install moviepy
#   12 D:\Prog\miniconda3\envs\audio_env\python.exe .\convert.py
#   13 python.exe .\convert.py
#   14 python.exe .\convert.py
#   15 conda install opencv-python
#   16 python.exe .\convert.py
#   17 pip install opencv-python
#   18 python.exe .\convert.py

def process_folders(base_folder, num_workers=1):
    # Поиск всех папок, начинающихся с "Clip"
    folders = [os.path.join(base_folder, folder) \
               for folder in sorted(os.listdir(base_folder)) \
               if folder.startswith("Clip") and len(folder) == 5]

    print('CONVERT :: 📁Folders found: ', folders)

    # Path to the GIF file (if needed)
    gif_file = os.path.join(base_folder, "static", "animated2.gif")  # Ensure the path is correct

    # Determine the number of CPU cores or use the specified number of workers
    num_cores = num_workers if num_workers else os.cpu_count()
    print(f"Using CPU cores: {num_cores}. Total CPUs: {os.cpu_count()}")
    
    profiles = {
        "test": Profile(
            name="🧪Test",
            fps=6,
            resize=0.5,
            crop=Crop(start=5, end=35),
            preset="faster"
        ),
        "quality_test": Profile(
            name="🧪👍 Quality Test",
            fps=60,
            crop=Crop(start=25, end=35),
            preset="medium"
        ),
        "final_fast": Profile(
            name="👍Final fast 🏃💨",
            fps=24,
            preset="faster"
        ),
        "final": Profile(
            name="👍Final",
            fps=60,
            preset="medium"
        )
    }
    profile = profiles["test"]

    for folder in folders:
        process_folder(folder, num_cores, profile, gif_file)
                

def process_folder(folder, num_cores, profile, gif_file):

    print(f'CONVERT :: -------- Folder: 📁{folder} -------------------------')
    # process_folder_obsolete(folder, num_cores, gif_file, profile)

    print(f'CONVERT :: Use workers: 🖥️{num_cores}')
    parts = list(range(num_cores))  # Creating a list of parts from 0 to num_cores - 1

    audio_file = tools.get_audio_file()
    # Проверяем, существует ли аудио-файл
    if not os.path.isfile(audio_file):
        print(f"❌Audio file not found in {folder}")
        return

    print(f'CONVERT :: 🎧Audio found: {audio_file}')
    clip_name = tools.get_filename_without_extension(audio_file)
    output_file = os.path.join(folder, f"{clip_name}.mp4")

    # Prepare arguments for create_video_from_folder
    args = []
    outputfiles = []
    for part in parts:
        outputfile = os.path.join(folder, f"output_part_{part}.mp4")
        outputfiles.append(outputfile)
        args.append((audio_file, profile, gif_file, part, num_cores, False, outputfile))
    # (folder, profile: Profile, gif_file=None, part=None, num_cores=1, is_audio=True, output_file=None):

    if num_cores > 1:
        # Process the folder in parallel
        with Pool(processes=num_cores) as pool:
            pool.starmap(convertor.create_video_from_folder, args)
            
        # # Output file path
        tools.merge_videos_with_audio(outputfiles, audio_file, output_file)
                
        convertor.merge_videos(output_file, outputfiles)
    else:
        convertor.create_video_from_folder(audio_file, profile, gif_file, num_cores, True, output_file)


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

    base_folder = "../"  # Укажите путь к основной папке, содержащей папки Clip
    num_workers = 1  # Количество параллельных процессов

    process_folders(base_folder, num_workers)