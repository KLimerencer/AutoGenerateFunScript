# Music Beat Detection Tool

A tool for detecting music beats and generating funscript files, supporting both audio and video input.

## Features

- 🎵 **Audio Processing**: Supports MP3, WAV, FLAC, M4A, OGG, and more
- 🎬 **Video Processing**: Supports MP4, AVI, MKV, MOV, WMV, FLV, and more, with automatic audio extraction
- 🎯 **Smart Detection**: Advanced beat detection using librosa
- 📊 **Visualization**: Generate waveform and spectrogram images
- 🎮 **Funscript Export**: Output in funscript format for interactive devices
- 🖥️ **GUI**: User-friendly graphical interface with progress bar
- ⚙️ **Parameter Tuning**: Adjustable detection thresholds for best results

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd AIfunScript
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify installation
```bash
python -c "import librosa, moviepy; print('Dependencies installed successfully!')"
```

## Usage

### GUI (Recommended)

1. **Start the GUI**
   ```bash
   python gui_detector.py
   ```

2. **Steps**
   - Select file type (audio or video)
   - Choose input file
   - Set output file path
   - Adjust detection parameters (optional)
   - Click "Start Detection" to process
   - Watch the progress bar and log for updates

3. **Parameter Description**
   - **Onset Threshold**: Sensitivity for detecting sound changes (0.1-1.0)
   - **Beat Threshold**: Sensitivity for beat detection (0.1-1.0)
   - **Detection Type**:
     - Beat Points: Regular beat points (recommended)
     - Onset Points: All sound change points (more sensitive)

### Command Line Usage

#### Basic
```bash
python advanced_detector.py input.mp3 --funscript output.funscript
```

#### Advanced
```bash
# Use onset points instead of beat points
python advanced_detector.py input.mp3 --funscript output.funscript --use-onset

# Adjust detection thresholds
python advanced_detector.py input.mp3 --funscript output.funscript --onset-threshold 0.3 --beat-threshold 0.7

# Generate visualization
python advanced_detector.py input.mp3 --funscript output.funscript --visualize
```

## Output Format

### Funscript Example
The generated funscript file contains:
```json
{
  "version": "1.0",
  "inverted": false,
  "range": 90,
  "actions": [
    {"at": 1000, "pos": 50},
    {"at": 2000, "pos": 80},
    ...
  ]
}
```
- `at`: Timestamp in milliseconds
- `pos`: Position/strength (0-100)
- `range`: Action range
- `inverted`: Invert flag

## Technical Details

### Beat Detection Algorithm
1. **Audio Preprocessing**: Load and resample audio
2. **Onset Detection**: Use librosa to detect sound changes
3. **Beat Tracking**: Track beats based on onset strength
4. **Strength Calculation**: Calculate action strength from audio energy
5. **Funscript Generation**: Convert detection results to funscript format

### Threshold Explanation
- **Onset Threshold**: Controls sensitivity for sound change detection
  - Low (0.1-0.3): Detects more subtle changes
  - High (0.7-0.9): Only detects obvious changes
- **Beat Threshold**: Controls sensitivity for beat detection
  - Low: Detects more possible beats
  - High: Only detects the most obvious beats

## File Structure

```
AIfunScript/
├── advanced_detector.py    # Core detector
├── gui_detector.py        # GUI interface
├── requirements.txt       # Dependency list
├── README.md              # Documentation
```

## FAQ

### Q: Video processing fails
**A**: Make sure moviepy is installed:
```bash
pip install --upgrade moviepy
```

### Q: Detection results are not ideal
**A**: Try adjusting the threshold parameters:
- Lower Onset Threshold to detect more changes
- Increase Beat Threshold for more regular beats

### Q: GUI does not respond
**A**: Check if tkinter is installed:
```bash
python -c "import tkinter; print('Tkinter available')"
```

### Q: Processing large files is slow
**A**: This is normal for large files. You can:
- Use smaller audio files for testing
- Adjust thresholds to reduce the number of detected points

## Development

### Adding New Features
1. Edit `advanced_detector.py` for core logic
2. Update `gui_detector.py` for GUI support
3. Update `requirements.txt` for new dependencies
4. Update `README.md` for documentation

### Testing
```bash
# Test basic functionality
python advanced_detector.py test.mp3 --funscript test.funscript

# Test GUI
python gui_detector.py
```

## License

MIT License

## Contributing

Feel free to submit issues and pull requests to improve this project!

## Changelog

### v1.0.0
- Initial release
- Support for audio and video files
- GUI interface
- Funscript export
- Progress bar and visualization support 