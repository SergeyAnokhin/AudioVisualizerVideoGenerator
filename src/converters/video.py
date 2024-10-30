
from dataclasses import dataclass
from typing import Any, Dict, List

from converters.aconverter import AConverter

@dataclass
class VideoConverter(AConverter):

    def convert(self, clips: List) -> List:
        # Example of generic processing for video conversion
        print(f"-- Converting video with config: {self.config}")

