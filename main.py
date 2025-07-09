import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, Menu
from PIL import Image, ImageTk
import requests
import io
import threading
import yt_dlp
import os
import concurrent.futures
import datetime
import re

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Video Downloader")
        self.geometry("1000x750")
        self.minsize(600, 500)

        self.video_info = None
        self.thumbnail_img = None
        self.download_folder = tk.StringVar(value="")
        self.selected_format_option = tk.StringVar(value="Video: MP4 (720p)")
        self.dark_mode = True

        self.menubar = None
        self.create_widgets()
        self.create_menu_bar()
        self.config(menu=self.menubar)




    def create_menu_bar(self):
        menubar = Menu(self)

<<<<<<< HEAD
        # Only Settings Menu
        settings_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Preferences", command=self.placeholder_command)
=======
        # File Menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add New Download", accelerator="Ctrl+N", command=self.placeholder_command)
        file_menu.add_command(label="Import from File/Playlist", command=self.placeholder_command)
        file_menu.add_command(label="Export Download List", command=self.placeholder_command)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        # Edit Menu
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Preferences/Settings", command=self.placeholder_command)
        edit_menu.add_command(label="Clear Download History", command=self.placeholder_command)
        edit_menu.add_separator()
        edit_menu.add_command(label="Reset to Defaults", command=self.placeholder_command)

        # View Menu
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Dark/Light Mode", command=self.toggle_mode)
        view_menu.add_command(label="Show/Hide Download Queue", command=self.placeholder_command)
        view_menu.add_command(label="Show Logs / Output Console", command=self.placeholder_command)
        view_menu.add_separator()
        view_menu.add_command(label="Fullscreen Mode", command=self.toggle_fullscreen)

        # Tools Menu
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Batch Downloader", command=self.placeholder_command)
        tools_menu.add_command(label="Audio Extractor", command=self.placeholder_command)
        tools_menu.add_command(label="File Format Converter", command=self.placeholder_command)
        tools_menu.add_command(label="Subtitle Downloader", command=self.placeholder_command)
        tools_menu.add_separator()
        tools_menu.add_command(label="Proxy Configuration", command=self.placeholder_command)

        # Downloads Menu
        downloads_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Downloads", menu=downloads_menu)
        downloads_menu.add_command(label="Pause All Downloads", command=self.placeholder_command)
        downloads_menu.add_command(label="Resume All", command=self.placeholder_command)
        downloads_menu.add_command(label="Cancel All", command=self.placeholder_command)
        downloads_menu.add_separator()
        downloads_menu.add_command(label="Open Download Folder", command=self.browse_folder)
        downloads_menu.add_command(label="Retry Failed Downloads", command=self.placeholder_command)

        # Help Menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.placeholder_command)
        help_menu.add_command(label="Check for Updates", command=self.placeholder_command)
        help_menu.add_command(label="Report a Bug", command=self.placeholder_command)
        help_menu.add_separator()
        help_menu.add_command(label="About This App", command=self.show_about)
