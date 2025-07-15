# YTV Downloader

A YouTube video downloader for Windows, built with Python, [customtkinter](https://github.com/TomSchimansky/CustomTkinter), [yt-dlp](https://github.com/yt-dlp/yt-dlp), and [Pillow](https://python-pillow.org/).

## Features
- Download both video and audio from YouTube
- Choose video/audio quality
- Select download folder
- Nice UI with dark mode toggle

## Setup
1. **Clone the repository** (if using git):
   ```sh
   git clone <your-repo-url>
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
   pip install yt-dlp customtkinter pillow
   ```

## Usage
1. Run the application:
   ```sh
   python main.py
   ```
2. Paste a YouTube URL, fetch video info, select quality, choose a download folder, and click Download.
3. Toggle dark/light mode with the button at the bottom.

## Packaging as .exe
1. Make sure your virtual environment is activated and dependencies are installed.
2. Install PyInstaller:
   ```sh
   pip install pyinstaller
   ```
3. Build the executable:
   ```sh
   pyinstaller --onefile --noconsole --add-data "venv\Lib\site-packages\customtkinter;customtkinter" main.py
   ```
   - The `.exe` will be in the `dist` folder.
   - You may need to adjust the `--add-data` path depending on your environment.

## Notes
- For best results, always use the latest version of `yt-dlp`.
- This app is for personal use. Please respect YouTube's Terms of Service. 