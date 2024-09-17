# AudioVisualizerVideoGenerator

AudioVisualizerVideoGenerator is a Python script that creates video files from audio and image sequences. It allows you to generate a slideshow of images synchronized to an audio file, with an optional audio visualizer effect. The visualizer reacts to the audio file, creating a colorful display of bars around circles that move according to the left and right audio channels.

## Features

- **Batch Video Creation**: Processes multiple folders (Clip 1, Clip 2, etc.) containing audio and image files, generating individual videos for each folder.
- **Customizable Slideshow**: Creates a slideshow using images in the folder, with adjustable duration for each image.
- **Audio Visualizer**: Adds a visualizer effect with animated bars around circles that respond to the left and right audio channels.
- **GIF Overlay**: Optionally overlays a GIF animation on the video.
- **Parallel Processing**: Supports parallel processing to create multiple videos simultaneously for faster execution.

## Requirements

- Python 3.x
- Required Python packages:
  - moviepy
  - numpy
  - librosa
  - opencv-python

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/AudioVisualizerVideoGenerator.git
    ```
2. Navigate to the project directory:
    ```bash
    cd AudioVisualizerVideoGenerator
    ```
3. Install the required packages:
    ```bash
    pip install moviepy numpy librosa opencv-python
    ```

## Usage

1. Place your audio file (`music.mp3`) and images (`.png`, `.jpg`, `.jpeg`) in folders named `Clip 1`, `Clip 2`, etc., in the project directory.

2. (Optional) Place an animated GIF file (`animated.gif`) in the project directory if you want to overlay a GIF on the video.

3. Run the script:
    ```bash
    python your_script_name.py
    ```
4. Adjust parameters such as image duration and the number of parallel processes directly in the script.

### Parameters

- `image_duration`: The duration (in seconds) for each image in the slideshow.
- `num_workers`: Number of parallel processes to use for video creation.
- `gif_file`: Path to an optional GIF file for overlay.

## Example

If you have the following directory structure:

AudioVisualizerVideoGenerator/ ├── Clip 1/ │ ├── music.mp3 │ ├── image1.jpg │ ├── image2.jpg ├── Clip 2/ │ ├── music.mp3 │ ├── image1.png │ ├── image2.png └── animated.gif


Running the script will generate `Clip 1_output_video.mp4` and `Clip 2_output_video.mp4`, each with the audio visualizer and image slideshow.

## Visualization

The script uses `moviepy`, `numpy`, `librosa`, and `opencv` to generate an audio-reactive visualizer. It analyzes the audio file to extract amplitude data for the left and right channels and visualizes it with animated bars around circles in the video.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests. Contributions are welcome!

## Author

- Your Name - [your_username](https://github.com/yourusername)

