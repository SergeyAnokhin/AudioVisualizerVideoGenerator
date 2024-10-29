import yaml
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any, List, Optional, Type, TypeVar, Dict

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
class Text:
    text: str
    position: Position
    size: int
    font: str
    color: str
    only_shots: bool

    def __str__(self):
        return f"Text(text={self.text}, position={self.position}, size={self.size}, font={self.font}, color={self.color}, only_shots={self.only_shots})"

    def __repr__(self):
        return self.__str__()

@dataclass
class EqualizerBand:
    start: int
    stop: int
    amplification: float

    def __str__(self):
        return f"EqualizerBand(start={self.start}, stop={self.stop}, amplification={self.amplification})"

    def __repr__(self):
        return self.__str__()

@dataclass
class Equalizer:
    colormap: str
    use_suggest_frequency_bands: bool
    bands: List[EqualizerBand]

    def __str__(self):
        return f"Equalizer(colormap={self.colormap}, use_suggest_frequency_bands={self.use_suggest_frequency_bands}, bands={self.bands})"

    def __repr__(self):
        return self.__str__()

@dataclass
class Audio:
    fade_duration: float
    crop: Optional[dict] = None

    def __str__(self):
        return f"Audio(fade_duration={self.fade_duration}, crop={self.crop})"

    def __repr__(self):
        return self.__str__()

@dataclass
class Video:
    fps: int
    preset: str
    codec: str

    def __str__(self):
        return f"Video(fps={self.fps}, preset={self.preset}, codec={self.codec})"

    def __repr__(self):
        return self.__str__()

@dataclass
class Slideshow:
    image_duration: int
    fade_duration: float
    target_height: Optional[int] = None
    resize: Optional[int] = None

    def __str__(self):
        return f"Slideshow(image_duration={self.image_duration}, fade_duration={self.fade_duration}, target_height={self.target_height}, resize={self.resize})"

    def __repr__(self):
        return self.__str__()

@dataclass
class TaskDefaults:
    workers: int
    audio: Audio
    video: Video
    slideshow: Slideshow
    equalizer: Equalizer
    text: List[Text]

    def __str__(self):
        return f"TaskDefaults(workers={self.workers}, audio={self.audio}, video={self.video}, slideshow={self.slideshow}, equalizer={self.equalizer}, text={self.text})"

    def __repr__(self):
        return self.__str__()

@dataclass
class Tasks:
    main: Optional[dict] = field(default_factory=dict)
    short: Optional[dict] = field(default_factory=dict)

    def __str__(self):
        return f"Tasks(main={self.main}, short={self.short})"

    def __repr__(self):
        return self.__str__()

@dataclass
class SongConfig:
    task_defaults: TaskDefaults
    tasks: Tasks

    def __str__(self):
        return f"SongConfig(task_defaults={self.task_defaults}, tasks={self.tasks})"

    def __repr__(self):
        return self.__str__()

# Function to load the YAML configuration
def load_config(file_path: str) -> SongConfig:
    with open(file_path, 'r') as f:
        config_dict = yaml.safe_load(f)
        
        # Parse the configuration dictionary into dataclasses
        task_defaults = config_dict['song']['task_defaults']
        tasks = config_dict['song']['tasks']

        # Parse Position and Text
        texts = [
            Text(
                text=t['text'],
                position=Position(**t['position']),
                size=t['size'],
                font=t['font'],
                color=t['color'],
                only_shots=t['only_shots']
            ) for t in task_defaults['text']
        ]

        # Parse EqualizerBands
        equalizer_bands = [
            EqualizerBand(**band) for band in task_defaults['equalizer']['bands']
        ]

        # Parse Equalizer
        equalizer = Equalizer(
            colormap=task_defaults['equalizer']['colormap'],
            use_suggest_frequency_bands=task_defaults['equalizer']['use_suggest_frequency_bands'],
            bands=equalizer_bands
        )

        # Create TaskDefaults object
        task_defaults_obj = TaskDefaults(
            workers=task_defaults['workers'],
            audio=Audio(**task_defaults['audio']),
            video=Video(**task_defaults['video']),
            slideshow=Slideshow(**task_defaults['slideshow']),
            equalizer=equalizer,
            text=texts
        )

        # Create Tasks object
        tasks_obj = Tasks(
            main=tasks.get('main', {}),
            short=tasks.get('short', {})
        )

        # Return the SongConfig object
        return SongConfig(task_defaults=task_defaults_obj, tasks=tasks_obj)

# Example usage
if __name__ == "__main__":
    config_path = "config.yaml"
    config = load_config(config_path)
    print(config)
