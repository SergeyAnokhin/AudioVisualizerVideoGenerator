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
    
    num_cores = os.cpu_count()
    duration = 350
    print("Use all CPU cores: ", num_cores)
    
    chunk_size = duration / num_cores
    for chunk_number in range(num_cores):
        start = chunk_number * chunk_size
        end = min(start + chunk_size, duration)

        # Generate the chunk
        chunk = (start, end)
        print(f"- Chunk number {chunk_number}: {chunk}")

    # with Pool(num_cores) as pool:
    #     pool.map(create_video_from_folder, range(num_cores)) ???

    # Join:
    # clips = [VideoFileClip(f"output_{start}_{end}.mp4") for start, end in chunks]
    # final_clip = concatenate_videoclips(clips)
    # final_clip.write_videofile("final_output_video.mp4", threads=4)
    
    convertor.create_video_from_folder(folders[0], gif_file)


# Основной запуск
if __name__ == "__main__":

    # Установить переменную окружения динамически на основе количества доступных ядер
    os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())

    base_folder = "../"  # Укажите путь к основной папке, содержащей папки Clip
    num_workers = 1  # Количество параллельных процессов

    process_folders(base_folder, num_workers)