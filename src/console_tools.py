from functools import wraps
from rich.console import Console
from rich.text import Text
from icecream import ic

console = Console()
# Переменные для хранения текущего префикса и цвета
current_prefix = ""
current_color = ""

def colored_ic(*args):
    # Превращаем аргументы в строку с пробелами
    values = " ".join(map(str, args))
    # Создаем цветной префикс
    prefix_text = Text(f"[{current_prefix}] ", style=current_color)
    # Выводим через Rich с цветным префиксом и результатом переменных
    console.print(prefix_text.append(values))

# Переопределение стандартной функции ic() для работы с цветом и суффиксом
def ice(*args):
    values = tuple(map(str, args))  # Преобразование значений переменных в строки
    colored_ic(*values)  # Выводим значения с цветом и суффиксом


# Декоратор для установки префикса и цвета
def prefix_color(prefix, color):
    """
    color : black, red, green, yellow, blue, magenta, cyan, white, bright_black, bright_red, bright_green, bright_yellow, bright_blue, bright_magenta, bright_cyan, bright_white
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global current_prefix, current_color
            current_prefix = prefix
            current_color = color
            ic.configureOutput(outputFunction=lambda x: console.print(Text(f"[{current_prefix:40}] ", style=current_color).append(x)))
            return func(*args, **kwargs)
        return wrapper
    return decorator


# List of available color names
colors = [
    "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
    "bright_black", "bright_red", "bright_green", "bright_yellow", "bright_blue",
    "bright_magenta", "bright_cyan", "bright_white", "aliceblue", "antiquewhite",
    "aqua", "aquamarine", "azure", "beige", "bisque", "blanchedalmond",
    "blueviolet", "brown", "burlywood", "cadetblue", "chartreuse", "chocolate",
    "coral", "cornflowerblue", "cornsilk", "crimson", "darkblue", "darkcyan",
    "darkgoldenrod", "darkgray", "darkgreen", "darkkhaki", "darkmagenta",
    "darkolivegreen", "darkorange", "darkorchid", "darkred", "darksalmon",
    "darkseagreen", "darkslateblue", "darkslategray", "darkturquoise",
    "darkviolet", "deeppink", "deepskyblue", "dimgray", "dodgerblue",
    "firebrick", "floralwhite", "forestgreen", "fuchsia", "gainsboro",
    "ghostwhite", "gold", "goldenrod", "gray", "greenyellow", "honeydew",
    "hotpink", "indianred", "indigo", "ivory", "khaki", "lavender",
    "lavenderblush", "lawngreen", "lemonchiffon", "lightblue", "lightcoral",
    "lightcyan", "lightgoldenrodyellow", "lightgray", "lightgreen", "lightpink",
    "lightsalmon", "lightseagreen", "lightskyblue", "lightslategray",
    "lightsteelblue", "lightyellow", "lime", "limegreen", "linen", "maroon",
    "mediumaquamarine", "mediumblue", "mediumorchid", "mediumpurple",
    "mediumseagreen", "mediumslateblue", "mediumspringgreen", "mediumturquoise",
    "mediumvioletred", "midnightblue", "mintcream", "mistyrose", "moccasin",
    "navajowhite", "navy", "oldlace", "olive", "olivedrab", "orange", "orangered",
    "orchid", "palegoldenrod", "palegreen", "paleturquoise", "palevioletred",
    "papayawhip", "peachpuff", "peru", "pink", "plum", "powderblue", "purple",
    "rebeccapurple", "rosybrown", "royalblue", "saddlebrown", "salmon",
    "sandybrown", "seagreen", "seashell", "sienna", "silver", "skyblue",
    "slateblue", "slategray", "snow", "springgreen", "steelblue", "tan", "teal",
    "thistle", "tomato", "turquoise", "violet", "wheat", "whitesmoke",
    "yellowgreen"
]

# Function to display all colors
# python -c "import console_tools; console_tools.display_all_colors()" 
def display_all_colors():
    for color in colors:
        colored_text = Text(f"{color}", style=color)
        console.print(colored_text)
