# AIfunScript - Advanced Beat Detection to Funscript

AIfunScript is a tool for detecting musical beats (main rhythm/beat) from audio or video files and exporting them as [funscript](https://funscript.io/) files for use with interactive devices or video players.

## Features
- Detects main musical beats (not just onsets) using advanced algorithms (librosa beat tracking)
- Supports both audio and video files (extracts audio from video automatically)
- Exports results in standard funscript format
- Includes a graphical user interface (GUI) for easy use
- CLI and GUI modes available

## Requirements
- Python 3.8+
- librosa
- numpy
- moviepy (for video support)
- tkinter (for GUI)

Install all dependencies with:
```bash
pip install -r requirements.txt
```

## Command Line Usage

Detect beats and export funscript from an audio or video file:
```bash
python advanced_detector.py <input_audio_or_video> --funscript <output.funscript>
```
Example:
```bash
python advanced_detector.py "my_song.mp4" --funscript "my_song.funscript"
```

## GUI Usage

Start the graphical interface:
```bash
python gui_detector.py
```
- Select your audio or video file
- Choose output funscript file name
- Click "Start Detection" to generate the funscript

## Output
- The generated funscript file will contain beat-synchronized actions for use with compatible devices or players.

## Notes
- Only the main musical beats are detected (not every onset or transient)
- For best results, use clear rhythmic music
- Video files are supported if moviepy is installed

## License
MIT 
