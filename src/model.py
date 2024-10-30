# from argparse import Namespace


# class Profile:
#     def __init__(self, name, fps, resize=1, crop=None, preset="medium", codec='libx264', img_fade_duration=0.5, target_height = 1024, audio_fade_duration=0.0):
#         self.name = name
#         self.audio = Audio(audio_fade_duration, crop)
#         self.video = Video(fps, preset, codec)
#         self.slideshow = SlideShow(fade_duration = img_fade_duration, target_height=target_height, resize=resize)

#     def __str__(self):
#         return (f"Profile(name={self.name}, audio={self.audio}, video={self.video}, "
#                 f"slideshow={self.slideshow})")
    
#     def __repr__(self):
#         return self.__str__()
        
# class SlideShow:
#     def __init__(self, fade_duration = 0.5, target_height = 1024, resize = 1):
#         self.fade_duration = fade_duration
#         self.target_height = target_height
#         self.resize = resize

#     def __str__(self):
#         return (f"SlideShow(fade_duration={self.fade_duration!r}, target_height={self.target_height!r}, resize={self.resize!r},)")
    
#     def __repr__(self):
#         return self.__str__()

# class Audio:
#     def __init__(self, fade_duration=0.5, crop=None):
#         self.fade_duration=fade_duration
#         self.crop=crop

#     def __str__(self):
#         return (f"SlideShow(fade_duration={self.fade_duration!r})")
    
#     def __repr__(self):
#         return self.__str__()        

# class Video:
#     def __init__(self, fps=60, preset="medium", codec='libx264'):
#         self.fps=fps
#         self.preset = preset
#         self.codec = codec

#     def __str__(self):
#         return (f"SlideShow(fps={self.fps!r}, preset={self.preset!r}, codec={self.codec!r})")
    
#     def __repr__(self):
#         return self.__str__()     

class Duration:
    def __init__(self, start=0, end=None):
        self.start = start
        self.end = end
        
    def is_empty(self):
        return self.end == None and self.start == 0

    def __str__(self):
        return f"⏱ [{self.start:3.0f}...{self.end:3.0f}] secs"
    
    def __repr__(self):
        return self.__str__()
    
    
# class TextConfig:
#     def __init__(self, text='', text_shot=True):
#         self.text = text.replace('|', '\n')
#         self.text_shot = text_shot

#     def __init__(self):
#         self.text = ''
#         self.text_shot = True

#     def __init__(self, args: Namespace):
#         self.text = (args.text or '').replace('|', '\n')
#         self.text_shot = args.text_shot or True

#     def is_empty(self):
#         return self.text == ''

#     def __str__(self):
#         return f"TextConfig(text='{self.text}', text_shot={self.text_shot})"
    
#     def __repr__(self):
#         return f"TextConfig(text={self.text!r}, text_shot={self.text_shot!r})"
