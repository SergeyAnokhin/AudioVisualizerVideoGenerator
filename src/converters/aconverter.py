import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List

from moviepy import Clip

from libs.task_data import TaskData

@dataclass
class AConverter(ABC):
    config: Dict[str, Any]

    def convert_list(self, taskData: TaskData, clips: List[Any]) -> List[Any]:
        results = [None] * len(clips)
        threads = []

        # Define a function to run each converter in a separate thread
        def run_converter(index: int, clip: Any):
            results[index] = self.convert(clip)

        # Create and start a thread for each clip using the current instance to convert
        for i, clip in enumerate(clips):
            thread = threading.Thread(target=run_converter, args=(i, clip))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        return results

    @abstractmethod
    def convert(self, clip: Clip) -> Clip:
        pass

    def __str__(self):
        return f"{self.__class__.__name__}(config={self.config})"

    def __repr__(self):
        return self.__str__()