>>>>>>> 42b8eea8ac877e1e749d4e503063c21e5b6f51f8

        self.menubar = menubar

    # Removed menu bar show/hide logic; menu bar is always visible

    def create_widgets(self):
        # Main grid layout: let both cards fill 50% of the row and expand vertically
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        # --- Top Bar ---
        self.top_frame = ctk.CTkFrame(self, corner_radius=0)
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.top_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self.top_frame, text="YouTube Video Downloader", font=("Arial", 20, "bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.theme_switch = ctk.CTkSwitch(self.top_frame, text="Light/Dark", command=self.toggle_mode)
        self.theme_switch.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        self.theme_switch.select()
        # Removed menu bar toggle button; menu bar is always visible

        # --- Left Column: Input and Video Info ---
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=1, column=0, padx=(5, 10), pady=10, sticky='nsew')
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(0, weight=0)
        self.left_frame.grid_rowconfigure(1, weight=0)

        # Single dropdown for both audio and video options
        self.format_options = [
            "Audio: MP3", "Audio: M4A", "Audio: WEBM", "Audio: AAC", "Audio: FLAC", "Audio: OPUS", "Audio: OGG", "Audio: WAV",
            "────────────",
            "Video: MP4 (144p)", "Video: MP4 (240p)", "Video: MP4 (360p)", "Video: MP4 (480p)", "Video: MP4 (720p)", "Video: MP4 (1080p)", "Video: MP4 (1440p)", "Video: WEBM (4K)"
        ]
        self.selected_format_option = tk.StringVar(value="Video: MP4 (720p)")

        self.url_format_frame = ctk.CTkFrame(self.left_frame)
        self.url_format_frame.grid(row=0, column=0, padx=10, pady=(10, 2), sticky="ew")
        self.url_format_frame.grid_columnconfigure(0, weight=3)
        self.url_format_frame.grid_columnconfigure(1, weight=2)

        self.url_entry = ctk.CTkEntry(self.url_format_frame, placeholder_text="Paste YouTube video URL here...")
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0,10))

        self.format_menu = ctk.CTkOptionMenu(self.url_format_frame, variable=self.selected_format_option, values=self.format_options, fg_color="#FFD600", button_color="#FFD600", button_hover_color="#FFEA00", text_color="#333333")
        self.format_menu.grid(row=0, column=1, sticky="ew")

        self.download_btn = ctk.CTkButton(self.left_frame, text="Download", command=self.start_download, state="normal", fg_color="#FFD600", hover_color="#FFEA00", text_color="#333333")
        self.download_btn.grid(row=1, column=0, padx=10, pady=(2, 2), sticky="ew")

        # --- Right Column: Download Options ---
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=1, column=1, padx=(5, 10), pady=10, sticky='new')  # Only north, east, west
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=0)
        self.right_frame.grid_rowconfigure(1, weight=0)
        self.right_frame.grid_rowconfigure(2, weight=0)

        # Download Config
        self.config_frame = ctk.CTkFrame(self.right_frame)
        self.config_frame.grid(row=1, column=0, padx=0, pady=(2, 2), sticky="ew")
        self.config_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.config_frame, text="Download Folder:").grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        self.folder_entry = ctk.CTkEntry(self.config_frame, textvariable=self.download_folder)
        self.folder_entry.grid(row=1, column=0, padx=(10,5), pady=5, sticky="ew")
        self.browse_btn = ctk.CTkButton(self.config_frame, text="Browse", command=self.browse_folder, width=80, fg_color="#FFD600", hover_color="#FFEA00", text_color="#333333")
        self.browse_btn.grid(row=1, column=1, padx=(0,10), pady=5)

        # Download Actions
        self.download_frame = ctk.CTkFrame(self.right_frame)
        self.download_frame.grid(row=2, column=0, padx=0, pady=5, sticky="ew")
        self.download_frame.grid_columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(self.download_frame, fg_color="#FFF9C4", progress_color="#FFD600")
        self.progress.set(0)
        self.progress.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        
        self.status_label = ctk.CTkLabel(self.download_frame, text="")
        self.status_label.grid(row=2, column=0, columnspan=3, padx=10, pady=5)

        # Remove the bottom tabview
        # Add a frame for active downloads at the bottom
        self.active_downloads_frame = ctk.CTkFrame(self)
        self.active_downloads_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(2, 10), sticky="nsew")
        self.active_download_rows = {}  # key: url, value: widgets

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_folder.set(folder)

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return
        if not self.download_folder.get():
            messagebox.showerror("Error", "Please select a download folder.")
            return
        # Step 7: Fetch video info (title, thumbnail, format, resolution/bitrate) before starting the download
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
            title = info.get('title', url)
            thumbnail_url = info.get('thumbnail')
            thumb_img = None
            if thumbnail_url:
                try:
                    resp = requests.get(thumbnail_url)
                    img_data = resp.content
                    img = Image.open(io.BytesIO(img_data)).resize((80, 45))
                    thumb_img = ImageTk.PhotoImage(img)
                except Exception:
                    thumb_img = None
            fmt = self.selected_format_option.get()
            res_or_bitrate = "-"
            if fmt.startswith('Video: '):
                match = re.search(r'(\d{3,4}p)', fmt)
                if match:
                    res_or_bitrate = match.group(1)
            elif fmt.startswith('Audio: '):
                abr = info.get('abr') or info.get('bitrate')
                if abr:
                    res_or_bitrate = f"{abr} kbps"
        except Exception as e:
            title = url
            thumb_img = None
            fmt = self.selected_format_option.get()
            res_or_bitrate = "-"
        # Add time started
        time_started = datetime.datetime.now().strftime('%H:%M:%S')
        row_widgets = self.create_download_row(url, title, thumb_img, fmt, res_or_bitrate, time_started)
        self.active_download_rows[url] = row_widgets
        threading.Thread(target=self._download_thread, args=(url, title, row_widgets), daemon=True).start()
        # Clear the URL entry after starting the download
        self.url_entry.delete(0, tk.END)

    def create_download_row(self, url, title, thumb_img, fmt, res_or_bitrate, time_started):
        row = len(self.active_download_rows)
        grid_row_top = row * 2
        grid_row_bottom = row * 2 + 1

        # Top row
        thumb_label = None
        if thumb_img:
            thumb_label = ctk.CTkLabel(self.active_downloads_frame, image=thumb_img, text="")
            thumb_label.image = thumb_img
            thumb_label.grid(row=grid_row_top, column=0, padx=5, pady=2, sticky="w")
        title_label = ctk.CTkLabel(self.active_downloads_frame, text=title, anchor="w", width=300)
        title_label.grid(row=grid_row_top, column=1, padx=5, pady=2, sticky="w")
        format_label = ctk.CTkLabel(self.active_downloads_frame, text=fmt, width=100)
        format_label.grid(row=grid_row_top, column=2, padx=5, pady=2)
        res_label = ctk.CTkLabel(self.active_downloads_frame, text=res_or_bitrate, width=80)
        res_label.grid(row=grid_row_top, column=3, padx=5, pady=2)
        progress = ctk.CTkProgressBar(self.active_downloads_frame, fg_color="#FFF9C4", progress_color="#FFD600", width=200)
        progress.set(0)
        progress.grid(row=grid_row_top, column=4, padx=5, pady=2, sticky="ew")
        percent_label = ctk.CTkLabel(self.active_downloads_frame, text="0%", width=50)
        percent_label.grid(row=grid_row_top, column=5, padx=5, pady=2)
        status_label = ctk.CTkLabel(self.active_downloads_frame, text="Queued", width=80)
        status_label.grid(row=grid_row_top, column=6, padx=5, pady=2)

        # Bottom row
        speed_label = ctk.CTkLabel(self.active_downloads_frame, text="Speed: 0 KB/s", width=100)
        speed_label.grid(row=grid_row_bottom, column=1, padx=5, pady=2)
        size_label = ctk.CTkLabel(self.active_downloads_frame, text="0 MB / 0 MB", width=120)
        size_label.grid(row=grid_row_bottom, column=2, padx=5, pady=2)
        eta_label = ctk.CTkLabel(self.active_downloads_frame, text="ETA: -", width=80)
        eta_label.grid(row=grid_row_bottom, column=3, padx=5, pady=2)
        time_label = ctk.CTkLabel(self.active_downloads_frame, text=time_started, width=70)
        time_label.grid(row=grid_row_bottom, column=4, padx=5, pady=2)
        cancel_btn = ctk.CTkButton(self.active_downloads_frame, text="Cancel", width=60, state="normal")
        cancel_btn.grid(row=grid_row_bottom, column=5, padx=5, pady=2)
        retry_btn = ctk.CTkButton(self.active_downloads_frame, text="Retry", width=60, state="disabled")
        retry_btn.grid(row=grid_row_bottom, column=6, padx=5, pady=2)
        open_btn = ctk.CTkButton(self.active_downloads_frame, text="Open Folder", width=90, state="disabled")
        open_btn.grid(row=grid_row_bottom, column=7, padx=5, pady=2)

        return {
            "title_label": title_label, "progress": progress, "percent_label": percent_label,
            "speed_label": speed_label, "size_label": size_label, "thumb_label": thumb_label,
            "status_label": status_label, "eta_label": eta_label, "format_label": format_label,
            "res_label": res_label, "time_label": time_label, "cancel_btn": cancel_btn,
            "retry_btn": retry_btn, "open_btn": open_btn
        }
    def _download_thread(self, url, title, row_widgets):
        row_widgets["status_label"].configure(text="Downloading")
        selected_option = self.selected_format_option.get()
        def progress_hook(d):
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
                downloaded = d.get('downloaded_bytes', 0)
                percent = downloaded / total
                row_widgets["progress"].set(percent)
                row_widgets["percent_label"].configure(text=f"{int(percent*100)}%")
                speed = d.get('speed', 0)
                speed_str = f"Speed: {speed/1024:.1f} KB/s" if speed else "Speed: -"
                row_widgets["speed_label"].configure(text=speed_str)
                size_str = f"{downloaded/1024/1024:.2f} MB / {total/1024/1024:.2f} MB"
                row_widgets["size_label"].configure(text=size_str)
                row_widgets["status_label"].configure(text="Downloading")
                eta = d.get('eta', None)
                if eta is not None:
                    row_widgets["eta_label"].configure(text=f"ETA: {eta}s")
                else:
                    row_widgets["eta_label"].configure(text="ETA: -")
            elif d['status'] == 'finished':
                row_widgets["progress"].set(1)
                row_widgets["status_label"].configure(text="Merging")
                row_widgets["eta_label"].configure(text="ETA: -")
        try:
            if selected_option.startswith("Audio: "):
                audio_format = selected_option.replace("Audio: ", "").lower()
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': f"{self.download_folder.get()}/%(title)s.%(ext)s",
                    'progress_hooks': [progress_hook],
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': audio_format,
                        'preferredquality': '192',
                    }],
                    'quiet': True,
                    'ffmpeg_location': self.ffmpeg_path,
                }
            elif selected_option.startswith("Video: "):
                video_info = selected_option.replace("Video: ", "")
                if "MP4" in video_info:
                    quality = video_info.split("(")[-1].replace(")", "")
                    height = quality.replace("p", "").replace("K", "000")
                    ydl_opts = {
                        'format': f'bestvideo[height<={height}]+bestaudio/best[height<={height}]/best',
                        'outtmpl': f"{self.download_folder.get()}/%(title)s.%(ext)s",
                        'progress_hooks': [progress_hook],
                        'quiet': True,
                        'ffmpeg_location': self.ffmpeg_path,
                    }
                elif "WEBM" in video_info:
                    ydl_opts = {
                        'format': 'bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]',
                        'outtmpl': f"{self.download_folder.get()}/%(title)s.%(ext)s",
                        'progress_hooks': [progress_hook],
                        'quiet': True,
                        'ffmpeg_location': self.ffmpeg_path,
                    }
                else:
                    ydl_opts = {
                        'format': 'best',
                        'outtmpl': f"{self.download_folder.get()}/%(title)s.%(ext)s",
                        'progress_hooks': [progress_hook],
                        'quiet': True,
                        'ffmpeg_location': self.ffmpeg_path,
                    }
            else:
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': f"{self.download_folder.get()}/%(title)s.%(ext)s",
                    'progress_hooks': [progress_hook],
                    'quiet': True,
                    'ffmpeg_location': self.ffmpeg_path,
                }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            row_widgets["status_label"].configure(text="Complete")
            row_widgets["open_btn"].configure(state="normal")
        except Exception as e:
            row_widgets["status_label"].configure(text="Error")
            row_widgets["retry_btn"].configure(state="normal")
            row_widgets["open_btn"].configure(state="disabled")
        self.download_btn.configure(state="normal")

    def toggle_mode(self):
        if self.dark_mode:
            ctk.set_appearance_mode("Light")
            self.dark_mode = False
        else:
            ctk.set_appearance_mode("Dark")
            self.dark_mode = True
        self.apply_menu_theme()


    def toggle_fullscreen(self):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    def show_about(self):
        messagebox.showinfo("About YouTube Downloader", "Version: 1.0\nCreated with CustomTkinter")

    def placeholder_command(self):
        messagebox.showinfo("Info", "This feature is not yet implemented.")

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()