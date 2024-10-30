from dataclasses import dataclass
from typing import Any, Dict, List

from converters.aconverter import AConverter

@dataclass
class TextConverter(AConverter):

    def convert(self, clips: List) -> List:
        # Example of generic processing for text conversion
        print(f"-- Adding text with config: {self.config}")
