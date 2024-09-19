from moviepy.editor import *
import os
import convertor
from multiprocessing import Pool

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

    print('Folders found: ', folders)

    folder = folders[0]

    # Path to the GIF file (if needed)
    gif_file = os.path.join(base_folder, "static", "animated2.gif")  # Ensure the path is correct

    # Determine the number of CPU cores or use the specified number of workers
    num_cores = num_workers if num_workers else os.cpu_count()
    print(f"Using CPU cores: {num_cores}. Total CPUs: {os.cpu_count()}")

    # convertor.create_video_from_folder(folder, gif_file, None)

    # Determine parts based on the number of cores
    parts = list(range(num_cores))  # Creating a list of parts from 0 to num_cores - 1

    # Prepare arguments for create_video_from_folder
    args = [(folder, gif_file, part, num_cores, 6) for part in parts]

    if num_cores > 1:
        # Process the folder in parallel
        with Pool(processes=num_cores) as pool:
            pool.starmap(convertor.create_video_from_folder, args)
        # folder = 'path/to/your/videos'
        video_files = sorted([os.path.join(base_folder, f) for f in os.listdir(base_folder) if f.endswith('.mp4') and f.startswith('Clip1')])

        # # Output file path
        output_file = os.path.join(folder, "Clip1_output_video.mp4")
                
        convertor.merge_videos(output_file, video_files)
    else:
        convertor.create_video_from_folder(folder, gif_file, 0, num_cores, fps=24)
        

# Основной запуск
if __name__ == "__main__":

    # Установить переменную окружения динамически на основе количества доступных ядер
    os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())

    base_folder = "../"  # Укажите путь к основной папке, содержащей папки Clip
    num_workers = 1  # Количество параллельных процессов

    process_folders(base_folder, num_workers)