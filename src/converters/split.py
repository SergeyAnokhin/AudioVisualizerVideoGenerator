from dataclasses import dataclass
from typing import Any, List

from moviepy import Clip

from console_tools import ice
from converters.aconverter import AConverter
from libs.task_data import TaskData


@dataclass
class SplitConverter(AConverter):

    @property
    def parts(self):
        return self.config["parts"]
    
    def convert_list(self, taskData: TaskData, clips: List[Any]) -> List[Any]:
        # Split the audio into parts
        ice(f'Use workers: 🖥️ {self.parts}')
        audio_parts = []
        part_duration = taskData.full_duration / self.parts
        for i in range(self.parts):
            start_time = i * part_duration
            end_time = (i + 1) * part_duration if i < self.parts - 1 else taskData.full_duration  # Make sure the last part ends exactly at the end of the clip
            ice(f"Part #{i}: ⏱ [{start_time:3.0f}...{end_time:3.0f}] secs")
            part = clips[0].subclip(start_time, end_time)
            audio_parts.append(part)

        return audio_parts        

    def convert(self, clip: Clip) -> Clip:
        # Example of generic processing for text conversion
        print(f"-- Split for parallel processing: {self.config}")
