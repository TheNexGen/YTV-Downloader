import sys
import os
# Add Tools directory to PATH before importing yt_dlp
TOOLS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Tools')
os.environ["PATH"] += os.pathsep + TOOLS_PATH
import threading
import yt_dlp
import requests
import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QFileDialog, QHBoxLayout, QVBoxLayout, QMenuBar, QMessageBox, QCheckBox,
    QProgressBar, QFrame, QGridLayout, QSizePolicy, QScrollArea, QToolButton
)
from PyQt6.QtGui import QIcon, QPixmap, QFont, QAction
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtSvgWidgets import QSvgWidget

class HoverIconButton(QToolButton):
    def __init__(self, icon_path_default, icon_path_hover, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon_path_default = icon_path_default
        self.icon_path_hover = icon_path_hover
        self.setIcon(QIcon(self.icon_path_default))
        self.setMouseTracking(True)

    def enterEvent(self, event):
        self.setIcon(QIcon(self.icon_path_hover))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setIcon(QIcon(self.icon_path_default))
        super().leaveEvent(event)

class DownloadRow(QWidget):
    update_progress_signal = pyqtSignal(int, str, str, str, str)
    # percent, percent_text, speed_str, size_str, eta_str

    def __init__(self, thumb_pixmap, title, fmt, res_or_bitrate, time_started, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(60)
        self.setStyleSheet("QWidget { background: transparent; }")
        layout = QGridLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)
        
        # Thumbnail (64px)
        if thumb_pixmap:
            self.thumb_label = QLabel()
            self.thumb_label.setPixmap(thumb_pixmap.scaled(64, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            layout.addWidget(self.thumb_label, 0, 0, 2, 1)
        else:
            self.thumb_label = QLabel()
            self.thumb_label.setFixedSize(64, 36)
            layout.addWidget(self.thumb_label, 0, 0, 2, 1)
        
        # Top row
        self.title_label = QLabel(title)
        self.title_label.setFixedWidth(180)  # Reduced from 220
        layout.addWidget(self.title_label, 0, 1)
        
        self.res_label = QLabel(res_or_bitrate)
        self.res_label.setFixedWidth(60)  # Reduced from 70
        layout.addWidget(self.res_label, 0, 2)
        
        self.percent_label = QLabel("0%")
        self.percent_label.setFixedWidth(35)  # Reduced from 40
        layout.addWidget(self.percent_label, 0, 4)
        
        self.status_label = QLabel("Queued")
        self.status_label.setFixedWidth(60)  # Reduced from 70
        layout.addWidget(self.status_label, 0, 5)
        
        # Bottom row
        self.speed_label = QLabel("0 KB/s")
        self.speed_label.setFixedWidth(80)  # Reduced from 100
        layout.addWidget(self.speed_label, 1, 1)
        
        self.size_label = QLabel("0 MB / 0 MB")
        self.size_label.setFixedWidth(100)  # Reduced from 120
        layout.addWidget(self.size_label, 1, 2)
        
        self.eta_label = QLabel("ETA: -")
        self.eta_label.setFixedWidth(70)  # Reduced from 80
        layout.addWidget(self.eta_label, 1, 3)
        
        self.time_label = QLabel(time_started)
        self.time_label.setFixedWidth(70)  # Reduced from 80
        layout.addWidget(self.time_label, 1, 4)
        
        # Icon buttons (32px each)
        self.cancel_btn = HoverIconButton("icons/cancel_gray.svg", "icons/cancel_white.svg")
        self.cancel_btn.setToolTip("Cancel")
        self.cancel_btn.setFixedSize(32, 32)
        self.cancel_btn.setEnabled(True)
        layout.addWidget(self.cancel_btn, 1, 5)
        
        self.retry_btn = HoverIconButton("icons/retry_gray.svg", "icons/retry_white.svg")
        self.retry_btn.setToolTip("Retry")
        self.retry_btn.setFixedSize(32, 32)
        self.retry_btn.setEnabled(False)
        layout.addWidget(self.retry_btn, 1, 6)
        
        self.open_btn = HoverIconButton("icons/folder_gray.svg", "icons/folder_white.svg")
        self.open_btn.setToolTip("Open Folder")
        self.open_btn.setFixedSize(32, 32)
        self.open_btn.setEnabled(False)
        layout.addWidget(self.open_btn, 1, 7)
        
        # Style the icon buttons
        for btn in [self.cancel_btn, self.retry_btn, self.open_btn]:
            btn.setStyleSheet("""
                QToolButton {
                    border: none;
                    background: transparent;
                    color: #ffffff;
                    padding: 0px;
                }
                QToolButton:hover {
                    background: transparent;
                    color: #ffffff;
                }
                QToolButton:pressed {
                    background: transparent;
                    color: #cccccc;
                }
                QToolButton:disabled {
                    background: transparent;
                    color: #888888;
                }
            """)
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.setColumnStretch(8, 1)  # Add stretch at the end to prevent squishing
        self.setLayout(layout)
        self.update_progress_signal.connect(self.update_progress)

    def update_progress(self, percent, percent_text, speed_str, size_str, eta_str):
        if speed_str.startswith("Speed: "):
            speed_str = speed_str.replace("Speed: ", "")
        self.percent_label.setText(percent_text)
        self.speed_label.setText(speed_str)
        self.size_label.setText(size_str)
        self.status_label.setText("Downloading")
        self.eta_label.setText(eta_str)

class YouTubeDownloaderApp(QMainWindow):
    download_row_requested = pyqtSignal(object, str, str, str, str, str, str, str, object)
    # args: thumb_pixmap, title, fmt, res_or_bitrate, time_started, url, folder, format_text, info

    def __init__(self):
        super().__init__()
        self.setWindowTitle("YTV Downloader beta")
        self.setWindowIcon(QIcon("ytdownloadlogo.ico"))
        self.resize(700, 600)
        self.download_folder = os.path.expanduser("~")
        self.active_download_rows = []
        self.init_ui()
        self.set_dark_mode(True)  # Set dark mode by default
        self.download_row_requested.connect(self._add_download_row)

    def init_ui(self):
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("Settings")
        settings_action = QAction("Preferences", self)
        settings_action.triggered.connect(self.placeholder_command)
        settings_menu.addAction(settings_action)

        # Add Help menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        top_layout = QHBoxLayout()
        self.title_label = QLabel("YTV Downloader")
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        top_layout.addWidget(self.title_label)
        top_layout.addStretch()
        self.theme_switch = QCheckBox("Dark Mode")
        self.theme_switch.setChecked(True)
        self.theme_switch.stateChanged.connect(self.toggle_mode)
        top_layout.addWidget(self.theme_switch)
        main_layout.addLayout(top_layout)

        columns_layout = QHBoxLayout()
        main_layout.addLayout(columns_layout, 1)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        columns_layout.addWidget(left_panel, 1)

        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText(" Paste YouTube video URL here...")
        left_layout.addWidget(self.url_entry)

        self.format_options = [
            "Audio: MP3", "Audio: M4A", "Audio: WEBM", "Audio: AAC", "Audio: FLAC", "Audio: OPUS", "Audio: OGG", "Audio: WAV",
            "────────────",
            "Video: MP4 (144p)",
            "Video: MP4 (240p)",
            "Video: MP4 (360p)",
            "Video: MP4 (480p)",
            "Video: MP4 (720p)",
            "Video: MP4 (1080p)",
            "Video: MP4 (1440p)"
        ]
        self.format_menu = QComboBox()
        for opt in self.format_options:
            self.format_menu.addItem(opt)
        self.format_menu.setCurrentText("Video: MP4 (720p)")
        left_layout.addWidget(self.format_menu)

        self.download_btn = QPushButton("Download")
        self.download_btn.setEnabled(True)
        self.download_btn.clicked.connect(self.download_video)
        self.set_button_style(self.download_btn)
        left_layout.addWidget(self.download_btn)

        left_layout.addSpacing(10)
        # Remove QScrollArea from left panel
        # left_layout.addWidget(self.active_downloads_scroll)

        left_layout.addStretch()

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        columns_layout.addWidget(right_panel, 1)

        folder_label = QLabel("Download Folder:")
        right_layout.addWidget(folder_label)
        folder_layout = QHBoxLayout()
        self.folder_entry = QLineEdit(self.download_folder)
        folder_layout.addWidget(self.folder_entry)
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_folder)
        self.set_button_style(self.browse_btn)
        folder_layout.addWidget(self.browse_btn)
        right_layout.addLayout(folder_layout)

        self.status_label = QLabel()
        right_layout.addWidget(self.status_label)
        right_layout.addStretch()

        # Add QScrollArea for download rows below the columns_layout, spanning full width
        self.active_downloads_scroll = QScrollArea()
        self.active_downloads_scroll.setWidgetResizable(True)
        self.active_downloads_scroll.setFixedHeight(150)
        self.active_downloads_widget = QWidget()
        self.active_downloads_layout = QVBoxLayout(self.active_downloads_widget)
        self.active_downloads_layout.setContentsMargins(4, 4, 4, 4)
        self.active_downloads_layout.setSpacing(6)
        self.active_downloads_scroll.setWidget(self.active_downloads_widget)
        main_layout.addWidget(self.active_downloads_scroll)

    def set_button_style(self, button):
        button.setStyleSheet("""
            QPushButton {
                background-color: #FFD600;
                color: #333333;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #FFEA00;
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #888888;
                border-radius: 8px;
            }
        """)

    def set_dark_mode(self, enabled):
        if enabled:
            self.setStyleSheet("""
                QMainWindow, QWidget { background: #232629; color: #f0f0f0; }
                QLabel, QLineEdit, QComboBox, QPushButton {
                    color: #f0f0f0;
                    background: #232629;
                }
                QPushButton { background: #FFD600; color: #333333; border-radius: 8px; }
                QPushButton:hover { background: #FFEA00; }
                QPushButton:disabled { background: #e0e0e0; color: #888888; border-radius: 8px; }
                QLineEdit, QComboBox { background: #333; border: 1px solid #888; border-radius: 8px; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget { background: #fafafa; color: #222; }
                QLabel, QLineEdit, QComboBox, QPushButton {
                    color: #222;
                    background: #fafafa;
                }
                QPushButton { background: #FFD600; color: #333333; border-radius: 8px; }
                QPushButton:hover { background: #FFEA00; }
                QPushButton:disabled { background: #e0e0e0; color: #888888; border-radius: 8px; }
                QLineEdit, QComboBox { background: #fff; border: 1px solid #ccc; border-radius: 8px; }
            """)

    def toggle_mode(self):
        self.set_dark_mode(self.theme_switch.isChecked())

    def download_video(self):
        url = self.url_entry.text().strip()
        folder = self.folder_entry.text().strip()
        format_text = self.format_menu.currentText()
        if not url:
            self.status_label.setText("Please enter a YouTube URL.")
            return
        if not folder or not os.path.isdir(folder):
            self.status_label.setText("Please select a valid download folder.")
            return
        self.status_label.setText("")
        self.download_btn.setEnabled(False)
        self.url_entry.clear()
        threading.Thread(target=self._prepare_download_row, args=(url, folder, format_text), daemon=True).start()

    def _prepare_download_row(self, url, folder, format_text):
        print("_prepare_download_row called with:", url, folder, format_text)
        ydl_opts = {"quiet": True, "skip_download": True}
        info = None
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            print("Video info fetched:", info.get('title', 'N/A'))
        except Exception as e:
            print("Exception in _prepare_download_row:", e)
            def update():
                self.status_label.setText(f"Error: {e}")
                self.download_btn.setEnabled(True)
                QMessageBox.critical(self, "Error", f"Failed to fetch video info.\n{e}")
            QTimer.singleShot(0, update)
            return
        title = info.get('title', 'N/A')
        fmt = format_text
        res_or_bitrate = self._get_res_or_bitrate(info, format_text)
        thumb_url = info.get('thumbnail')
        thumb_pixmap = None
        if thumb_url:
            try:
                resp = requests.get(thumb_url)
                img_data = resp.content
                thumb_pixmap = QPixmap()
                thumb_pixmap.loadFromData(img_data)
            except Exception:
                thumb_pixmap = None
        time_started = datetime.datetime.now().strftime("%H:%M:%S")
        self.download_row_requested.emit(thumb_pixmap, title, fmt, res_or_bitrate, time_started, url, folder, format_text, info)

    def _add_download_row(self, thumb_pixmap, title, fmt, res_or_bitrate, time_started, url, folder, format_text, info):
        print("_add_download_row called: creating DownloadRow and starting download thread")
        row = DownloadRow(thumb_pixmap, title, fmt, res_or_bitrate, time_started)
        row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.active_download_rows.append(row)
        self.active_downloads_layout.addWidget(row)
        self._start_download_thread(url, folder, format_text, row, info)

    def _get_res_or_bitrate(self, info, format_text):
        if format_text.startswith("Audio: "):
            audio_format = format_text.replace("Audio: ", "")
            return f"{audio_format}"
        elif format_text.startswith("Video: "):
            if "(" in format_text and ")" in format_text:
                resolution = format_text.split("(")[-1].replace(")", "")
                return f"{resolution}"
            return "-"
        return "-"

    def _start_download_thread(self, url, folder, format_text, row_widget, info):
        print("_start_download_thread called")
        threading.Thread(target=self._download_thread, args=(url, folder, format_text, row_widget, info), daemon=True).start()

    def _download_thread(self, url, folder, format_text, row_widget, info):
        print("_download_thread called")
        format_map = {
            "Audio: MP3": "bestaudio[ext=mp3]",
            "Audio: M4A": "bestaudio[ext=m4a]",
            "Audio: WEBM": "bestaudio[ext=webm]",
            "Audio: AAC": "bestaudio[ext=aac]",
            "Audio: FLAC": "bestaudio[ext=flac]",
            "Audio: OPUS": "bestaudio[ext=opus]",
            "Audio: OGG": "bestaudio[ext=ogg]",
            "Audio: WAV": "bestaudio[ext=wav]",
            "Video: MP4 (144p)": "bestvideo[ext=mp4][height<=144]+bestaudio[ext=m4a]/best[ext=mp4][height<=144]",
            "Video: MP4 (240p)": "bestvideo[ext=mp4][height<=240]+bestaudio[ext=m4a]/best[ext=mp4][height<=240]",
            "Video: MP4 (360p)": "bestvideo[ext=mp4][height<=360]+bestaudio[ext=m4a]/best[ext=mp4][height<=360]",
            "Video: MP4 (480p)": "bestvideo[ext=mp4][height<=480]+bestaudio[ext=m4a]/best[ext=mp4][height<=480]",
            "Video: MP4 (720p)": "bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]",
            "Video: MP4 (1080p)": "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4][height<=1080]",
            "Video: MP4 (1440p)": "bestvideo[ext=mp4][height<=1440]+bestaudio[ext=m4a]/best[ext=mp4][height<=1440]",
        }
        ydl_format = format_map.get(format_text, "best")
        outtmpl = os.path.join(folder, "%(title)s.%(ext)s")
        ffmpeg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Tools', 'ffmpeg.exe')
        print("FFmpeg path used:", ffmpeg_path)  # Debug print
        try:
            print("_download_thread: starting yt_dlp download")
            def progress_hook(d):
                print("Progress hook called:", d.get('status'), d.get('downloaded_bytes', 0), d.get('total_bytes', 0))
                if d['status'] == 'downloading':
                    total = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
                    downloaded = d.get('downloaded_bytes', 0)
                    percent = downloaded / total
                    speed = d.get('speed', 0)
                    speed_str = f"{speed/1024:.1f} KB/s" if speed else "Speed: -"
                    size_str = f"{downloaded/1024/1024:.2f} MB / {total/1024/1024:.2f} MB"
                    eta = d.get('eta', None)
                    print(f"Progress: {int(percent*100)}%, Speed: {speed_str}, Size: {size_str}")
                    # Use signal to update UI
                    row_widget.update_progress_signal.emit(
                        int(percent*100),
                        f"{int(percent*100)}%",
                        speed_str,
                        size_str,
                        f"ETA: {eta}s" if eta is not None else "ETA: -"
                    )
                elif d['status'] == 'finished':
                    print("Download finished, merging...")
                    def update():
                        row_widget.status_label.setText("Merging")
                        row_widget.eta_label.setText("ETA: -")
                    QTimer.singleShot(0, update)
            ydl_opts = {
                'format': ydl_format,
                'outtmpl': outtmpl,
                'progress_hooks': [progress_hook],
                'quiet': True,
                'noplaylist': True,
                'merge_output_format': None,
                'ffmpeg_location': ffmpeg_path,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            def update():
                row_widget.status_label.setText("Complete")
                row_widget.open_btn.setEnabled(True)
                row_widget.cancel_btn.setEnabled(False)
                row_widget.retry_btn.setEnabled(False)
                self.download_btn.setEnabled(True)
            QTimer.singleShot(0, update)
        except Exception as e:
            print("Exception in _download_thread:", e)
            def update():
                row_widget.status_label.setText("Error")
                row_widget.retry_btn.setEnabled(True)
                row_widget.open_btn.setEnabled(False)
                row_widget.cancel_btn.setEnabled(False)
                self.download_btn.setEnabled(True)
            QTimer.singleShot(0, update)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", self.download_folder)
        if folder:
            self.download_folder = folder
            self.folder_entry.setText(folder)

    def placeholder_command(self):
        QMessageBox.information(self, "Info", "This feature is not yet implemented.")

    def show_about_dialog(self):
        QMessageBox.information(self, "About YTV Downloader", "YTV Downloader beta\nA modern YouTube video downloader built with PyQt6.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = YouTubeDownloaderApp()
    window.show()
    sys.exit(app.exec()) 