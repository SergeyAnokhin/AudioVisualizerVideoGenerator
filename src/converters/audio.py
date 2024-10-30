
import os
from dataclasses import dataclass
from typing import Any, List

from moviepy import Clip
from moviepy.editor import *

from model import Duration
import tools
from console_tools import ice
from converters.aconverter import AConverter
from libs.task_data import TaskData


# Define specific converter types with a common config field and a generic convert function
@dataclass
class AudioConverter(AConverter):
    
    def crop(self, max_duration=999):
        if 'crop' not in self.config:
            return None
        crop = self.config['crop']
        start = tools.convert_to_seconds(crop['start'])
        end = tools.convert_to_seconds(crop['end'])
        end = end if end <= max_duration else max_duration  
        return Duration(start, end)
    
    def read_audio_file(self, taskData: TaskData):
        audio_file = tools.get_audio_file(taskData.folder)
        # # Проверяем, существует ли аудио-файл
        if audio_file == None or not os.path.isfile(audio_file):
            taskData.error = f"Audio file not found"
            return
        ice(f'🎧Audio found: {audio_file}')

        # tools.suggest_frequency_bands(audio_file)

        # clip_name = tools.get_filename_without_extension(audio_file)

        # Длительность аудио-файла
        audio = AudioFileClip(audio_file)
        taskData.full_duration = audio.duration
        ice(f"🎶Audio ⏱duration: {audio.duration} secs")

    def convert(self, clip: Clip) -> Clip:
        audio = self.read_audio_file(taskData)

        if self.crop():
            crop = self.crop(audio.duration)
            ice(f"Crop ✂️✂️✂️ : {crop}")
            audio = audio.subclip(crop.start, crop.end)

        if clip != None:
            pass
            # Add audio to file


