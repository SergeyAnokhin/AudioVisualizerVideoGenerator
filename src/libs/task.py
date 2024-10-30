
from dataclasses import dataclass
from typing import List

from converters.aconverter import AConverter

@dataclass
class Task:
    name: str
    workers: int
    converters: List[AConverter]
    
    def __str__(self):
        return f"Task(workers={self.workers}, converters={self.converters})"

    def __repr__(self):
        return self.__str__()