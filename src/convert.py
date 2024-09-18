from moviepy.editor import *
import os
import convertor

def process_folders(base_folder, num_workers=1):
    # Поиск всех папок, начинающихся с "Clip"
    folders = [os.path.join(base_folder, folder) \
               for folder in sorted(os.listdir(base_folder)) \
               if folder.startswith("Clip") and len(folder) == 5]

    print('Folders found: ', folders)

    # Путь к GIF-файлу (если есть)
    gif_file = base_folder + "static/animated2.gif"  # Вы можете указать путь к вашему GIF-файлу

    # Используем параллельную обработку
    # with ProcessPoolExecutor(max_workers=num_workers) as executor:
    #     executor.map(create_video_from_folder, folders, [gif_file]*len(folders))
    convertor.create_video_from_folder(folders[0], gif_file)


# Основной запуск
if __name__ == "__main__":

    # Установить переменную окружения динамически на основе количества доступных ядер
    print("Use all CPU cores: ", os.cpu_count())
    os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())

    base_folder = "../"  # Укажите путь к основной папке, содержащей папки Clip
    num_workers = 1  # Количество параллельных процессов

    process_folders(base_folder, num_workers)