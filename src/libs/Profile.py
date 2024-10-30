import yaml
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any, List, Optional, Type, TypeVar, Dict

from converters.audio import AudioConverter
from converters.equalizers import EqualizerConverter
from converters.join import JoinConverter
from converters.slideshow import SlideshowConverter
from converters.split import SplitConverter
from converters.text import TextConverter
from converters.video import VideoConverter
from libs.task import Task

T = TypeVar('T')

# Define dataclasses
@dataclass
class Position:
    x: int
    y: int

    def __str__(self):
        return f"Position(x={self.x}, y={self.y})"

    def __repr__(self):
        return self.__str__()
    
@dataclass
class SongConfig:
    tasks: List[Task]

    def __str__(self):
        return f"SongConfig(tasks={self.tasks})"

    def __repr__(self):
        return self.__str__()

# Function to load the YAML configuration

def from_dict(data_class: Type[T], data: Dict[str, Any]) -> T:
    # Ensure the target class is a dataclass
    if not is_dataclass(data_class):
        raise TypeError(f"{data_class} is not a dataclass.")

    kwargs = {}
    for f in fields(data_class):
        field_value = data.get(f.name)
        # If the field is a nested dataclass, recursively parse it
        if is_dataclass(f.type):
            kwargs[f.name] = from_dict(f.type, field_value or {})
        # If the field is a list of dataclasses, recursively parse each item in the list
        elif isinstance(field_value, list) and len(field_value) > 0 and is_dataclass(f.type.__args__[0]):
            kwargs[f.name] = [from_dict(f.type.__args__[0], item) for item in field_value]
        else:
            # Otherwise, use the value directly
            kwargs[f.name] = field_value
    return data_class(**kwargs)

def load_config(file_path: str) -> SongConfig:
    # Load the YAML file and parse it into a dictionary
    with open(file_path, 'r') as f:
        config_dict = yaml.safe_load(f)

    tasks = []
    # Iterate through each task in the configuration
    for task_name, task_data in config_dict['song']['tasks'].items():
        converters = []
        # Iterate through each converter defined in the task
        for converter in task_data['converters']:
            convert_data = converter['convert']
            # Create specific converter objects based on the type
            if convert_data['type'] == 'audio':
                converters.append(AudioConverter(config=convert_data))
            elif convert_data['type'] == 'video':
                converters.append(VideoConverter(config=convert_data))
            elif convert_data['type'] == 'slideshow':
                converters.append(SlideshowConverter(config=convert_data))
            elif convert_data['type'] == 'equalizer':
                converters.append(EqualizerConverter(config=convert_data))
            elif convert_data['type'] == 'text':
                converters.append(TextConverter(config=convert_data))
            elif convert_data['type'] == 'split':
                converters.append(SplitConverter(config=convert_data))
            elif convert_data['type'] == 'join':
                converters.append(JoinConverter(config=convert_data))
            else:
                raise Exception(f"Unknown type: {convert_data['type']}")
            #     # If the type is not recognized, create a generic Converter
            #     converters.append(Converter(config=convert_data))
        # Create a Task object with the defined workers and converters
        task = Task(workers=task_data['workers'], converters=converters, name=task_name)
        tasks.append(task)

    # Return the full SongConfig object containing all tasks
    return SongConfig(tasks=tasks)

# Example usage
# if __name__ == "__main__":
#     config_path = "config.yaml"
#     # Load and print the configuration to verify the output
#     config = load_config(config_path)
#     print(config)
