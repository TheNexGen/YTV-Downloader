<img width="1928" height="602" alt="YTVbannerv1" src="https://github.com/user-attachments/assets/51bec522-b4b9-4ddc-83b9-557ed9f8bdda" />

## YTV Downloader

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
Download the latest release from the [Releases](https://github.com/TheNexGen/Video-Downloader/releases) page.

### System Requirements
- Windows 10 or later
- No additional software required (FFmpeg is bundled)

## Installation

### Download Executable
1. Go to the [Releases](https://github.com/TheNexGen/Video-Downloader/releases) page
2. Download the latest `YTV-Downloader.exe`
3. Run the executable - no installation required!


## Usage
1. Launch the application
2. Paste a YouTube URL in the text box
3. Select your desired format (video quality or audio format)
4. Choose a download folder (optional - defaults to Downloads)
5. Click "Download" to start
6. Monitor progress in the download cards at the bottom
7. Use the dark mode toggle for your preferred theme


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


