# **AudioVisualizerVideoGenerator** 🎶🎥

A **Python-based audio and video processing** project using several libraries to perform transformations, equalizations, and conversions. The project includes custom Python scripts and models to handle media manipulation.

## **Description** 📄

This project is designed to handle various media tasks like audio equalization, video conversion, and processing using Python. It supports advanced functionality for transforming and editing audio/video files using a range of libraries such as NumPy, OpenCV, and MoviePy.

## **Installation** ⚙️

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## **Usage** 🛠️

To start using the scripts for audio and video processing, you can run the Python scripts directly in your terminal or include them in your project.

### **convertor.py** Overview:

This script is designed to create a slideshow from images synchronized with an audio file in `.mp3` format. The script searches for audio files in directories `Clip1`, `Clip2`, `Clip3`, and so on, using their names as the output video file name.

#### How it works:

1. An `.mp3` file is placed in the directory `Clip1`, `Clip2`, `Clip3`, etc. The name of this file will be used as the name of the output video file.
2. The script searches for images in these directories, sorted by name. It supports the following main image formats: `.jpg`, `.jpeg`, `.png`, and `.gfif`.
3. The images are compiled into a slideshow, which loops if the images run out.
4. The audio track is analyzed to add visualizations synchronized with the images.

### Example:

```bash
python convertor.py
```

Ensure your media files are in the proper directory for processing, or adjust the paths in the code accordingly.


## **Arguments** 🧾

The following arguments are available for the scripts:

### **convertor.py** Arguments:

- **--workers**: Specifies the number of CPU workers for parallel processing. Default is 2 if not provided.
- **--profile**: Specifies the performance profile to use. Available profiles are `test`, `quality_test`, `final_fast`, and `final`.

#### **Example**:

```bash
python convertor.py --workers 4 --profile final
```

This will use 4 CPU cores and the `final` profile for video processing, which is optimized for high quality.

## **Features** ✨

- **Audio Equalization**: Customize sound frequencies using `equalizers.py`.
- **Video Conversion**: Convert video formats and handle processing via `convertor.py` and `moviepy`.
- **Model Integration**: Use `model.py` for advanced operations like media classification or transformation.
- **Tooling Support**: Various helper functions available in `tools.py` for media handling.

## **Files Description** 📂

- `convertor.py`: Script to convert video files into different formats and handle basic video processing.
- `equalizers.py`: Contains functions to equalize audio using predefined filters.
- `model.py`: Implements machine learning models or algorithms to classify or transform media.
- `tools.py`: A set of utility functions to support audio and video handling.
- `requirements.txt`: Lists all the dependencies required for the project.

## **Requirements** 📦

The following libraries are required to run the project (found in the `requirements.txt` file):

- NumPy
- Librosa
- OpenCV-Python
- MoviePy
- FFMPEG
- Pillow 9.5.0
- Soxr

## **Contributors** 👥

Feel free to add your name here if you contribute to this project!

## **License** 📜

This project is licensed under the MIT License.


