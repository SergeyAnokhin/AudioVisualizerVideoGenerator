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