
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from converters.aconverter import AConverter
from libs.Profile import Position


# Define specific converter types with a common config field and a generic convert function
@dataclass
class LogoConverter(AConverter):

    def convert(self, clips: List) -> List:
        # Example of generic processing for audio conversion
        print(f"-- Converting logo with config: {self.config}")

