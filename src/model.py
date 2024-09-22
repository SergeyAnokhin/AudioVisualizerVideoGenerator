from argparse import Namespace


class Profile:
    def __init__(self, name, fps, resize=1, crop=None, preset="medium", codec='libx264'):
        self.name = name
        self.fps = fps
        self.resize = resize
        self.crop = crop
        self.preset = preset
        self.codec = codec

    def __str__(self):
        return (f"Profile(name={self.name}, fps={self.fps}, resize={self.resize}, "
                f"crop={self.crop}, preset={self.preset}, codec={self.codec})")
    
    def __repr__(self):
        return (f"Profile(name={self.name!r}, fps={self.fps!r}, resize={self.resize!r}, "
                f"crop={self.crop!r}, preset={self.preset!r}, codec={self.codec!r})")
        
class Crop:
    def __init__(self, start=0, end=None):
        self.start = start
        self.end = end
        
    def is_empty(self):
        return self.end == None and self.start == 0

    def __str__(self):
        return f"Crop(start={self.start}, end={self.end})"
    
    def __repr__(self):
        return f"Crop(start={self.start!r}, end={self.end!r})"
    
    
class TextConfig:
    def __init__(self, text='', text_shot=True):
        self.text = text.replace('|', '\n')
        self.text_shot = text_shot

    def __init__(self):
        self.text = ''
        self.text_shot = True

    def __init__(self, args: Namespace):
        self.text = (args.text or '').replace('|', '\n')
        self.text_shot = args.text_shot or True

    def is_empty(self):
        return self.text == ''

    def __str__(self):
        return f"TextConfig(text='{self.text}', text_shot={self.text_shot})"
    
    def __repr__(self):
        return f"TextConfig(text={self.text!r}, text_shot={self.text_shot!r})"
