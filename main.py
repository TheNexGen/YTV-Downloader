import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, Menu
from PIL import Image, ImageTk
import requests
import io
import threading
import yt_dlp
import os
import datetime
import re

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.iconbitmap("ytdownloadlogo.ico")
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
        settings_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Preferences", command=self.placeholder_command)
        self.menubar = menubar

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.top_frame = ctk.CTkFrame(self, corner_radius=0)
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.top_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self.top_frame, text="YouTube Video Downloader", font=("Arial", 20, "bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.theme_switch = ctk.CTkSwitch(self.top_frame, text="Light/Dark", command=self.toggle_mode)
        self.theme_switch.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        self.theme_switch.select()

        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=1, column=0, padx=(5, 10), pady=10, sticky='nsew')
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(0, weight=0)
        self.left_frame.grid_rowconfigure(1, weight=0)

        self.format_options = [
            "Audio: MP3", "Audio: M4A", "Audio: WEBM", "Audio: AAC", "Audio: FLAC", "Audio: OPUS", "Audio: OGG", "Audio: WAV",
            "────────────",
            "Video: MP4 (144p)", "Video: MP4 (240p)", "Video: MP4 (360p)", "Video: MP4 (480p)", "Video: MP4 (720p)", "Video: MP4 (1080p)", "Video: MP4 (1440p)", "Video: WEBM (4K)"
        ]

        self.url_format_frame = ctk.CTkFrame(self.left_frame)
        self.url_format_frame.grid(row=0, column=0, padx=10, pady=(10, 2), sticky="ew")
        self.url_format_frame.grid_columnconfigure(0, weight=3)
        self.url_format_frame.grid_columnconfigure(1, weight=2)

        self.url_entry = ctk.CTkEntry(self.url_format_frame, placeholder_text="Paste YouTube video URL here...")
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0,10))

        self.format_menu = ctk.CTkOptionMenu(self.url_format_frame, variable=self.selected_format_option, values=self.format_options, fg_color="#FFD600", button_color="#FFD600", button_hover_color="#FFEA00", text_color="#333333")
        self.format_menu.grid(row=0, column=1, sticky="ew")

        self.download_btn = ctk.CTkButton(self.left_frame, text="Fetch Video Info", command=self.fetch_video_info, state="normal", fg_color="#FFD600", hover_color="#FFEA00", text_color="#333333")
        self.download_btn.grid(row=1, column=0, padx=10, pady=(2, 2), sticky="ew")

        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=1, column=1, padx=(5, 10), pady=10, sticky='new')
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=0)
        self.right_frame.grid_rowconfigure(1, weight=0)
        self.right_frame.grid_rowconfigure(2, weight=0)

        self.config_frame = ctk.CTkFrame(self.right_frame)
        self.config_frame.grid(row=1, column=0, padx=0, pady=(2, 2), sticky="ew")
        self.config_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.config_frame, text="Download Folder:").grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        self.folder_entry = ctk.CTkEntry(self.config_frame, textvariable=self.download_folder)
        self.folder_entry.grid(row=1, column=0, padx=(10,5), pady=5, sticky="ew")
        self.browse_btn = ctk.CTkButton(self.config_frame, text="Browse", command=self.browse_folder, width=80, fg_color="#FFD600", hover_color="#FFEA00", text_color="#333333")
        self.browse_btn.grid(row=1, column=1, padx=(0,10), pady=5)

        self.download_frame = ctk.CTkFrame(self.right_frame)
        self.download_frame.grid(row=2, column=0, padx=0, pady=5, sticky="ew")
        self.download_frame.grid_columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(self.download_frame, fg_color="#FFF9C4", progress_color="#FFD600")
        self.progress.set(0)
        self.progress.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.status_label = ctk.CTkLabel(self.download_frame, text="")
        self.status_label.grid(row=2, column=0, columnspan=3, padx=10, pady=5)

        self.active_downloads_frame = ctk.CTkFrame(self)
        self.active_downloads_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(2, 10), sticky="nsew")
        self.active_download_rows = {}

    def fetch_video_info(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return

        self.status_label.configure(text="Fetching video info...")
        self.download_btn.configure(state="disabled")
        threading.Thread(target=self._fetch_info_thread, args=(url,), daemon=True).start()

    def _fetch_info_thread(self, url):
        ydl_opts = {"quiet": True, "skip_download": True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            self.video_info = info
            self.status_label.configure(text=f"Fetched: {info.get('title', 'N/A')}")
            self.download_btn.configure(state="normal")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")
            messagebox.showerror("Error", f"Failed to fetch video info.\n{e}")

    def toggle_mode(self):
        if self.dark_mode:
            ctk.set_appearance_mode("Light")
            self.dark_mode = False
        else:
            ctk.set_appearance_mode("Dark")
            self.dark_mode = True

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_folder.set(folder)

    def placeholder_command(self):
        messagebox.showinfo("Info", "This feature is not yet implemented.")

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
