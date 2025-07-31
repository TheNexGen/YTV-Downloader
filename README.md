# YTV Downloader

A modern YouTube video downloader for Windows, built with Python, [PyQt6](https://www.riverbankcomputing.com/software/pyqt/), [yt-dlp](https://github.com/yt-dlp/yt-dlp), and [Pillow](https://python-pillow.org/).

## Features
- Download both video and audio from YouTube
- Choose video/audio quality and format
- Select download folder
- Modern UI with dark mode toggle
- Concurrent downloads with progress tracking
- Video thumbnails and detailed progress information
- Automatic FFmpeg integration

## Download

### Latest Release
Download the latest release from the [Releases](https://github.com/yourusername/Video-Downloader/releases) page.

### System Requirements
- Windows 10 or later
- No additional software required (FFmpeg is bundled)

## Installation

### Option 1: Download Executable (Recommended)
1. Go to the [Releases](https://github.com/yourusername/Video-Downloader/releases) page
2. Download the latest `YTV-Downloader.exe`
3. Run the executable - no installation required!

### Option 2: Build from Source
1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/Video-Downloader.git
   cd Video-Downloader
   ```

2. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```sh
   python main.py
   ```

## Usage
1. Launch the application
2. Paste a YouTube URL in the text box
3. Select your desired format (video quality or audio format)
4. Choose a download folder (optional - defaults to Downloads)
5. Click "Download" to start
6. Monitor progress in the download cards at the bottom
7. Use the dark mode toggle for your preferred theme

## Building Executable

### Automated Build
Run the build script:
```sh
python build.py
```
The executable will be created in the `release` directory.

### Manual Build
1. Install PyInstaller:
   ```sh
   pip install pyinstaller
   ```

2. Build using the spec file:
   ```sh
   pyinstaller main.spec
   ```

## Development

### Project Structure
```
Video-Downloader/
├── main.py              # Main application
├── main.spec            # PyInstaller configuration
├── build.py             # Build script
├── requirements.txt     # Python dependencies
├── Tools/
│   └── ffmpeg.exe      # Bundled FFmpeg
├── icons/              # Application icons
└── .github/workflows/  # GitHub Actions
```

### Adding New Features
1. Make your changes to `main.py`
2. Test thoroughly
3. Update version in `build.py` if needed
4. Create a new release tag:
   ```sh
   git tag v1.0.1
   git push origin v1.0.1
   ```

## Notes
- For best results, always use the latest version of `yt-dlp`
- This app is for personal use. Please respect YouTube's Terms of Service
- FFmpeg is bundled with the application for video processing
- The application saves your download folder preference in `config.json`

## License
[Add your license here]

## Contributing
[Add contribution guidelines here] 