from dataclasses import dataclass

@dataclass
class TaskData:
    workers: int
    name: str
    folder: str
    error: str
    full_duration: int