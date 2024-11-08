import os
import subprocess
from tkinter import ttk, StringVar, Menu
from tkinter.ttk import Progressbar
from tkinter.constants import END
from pathlib import Path
import yt_dlp

class GGDriveDownloader:
    def __init__(self, master, parent):
        self.master = master
        self.parent = parent

        # Google Drive Video Download Frame
        self.ggdrive_frame = ttk.LabelFrame(self.master, text="GGDrive Video Block Download")
        self.ggdrive_frame.pack(fill="x", padx=20, pady=10)

        # Google Drive Video URL Label
        self.ggdrive_url_label = ttk.Label(self.ggdrive_frame, text="GGDrive Video URL:")
        self.ggdrive_url_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Google Drive Video URL Entry
        self.ggdrive_url_var = StringVar()
        self.ggdrive_url_entry = ttk.Entry(self.ggdrive_frame, textvariable=self.ggdrive_url_var, width=20)
        self.ggdrive_url_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")

        # Add right-click context menu to the URL entry
        self.ggdrive_url_entry.bind("<Button-3>", self.show_context_menu)
        self.context_menu = Menu(self.ggdrive_url_entry, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_text)
        self.context_menu.add_command(label="Paste", command=self.paste_text)

        # Google Drive Video Download Button
        self.ggdrive_download_button = ttk.Button(self.ggdrive_frame, text="Download", command=self.download_ggdrive_video)
        self.ggdrive_download_button.grid(row=0, column=2, padx=10, pady=5)

        # Open Download Folder Button
        self.open_download_folder_button = ttk.Button(self.ggdrive_frame, text="Mở thư mục tải xuống", command=self.open_download_folder)
        self.open_download_folder_button.grid(row=0, column=3, padx=10, pady=5)

        # Progress Bar
        self.progress_bar = Progressbar(self.ggdrive_frame, style="CustomProgressBar.Horizontal.TProgressbar", maximum=100)
        self.progress_bar.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def copy_text(self):
        self.ggdrive_url_entry.clipboard_clear()
        self.ggdrive_url_entry.clipboard_append(self.ggdrive_url_entry.get())

    def paste_text(self):
        self.ggdrive_url_entry.delete(0, END)
        self.ggdrive_url_entry.insert(0, self.ggdrive_url_entry.clipboard_get())

    def download_ggdrive_video(self):
        ggdrive_url = self.ggdrive_url_var.get()
        if ggdrive_url:
            self.parent.status_bar.config(text="Đang tải xuống video từ Google Drive...")
            try:
                download_dir = os.path.join("Download-yt")
                os.makedirs(download_dir, exist_ok=True)

                ydl_opts = {
                    'outtmpl': f"{download_dir}/%(title)s.%(ext)s",
                    'progress_hooks': [self.show_progress],
                    'quiet': True,
                    'no_warnings': True,
                    'ignoreerrors': True,
                    'format': '22'
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([ggdrive_url])

                self.parent.status_bar.config(text="Video đã được tải xuống!")
            except (subprocess.CalledProcessError, yt_dlp.utils.DownloadError) as e:
                self.parent.status_bar.config(text="Lỗi không thể tải xuống video từ Google Drive.")
                print(f"Error: {e}")
        else:
            self.parent.status_bar.config(text="Please enter a valid Google Drive video URL.")

    def show_progress(self, progress):
        if progress['status'] == 'downloading':
            percentage = progress['_percent_str']
            self.progress_bar['value'] = progress['downloaded_bytes'] / progress['total_bytes'] * 100
            self.progress_bar.update()
            self.parent.status_bar.config(text=f"Đang tải xuống... {percentage}")
        elif progress['status'] == 'finished':
            self.progress_bar['value'] = 100
            self.progress_bar.update()
            self.parent.status_bar.config(text="Video đã được tải xuống!")

    def open_download_folder(self):
        download_dir = os.path.join("Download-yt")
        os.startfile(download_dir)
