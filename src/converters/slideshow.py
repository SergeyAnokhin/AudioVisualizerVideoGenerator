
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from moviepy.editor import *
from rich.pretty import pprint

import tools
from console_tools import ice
from converters.aconverter import AConverter

@dataclass
class SlideshowConverter(AConverter):

    def convert(self, clips: List) -> List:
        # Example of generic processing for slideshow conversion
        print(f"-- Converting slideshow with config: ")
        pprint(self.config)

        # Создаем слайд-шоу с повторением и затемнением
        ice(f"⏩Create looping slideshow with fade transition")
        imageClips = [ImageClip(img) for img in images]
            
        target_height = 1024 # None # 
        if target_height != None:
            ice(f"Resulted height will be 🖼️↕️ {target_height}")

        imageClips = tools.adjust_image_clips(imageClips, target_height, mode='crop')
        slideshow = tools.create_slideshow_with_fade(imageClips, audio_duration=audio_duration, 
                                            image_duration=image_duration, fade_duration=0.1)        

