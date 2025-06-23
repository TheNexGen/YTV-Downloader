import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import requests
import io
import threading
import yt_dlp

ctk.set_appearance_mode("System")  # Start with system mode
ctk.set_default_color_theme("blue")

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Video Downloader")
        self.geometry("600x700")
        self.resizable(False, False)
        self.video_info = None
        self.thumbnail_img = None
        self.download_folder = tk.StringVar(value="")
        self.quality_options = []
        self.selected_quality = tk.StringVar(value="")
        self.dark_mode = True
        self.create_widgets()

    def create_widgets(self):
        # Title
        self.title_label = ctk.CTkLabel(self, text="YouTube Video Downloader", font=("Arial", 24, "bold"))
        self.title_label.pack(pady=(20, 10))

        # URL Entry
        self.url_entry = ctk.CTkEntry(self, width=400, placeholder_text="Paste YouTube video URL here...")
        self.url_entry.pack(pady=(10, 5))

        # Fetch Info Button
        self.fetch_btn = ctk.CTkButton(self, text="Fetch Video Info", command=self.fetch_video_info)
        self.fetch_btn.pack(pady=(5, 10))

        # Thumbnail
        self.thumbnail_label = ctk.CTkLabel(self, text="", width=320, height=180)
        self.thumbnail_label.pack(pady=(10, 5))

        # Video Info
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(pady=(5, 10), fill="x", padx=40)
        self.title_info = ctk.CTkLabel(self.info_frame, text="", font=("Arial", 14, "bold"), wraplength=400, justify="left")
        self.title_info.pack(anchor="w", pady=(5, 0))
        self.author_info = ctk.CTkLabel(self.info_frame, text="", font=("Arial", 12), wraplength=400, justify="left")
        self.author_info.pack(anchor="w")
        self.length_info = ctk.CTkLabel(self.info_frame, text="", font=("Arial", 12), wraplength=400, justify="left")
        self.length_info.pack(anchor="w")

        # Quality Selection
        self.quality_label = ctk.CTkLabel(self, text="Select Quality:")
        self.quality_label.pack(pady=(10, 0))
        self.quality_menu = ctk.CTkOptionMenu(self, variable=self.selected_quality, values=[])
        self.quality_menu.pack(pady=(0, 10))

        # Download Folder
        self.folder_frame = ctk.CTkFrame(self)
        self.folder_frame.pack(pady=(5, 10), fill="x", padx=40)
        self.folder_label = ctk.CTkLabel(self.folder_frame, text="Download Folder:")
        self.folder_label.pack(side="left", padx=(0, 10))
        self.folder_entry = ctk.CTkEntry(self.folder_frame, textvariable=self.download_folder, width=250)
        self.folder_entry.pack(side="left", padx=(0, 10))
        self.folder_btn = ctk.CTkButton(self.folder_frame, text="Browse", command=self.browse_folder, width=80)
        self.folder_btn.pack(side="left")

        # Download Button
        self.download_btn = ctk.CTkButton(self, text="Download", command=self.start_download, state="disabled")
        self.download_btn.pack(pady=(10, 5))

        # Progress Bar
        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.set(0)
        self.progress.pack(pady=(10, 5))

        # Status Label
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.status_label.pack(pady=(5, 10))

        # Dark Mode Toggle
        self.toggle_btn = ctk.CTkButton(self, text="Toggle Dark/Light Mode", command=self.toggle_mode)
        self.toggle_btn.pack(pady=(10, 10))

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
            self.show_video_info(info)
            self.status_label.configure(text="Video info loaded.")
            self.download_btn.configure(state="normal")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")
            messagebox.showerror("Error", f"Failed to fetch video info.\n{e}")

    def show_video_info(self, info):
        # Thumbnail
        thumb_url = info.get("thumbnail")
        if thumb_url:
            try:
                response = requests.get(thumb_url)
                img_data = response.content
                img = Image.open(io.BytesIO(img_data)).resize((320, 180))
                self.thumbnail_img = ImageTk.PhotoImage(img)
                self.thumbnail_label.configure(image=self.thumbnail_img, text="")
            except Exception:
                self.thumbnail_label.configure(text="[Thumbnail not available]", image=None)
        else:
            self.thumbnail_label.configure(text="[Thumbnail not available]", image=None)
        # Info
        self.title_info.configure(text=f"Title: {info.get('title', 'N/A')}")
        self.author_info.configure(text=f"Channel: {info.get('uploader', 'N/A')}")
        mins, secs = divmod(info.get('duration', 0), 60)
        self.length_info.configure(text=f"Length: {mins}m {secs}s")
        # Quality options
        formats = info.get('formats', [])
        options = []
        for f in formats:
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                label = f"Video+Audio | {f.get('format_note', '')} | {f.get('ext', '')} | {f.get('filesize', 0)//1024//1024}MB"
            elif f.get('vcodec') != 'none':
                label = f"Video Only | {f.get('format_note', '')} | {f.get('ext', '')} | {f.get('filesize', 0)//1024//1024}MB"
            elif f.get('acodec') != 'none':
                label = f"Audio Only | {f.get('abr', '')}kbps | {f.get('ext', '')} | {f.get('filesize', 0)//1024//1024}MB"
            else:
                continue
            options.append(label)
        self.quality_options = options
        if options:
            self.quality_menu.configure(values=options)
            self.selected_quality.set(options[0])
        else:
            self.quality_menu.configure(values=["No formats found"])
            self.selected_quality.set("No formats found")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_folder.set(folder)

    def start_download(self):
        if not self.video_info:
            messagebox.showerror("Error", "No video info loaded.")
            return
        if not self.download_folder.get():
            messagebox.showerror("Error", "Please select a download folder.")
            return
        self.status_label.configure(text="Starting download...")
        self.progress.set(0)
        self.download_btn.configure(state="disabled")
        threading.Thread(target=self._download_thread, daemon=True).start()

    def _download_thread(self):
        url = self.url_entry.get().strip()
        selected = self.selected_quality.get()
        # Find the format code
        format_id = None
        for f in self.video_info.get('formats', []):
            label = ""
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                label = f"Video+Audio | {f.get('format_note', '')} | {f.get('ext', '')} | {f.get('filesize', 0)//1024//1024}MB"
            elif f.get('vcodec') != 'none':
                label = f"Video Only | {f.get('format_note', '')} | {f.get('ext', '')} | {f.get('filesize', 0)//1024//1024}MB"
            elif f.get('acodec') != 'none':
                label = f"Audio Only | {f.get('abr', '')}kbps | {f.get('ext', '')} | {f.get('filesize', 0)//1024//1024}MB"
            if label == selected:
                format_id = f.get('format_id')
                break
        ydl_opts = {
            'format': format_id if format_id else 'best',
            'outtmpl': f"{self.download_folder.get()}/%(title)s.%(ext)s",
            'progress_hooks': [self.yt_progress_hook],
            'quiet': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status_label.configure(text="Download complete!")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")
            messagebox.showerror("Error", f"Download failed.\n{e}")
        self.download_btn.configure(state="normal")

    def yt_progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
            downloaded = d.get('downloaded_bytes', 0)
            percent = downloaded / total
            self.progress.set(percent)
            self.status_label.configure(text=f"Downloading... {int(percent*100)}%")
        elif d['status'] == 'finished':
            self.progress.set(1)
            self.status_label.configure(text="Processing...")

    def toggle_mode(self):
        if self.dark_mode:
            ctk.set_appearance_mode("Light")
            self.dark_mode = False
        else:
            ctk.set_appearance_mode("Dark")
            self.dark_mode = True

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop() 