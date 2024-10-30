from dataclasses import dataclass

from moviepy import Clip

from converters.aconverter import AConverter


@dataclass
class JoinConverter(AConverter):

    def convert(self, clip: Clip) -> Clip:
        print(f"-- Join after parallel processing: {self.config}")
