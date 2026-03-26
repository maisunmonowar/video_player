# Local Dual-Subtitle Video Player

A fully offline, cross-platform video player that automatically detects the original spoken language of any video, generates subtitles, and translates them into a user-specified language.

The player overlay displays **Translated Subtitles** at the top of the video and **Original Subtitles** at the bottom seamlessly.

![Dual Subtitle Overview](https://img.shields.io/badge/Status-Functional-brightgreen.svg)

## Key Features
- **100% Offline Processing**: Uses local models ensuring no APIs or internet services are required after the initial model download.
- **Cross-Platform Compatibility**: Supports Windows, Linux, AMD, and Intel architectures through generic CPU wheels for ML dependencies.
- **Auto Language Detection**: Automatically recognizes the spoken language in the video.
- **Dual Subtitles**: Overlays your chosen translation on top and the original syntax on the bottom.

## Technologies Used
- **[uv](https://github.com/astral-sh/uv)**: Blazing-fast Python package and project manager.
- **PyQt6**: Cross-platform application framework and multimedia player engine.
- **faster-whisper**: High-performance CPU-optimized audio transcription and language detection.
- **argostranslate**: Offline neural machine translation engine.
- **FFmpeg**: Video and audio extraction toolkit.

## Prerequisites
- [uv](https://github.com/astral-sh/uv) installed on your system.
- **FFmpeg** installed and available in your system's PATH. (`ffmpeg-python` relies on the system FFmpeg executable).

## Installation
1. Clone the repository and navigate to the project directory:
   ```bash
   cd video_player_2
   ```

2. Sync the environment and install dependencies using `uv`. (Note: The project uses explicit CPU wheels for PyTorch to prevent DLL initialization errors on non-CUDA systems).
   ```bash
   uv sync
   ```

## Usage
To start the application, run:
```bash
uv run main.py
```

1. Click **Open Video...** from the interface and select a compatible video file (e.g., `.mp4`, `.mkv`).
2. You will be prompted to enter the **target language code** (e.g., `es` for Spanish, `fr` for French, `en` for English).
3. The background worker will automatically:
   - Extract the audio from the video.
   - Detect the original spoken language and transcribe it using `faster-whisper`.
   - Translate the transcribed segments into your target language using `argostranslate` (it will download the specific language pair on the first run).
4. Once processing completes, click the **Play** button to view your video with dual subtitles!
