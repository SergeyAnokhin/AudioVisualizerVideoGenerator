import argparse
import os
from multiprocessing import Pool

from moviepy.editor import *
from rich.pretty import pprint

from converters.audio import AudioConverter
import libs.Profile
from libs.task_data import TaskData
import tools
from console_tools import ice, prefix_color
from libs.Profile import Task

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

# Hierarchy:
# Main
#  \ Folder
#   \ Task
#    \ Convertor (List[Clip]) -> List[Clip]
#     \ Worker

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
    
    # profiles = {
    #     "test": Profile(
    #         name="🧪Test",
    #         fps=6,
    #         resize=0.5,
    #         # crop=Crop(start=0, end=15),
    #         preset="faster"
    #     ),
    #     "quality_test": Profile(
    #         name="🧪👍 Quality Test",
    #         fps=60,
    #         crop=Crop(start=25, end=30),
    #         preset="medium"
    #     ),
    #     "final_fast": Profile(
    #         name="👍Final fast 🏃💨",
    #         fps=24,
    #         crop=None,
    #         preset="faster"
    #     ),
    #     "final": Profile(
    #         name="👍Final",
    #         fps=60,
    #         # crop=Crop(start=0, end=170),
    #         preset="medium"
    #     ),
    #     "short": Profile(
    #         name="🎞Short",
    #         fps=60,
    #         crop=Crop(start=0, end=58),
    #         preset="medium",
    #         img_fade_duration=0.1,
    #         audio_fade_duration=0.5
    #     )        
    # }

    # profileId = args.profile or  "final_fast"
    # profile = profiles[profileId]
    # ice(f'Used profile : {profile.name}')
    # colormap_name = args.colormap or "COLORMAP_JET"
    # colormap = getattr(cv2, colormap_name, cv2.COLORMAP_JET)
    # ice(f'Used colormap : {args.colormap}')    
    # image_duration = args.image_duration or 20
    # ice(f'Slideshow image_duration : {image_duration}')
    # crop = args.crop
    # if crop:
    #     duration = tools.durations_to_seconds(crop)
    #     profile.audio.crop = Crop(start=duration[0], end=duration[1])
    #     num_cores = 1
    # if profile.crop:
    #     ice(f'✂Crop : {profile.crop}. ⚠ Use 1 worker ⚠')

    for folder in folders:
        process_folder(folder)
                

@prefix_color("ProcFOLDER", "white")
def process_folder(folder):

    ice(f'-------- Folder: 📁{folder} -------------------------')
    # process_folder_obsolete(folder, num_cores, gif_file, profile)

    configFile = os.path.join(folder, "config.yaml")
    if configFile == None or not os.path.isfile(configFile):
        print(f"❌Config file not found in {folder}")
        return
    
    config = libs.Profile.load_config(configFile)
    for task in config.tasks:
        process_task(folder, task)


@prefix_color("ProcTask", "yellow")
def process_task(folder, task: Task):

    ice(f'-----= Task: ⚙ {task.name} =------')
    # pprint(task)

    # parts = list(range(task.workers))  # Creating a list of parts from 0 to num_cores - 1
    taskData = TaskData(workers=task.workers, name=task.name, 
                    folder=folder, error=None)

    clips = [None]
    for convertor in task.converters:
        clips = convertor.convert_list(taskData, clips)
        if taskData.error:
            ice(f"❌{taskData.error}")
            return


    # if profile.crop and not profile.crop.is_empty():
    #    clip_name += "_crop"
    # output_file = os.path.join(folder, f"{clip_name}.mp4")

    # # Prepare arguments for create_video_from_folder
    # args = []
    # outputfiles = []
    # for part in parts:
    #     outputfile = os.path.join(folder, f"output_part_{part}.mp4")
    #     outputfiles.append(outputfile)
    #     args.append((audio_file, profile, gif_file, part, num_cores, False, outputfile, colormap, image_duration, text))
    # # (folder, profile: Profile, gif_file=None, part=None, num_cores=1, is_audio=True, output_file=None):

    # if num_cores > 1:
    #     # Process the folder in parallel
    #     with Pool(processes=num_cores) as pool:
    #         pool.starmap(convertor.create_video_from_folder, args)
            
    #     # # Output file path
    #     tools.merge_videos_with_audio(outputfiles, audio_file, output_file, profile)
    # else:
    #     convertor.create_video_from_folder(audio_file, profile, gif_file, None, num_cores, True, output_file, colormap, image_duration, text)

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
    parser.add_argument('--crop', type=str, required=False, help='crop audio in format "0:20,0:50"') # --crop 0:07,0:38
    args = parser.parse_args()

    base_folder = "../"  # Укажите путь к основной папке, содержащей папки Clip
    num_workers = args.workers or 2  # Количество параллельных процессов

    process_folders(base_folder, args, num_workers)