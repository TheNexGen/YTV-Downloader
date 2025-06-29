import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, Menu
from PIL import Image, ImageTk
import requests
import io
import threading
import yt_dlp

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.iconbitmap("ytdownloadlogo.ico")  # For .ico files (best for Windows)
        self.title("YouTube Video Downloader")
        self.geometry("1000x750")
        self.minsize(600, 500)

        self.video_info = None
        self.thumbnail_img = None
        self.download_folder = tk.StringVar(value="")
        self.selected_quality = tk.StringVar()
        self.selected_format = tk.StringVar()
        self.dark_mode = True

        self.create_menu()
        self.create_widgets()

    def create_menu(self):
        menubar = Menu(self)
        self.config(menu=menubar)

        # --- File Menu ---
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add New Download", accelerator="Ctrl+N", command=self.placeholder_command)
        file_menu.add_command(label="Import from File/Playlist", command=self.placeholder_command)
        file_menu.add_command(label="Export Download List", command=self.placeholder_command)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        # --- Edit Menu ---
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Preferences/Settings", command=self.placeholder_command)
        edit_menu.add_command(label="Clear Download History", command=self.placeholder_command)
        edit_menu.add_separator()
        edit_menu.add_command(label="Reset to Defaults", command=self.placeholder_command)

        # --- View Menu ---
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Dark/Light Mode", command=self.toggle_mode)
        view_menu.add_command(label="Show/Hide Download Queue", command=self.placeholder_command)
        view_menu.add_command(label="Show Logs / Output Console", command=self.placeholder_command)
        view_menu.add_separator()
        view_menu.add_command(label="Fullscreen Mode", command=self.toggle_fullscreen)

        # --- Tools Menu ---
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Batch Downloader", command=self.placeholder_command)
        tools_menu.add_command(label="Audio Extractor", command=self.placeholder_command)
        tools_menu.add_command(label="File Format Converter", command=self.placeholder_command)
        tools_menu.add_command(label="Subtitle Downloader", command=self.placeholder_command)
        tools_menu.add_separator()
        tools_menu.add_command(label="Proxy Configuration", command=self.placeholder_command)

        # --- Downloads Menu ---
        downloads_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Downloads", menu=downloads_menu)
        downloads_menu.add_command(label="Pause All Downloads", command=self.placeholder_command)
        downloads_menu.add_command(label="Resume All", command=self.placeholder_command)
        downloads_menu.add_command(label="Cancel All", command=self.placeholder_command)
        downloads_menu.add_separator()
        downloads_menu.add_command(label="Open Download Folder", command=self.browse_folder)
        downloads_menu.add_command(label="Retry Failed Downloads", command=self.placeholder_command)

        # --- Help Menu ---
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.placeholder_command)
        help_menu.add_command(label="Check for Updates", command=self.placeholder_command)
        help_menu.add_command(label="Report a Bug", command=self.placeholder_command)
        help_menu.add_separator()
        help_menu.add_command(label="About This App", command=self.show_about)

    def create_widgets(self):
        # Main grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Top Bar ---
        self.top_frame = ctk.CTkFrame(self, corner_radius=0)
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.top_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self.top_frame, text="YouTube Video Downloader", font=("Arial", 20, "bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.theme_switch = ctk.CTkSwitch(self.top_frame, text="Light/Dark", command=self.toggle_mode)
        self.theme_switch.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        self.theme_switch.select() # Start in dark mode

        # --- Left Column: Input and Video Info ---
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(2, weight=1)

        self.url_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Paste YouTube video URL here...")
        self.url_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.fetch_btn = ctk.CTkButton(self.left_frame, text="Fetch Video Info", command=self.fetch_video_info)
        self.fetch_btn.grid(row=1, column=0, padx=10, pady=5)

        self.media_info_frame = ctk.CTkScrollableFrame(self.left_frame)
        self.media_info_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.media_info_frame.grid_columnconfigure(0, weight=1)
        self.media_info_frame._scrollbar.grid_forget()

        self.thumbnail_label = ctk.CTkLabel(self.media_info_frame, text="", width=320, height=180)
        self.thumbnail_label.grid(row=0, column=0, padx=10, pady=10)

        self.title_info = ctk.CTkLabel(self.media_info_frame, font=("Arial", 14, "bold"), justify="left")
        self.author_info = ctk.CTkLabel(self.media_info_frame, font=("Arial", 12), justify="left")
        self.length_info = ctk.CTkLabel(self.media_info_frame, font=("Arial", 12), justify="left")
        self.views_info = ctk.CTkLabel(self.media_info_frame, font=("Arial", 12), justify="left")

        # --- Right Column: Download Options ---
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Format and Quality
        self.format_quality_frame = ctk.CTkFrame(self.right_frame)
        self.format_quality_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.format_quality_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.format_quality_frame, text="Format:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.format_menu = ctk.CTkOptionMenu(self.format_quality_frame, variable=self.selected_format, values=["MP4", "MP3", "WebM", "MKV"])
        self.format_menu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.format_quality_frame, text="Quality:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.quality_menu = ctk.CTkOptionMenu(self.format_quality_frame, variable=self.selected_quality, values=["Best", "1080p", "720p", "480p"])
        self.quality_menu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Download Config
        self.config_frame = ctk.CTkFrame(self.right_frame)
        self.config_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.config_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.config_frame, text="Download Folder:").grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        self.folder_entry = ctk.CTkEntry(self.config_frame, textvariable=self.download_folder)
        self.folder_entry.grid(row=1, column=0, padx=(10,5), pady=5, sticky="ew")
        self.browse_btn = ctk.CTkButton(self.config_frame, text="Browse", command=self.browse_folder, width=80)
        self.browse_btn.grid(row=1, column=1, padx=(0,10), pady=5)

        # Download Actions
        self.download_frame = ctk.CTkFrame(self.right_frame)
        self.download_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.download_frame.grid_columnconfigure(0, weight=1)

        self.download_btn = ctk.CTkButton(self.download_frame, text="Download", command=self.start_download, state="disabled")
        self.download_btn.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.progress = ctk.CTkProgressBar(self.download_frame)
        self.progress.set(0)
        self.progress.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        
        self.status_label = ctk.CTkLabel(self.download_frame, text="")
        self.status_label.grid(row=2, column=0, columnspan=3, padx=10, pady=5)

        # --- Bottom Tabs ---
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=2, column=0, columnspan=2, padx=20, pady=(10,20), sticky="nsew")
        self.tab_view.add("Download Queue")
        self.tab_view.add("History")
        self.tab_view.add("Batch Download")

        ctk.CTkLabel(self.tab_view.tab("Download Queue"), text="Download queue management will be here.").pack(padx=20, pady=20)
        ctk.CTkLabel(self.tab_view.tab("History"), text="Download history will be here.").pack(padx=20, pady=20)
        ctk.CTkLabel(self.tab_view.tab("Batch Download"), text="Playlist/batch download options will be here.").pack(padx=20, pady=20)

    def fetch_video_info(self):
        # Clear previous info
        self.thumbnail_label.configure(image=None, text="")
        self.title_info.grid_forget()
        self.author_info.grid_forget()
        self.length_info.grid_forget()
        self.views_info.grid_forget()

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
        self.views_info.configure(text=f"Views: {info.get('view_count', 'N/A'):,}")

        # Place labels on grid
        self.title_info.grid(row=1, column=0, sticky="ew", padx=10, pady=2)
        self.author_info.grid(row=2, column=0, sticky="ew", padx=10, pady=2)
        self.length_info.grid(row=3, column=0, sticky="ew", padx=10, pady=2)
        self.views_info.grid(row=4, column=0, sticky="ew", padx=10, pady=2)

        # Quality options
        formats = info.get('formats', [])
        video_options = set()
        for f in formats:
            if f.get('vcodec') not in [None, 'none'] and f.get('height') is not None:
                video_options.add(f"{f['height']}p")
        
        if video_options:
            # Sort by integer value of resolution
            sorted_options = sorted(list(video_options), key=lambda x: int(x.replace('p','')), reverse=True)
            self.quality_menu.configure(values=sorted_options)
            self.selected_quality.set(sorted_options[0])
        else:
            self.quality_menu.configure(values=["No qualities found"])
            self.selected_quality.set("No qualities found")

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
        selected_format = self.selected_format.get().lower()
        selected_quality = self.selected_quality.get()

        if selected_format in ['mp3', 'm4a']: # Audio download
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f"{self.download_folder.get()}/%(title)s.%(ext)s",
                'progress_hooks': [self.yt_progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': selected_format,
                    'preferredquality': '192', # default quality
                }],
                'quiet': True,
            }
        else: # Video download
            ydl_opts = {
                'format': f'bestvideo[height<={selected_quality[:-1]}]+bestaudio/best[height<={selected_quality[:-1]}]/best',
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

    def toggle_fullscreen(self):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    def show_about(self):
        messagebox.showinfo("About YouTube Downloader", "Version: 1.0\nCreated with CustomTkinter")

    def placeholder_command(self):
        messagebox.showinfo("Info", "This feature is not yet implemented.")

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
