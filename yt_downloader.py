import os
import yt_dlp
from tkinter import ttk, StringVar, Menu
import tkinter as tk

class YTDownloader:
    def __init__(self, master, app):
        self.master = master
        self.app = app

        # YouTube Downloader Section
        self.yt_downloader_frame = ttk.LabelFrame(master, text="Tiktok, YouTube, Facebook Downloader", style="CustomLabelFrame.TLabelframe")
        self.yt_downloader_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.yt_url_label = ttk.Label(self.yt_downloader_frame, text="Link Video Youtube:", style="CustomSmallLabel.TLabel")
        self.yt_url_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.yt_url_entry = ttk.Entry(self.yt_downloader_frame, style="CustomEntry.TEntry")
        self.yt_url_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")

        # Add right-click menu for copy and paste
        self.yt_url_entry.bind("<Button-3>", self.show_right_click_menu)
        self.right_click_menu = Menu(self.yt_url_entry, tearoff=0)
        self.right_click_menu.add_command(label="Copy", command=self.copy_text)
        self.right_click_menu.add_command(label="Paste", command=self.paste_text)

        self.audio_only_button = ttk.Button(self.yt_downloader_frame, text="Audio only YT/FB", command=lambda: self.download_audio_only(), style="CustomButton.TButton")
        self.audio_only_button.grid(row=1, column=0, padx=10, pady=5)

        self.video_only_button = ttk.Button(self.yt_downloader_frame, text="Video only YT/FB", command=lambda: self.download_video_only(), style="CustomButton.TButton")
        self.video_only_button.grid(row=1, column=1, padx=10, pady=5)

        self.audio_video_button = ttk.Button(self.yt_downloader_frame, text="A+V YT/FB", command=lambda: self.download_audio_and_video(), style="CustomButton.TButton")
        self.audio_video_button.grid(row=1, column=2, padx=10, pady=5)

        self.tiktok_button = ttk.Button(self.yt_downloader_frame, text="A+V Tiktok", command=lambda: self.download_tiktok(), style="CustomButton.TButton")
        self.tiktok_button.grid(row=2, column=0, padx=10, pady=5)

        self.max_quality = ttk.Button(self.yt_downloader_frame, text="Max Quality Up to 4K YT/FB", command=lambda: self.download_max_quality(), style="CustomButton.TButton")
        self.max_quality.grid(row=2, column=1, padx=10, pady=5)

        self.open_yt_folder_button = ttk.Button(self.yt_downloader_frame, text="Mở thư mục Download", command=lambda: self.open_folder("Download-yt"), style="CustomButton.TButton")
        self.open_yt_folder_button.grid(row=2, column=2, columnspan=3, padx=10, pady=5)

        self.progress_bar = ttk.Progressbar(self.yt_downloader_frame, mode='determinate', length=500)  # Increased progress bar length to 500 pixels
        self.progress_bar.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    def show_right_click_menu(self, event):
        self.right_click_menu.post(event.x_root, event.y_root)

    def copy_text(self):
        self.yt_url_entry.clipboard_clear()
        self.yt_url_entry.clipboard_append(self.yt_url_entry.get())

    def paste_text(self):
        self.yt_url_entry.delete(0, tk.END)  # Use tk.END instead of END
        self.yt_url_entry.insert(0, self.yt_url_entry.clipboard_get())

    def download_audio_only(self):
        self.download_video(format='bestaudio[ext=m4a]')

    def download_video_only(self):
        self.download_video(format='bv[ext=mp4]')

    def download_audio_and_video(self):
        self.download_video(format='bv*[ext=mp4]+ba')

    def download_tiktok(self):
        self.download_video()

    def download_max_quality(self):
        self.download_video(format='bv*[ext=mp4]+ba')

    def download_video(self, format=None):
        video_url = self.yt_url_entry.get()
        if video_url:
            # Check if the URL is for a playlist
            if 'list=' in video_url:
                self.app.status_bar.config(text="Downloading playlists is not supported.", style="CustomStatusBar.TLabel")
                self.master.update()
                return

            output_file = "./Download-yt/%(title)s.%(id)s.%(ext)s"
            self.app.status_bar.config(text="Đang tải xuống...", style="CustomStatusBar.TLabel")
            self.master.update()

            try:
                ydl_opts = {
                    'outtmpl': output_file,
                    'format': format if format else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'quiet': True,
                    'no_warnings': True,
                    'ignoreerrors': True,
                    'progress_hooks': [self.show_progress],
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                self.app.status_bar.config(text="Đã tải xuống.", style="CustomStatusBar.TLabel")
            except Exception as e:
                # Handle all exceptions without showing error messages
                self.app.status_bar.config(text="Lỗi không xác định, vui lòng thử lại sau.", style="CustomStatusBar.TLabel")
            finally:
                self.master.update()

    def show_progress(self, progress):
        if progress['status'] == 'downloading':
            percentage = progress['_percent_str']
            if 'total_bytes' in progress:
                self.progress_bar['value'] = progress['downloaded_bytes'] / progress['total_bytes'] * 100
            else:
                self.progress_bar['value'] = 0  # Reset the progress bar to 0 if 'total_bytes' is not available
            self.app.status_bar.config(text=f"Đang tải xuống... {percentage}")
            self.master.update()

    def open_folder(self, folder_name):
        folder_path = os.path.join(os.getcwd(), folder_name)
        if os.path.exists(folder_path):
            os.startfile(folder_path)
