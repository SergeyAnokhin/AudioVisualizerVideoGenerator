from moviepy.editor import *
import os
import convertor
from multiprocessing import Pool

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
    print("Using CPU cores: ", num_cores)

    # Determine parts based on the number of cores
    parts = list(range(num_cores))  # Creating a list of parts from 0 to num_cores - 1

    # Prepare arguments for create_video_from_folder
    args = [(folder, gif_file, part) for part in parts]

    # Process the folder in parallel
    with Pool(processes=num_cores) as pool:
        pool.starmap(convertor.create_video_from_folder, args)

# Основной запуск
if __name__ == "__main__":

    # Установить переменную окружения динамически на основе количества доступных ядер
    os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())

    base_folder = "../"  # Укажите путь к основной папке, содержащей папки Clip
    num_workers = 4  # Количество параллельных процессов

    process_folders(base_folder, num_workers)