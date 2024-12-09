import os
import subprocess
from tkinter import ttk, StringVar, Menu, filedialog
from tkinter.ttk import Progressbar
from tkinter.constants import END
from pathlib import Path
import yt_dlp
from getinfo import get_video_info
import requests
from io import BytesIO
from PIL import Image, ImageTk

class GGDriveDownloader:
    def __init__(self, master, parent):
        self.master = master
        self.parent = parent

        # Google Drive Video Download Frame
        self.ggdrive_frame = ttk.LabelFrame(self.master, text="GGDrive Video Download")
        self.ggdrive_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Google Drive Video URL Label
        self.ggdrive_url_label = ttk.Label(self.ggdrive_frame, text="GGDrive Video URL:")
        self.ggdrive_url_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Google Drive Video URL Entry
        self.ggdrive_url_var = StringVar()
        self.ggdrive_url_entry = ttk.Entry(self.ggdrive_frame, textvariable=self.ggdrive_url_var, width=50)
        self.ggdrive_url_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.ggdrive_url_entry.bind("<Control-v>", self.on_url_entry_paste)  # Bind the Ctrl+V event
        self.ggdrive_url_entry.bind("<Button-3>", self.show_context_menu)  # Bind the right-click event

        # Right-click context menu to the URL entry
        self.context_menu = Menu(self.ggdrive_url_entry, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_text)
        self.context_menu.add_command(label="Paste", command=self.paste_text)

        # Save Location Label
        self.save_location_label = ttk.Label(self.ggdrive_frame, text="Chọn nơi lưu:")
        self.save_location_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Save Location Entry
        self.save_location_var = StringVar()
        self.save_location_entry = ttk.Entry(self.ggdrive_frame, textvariable=self.save_location_var, width=50)
        self.save_location_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Save Location Button
        self.save_location_button = ttk.Button(self.ggdrive_frame, text="Chọn Folder", command=self.choose_save_location)
        self.save_location_button.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        # Google Drive Video Download Button
        self.ggdrive_download_button = ttk.Button(self.ggdrive_frame, text="Download", command=self.download_ggdrive_video)
        self.ggdrive_download_button.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Open Download Folder Button
        self.open_download_folder_button = ttk.Button(self.ggdrive_frame, text="Open Download Folder", command=self.open_download_folder)
        self.open_download_folder_button.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Progress Bar
        self.progress_bar = ttk.Progressbar(self.ggdrive_frame, mode='determinate', length=540)
        self.progress_bar.grid(row=4, column=0, columnspan=4, padx=10, pady=5)

        # Video Information Frame
        self.video_info_frame = ttk.Frame(self.ggdrive_frame)
        self.video_info_frame.grid(row=5, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        self.thumbnail_label = ttk.Label(self.video_info_frame)
        self.thumbnail_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.video_info_container = ttk.Frame(self.video_info_frame)
        self.video_info_container.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.title_label = ttk.Label(self.video_info_container, text="", style="CustomBoldLabel.TLabel", wraplength=350)
        self.title_label.pack(pady=5, anchor="w")

        self.length_label = ttk.Label(self.video_info_container, text="", style="CustomLabel.TLabel")
        self.length_label.pack(pady=5, anchor="w")

        self.resolutions_label = ttk.Label(self.video_info_container, text="", style="CustomLabel.TLabel", wraplength=350)
        self.resolutions_label.pack(pady=5, anchor="w")

        self.download_speed_label = ttk.Label(self.video_info_container, text="", style="CustomLabel.TLabel")
        self.download_speed_label.pack(pady=5, anchor="w")

    # Delay 100ms after pasting the link
    def on_url_entry_paste(self, event):
        self.ggdrive_url_entry.after(100, self.on_url_entry_focus_out)

    # Process the URL entry and get video information
    def on_url_entry_focus_out(self, event=None):
        ggdrive_url = self.ggdrive_url_var.get()
        if ggdrive_url:
            # Display a message that video information is being fetched
            self.parent.status_bar.config(text="Đang lấy thông tin video...", style="CustomStatusBar.TLabel")
            self.master.update()

            video_info = get_video_info(ggdrive_url)
            self.update_video_info(video_info)

            # Reset the status bar message
            self.parent.status_bar.config(text="", style="CustomStatusBar.TLabel")
            self.master.update()

    # Download and display the thumbnail image
    def update_video_info(self, video_info):
        # Update the video info
        thumbnail_url = video_info['thumbnail']
        if thumbnail_url:
            try:
                response = requests.get(video_info['thumbnail'])
                img_data = response.content
                img = Image.open(BytesIO(img_data))

                # Resize the thumbnail to fit the frame
                if img.width > img.height:
                    img = img.resize((160, 90), resample=Image.LANCZOS)
                else:
                    img = img.resize((90, 160), resample=Image.LANCZOS)

                photo = ImageTk.PhotoImage(img)
                self.thumbnail_label.configure(image=photo)
                self.thumbnail_label.image = photo
            except Exception as e:
                # Handle errors when downloading the thumbnail
                print(f"Error downloading thumbnail: {e}")
                self.thumbnail_label.configure(text="Thumbnail không khả dụng")
                self.thumbnail_label.image = None  # Clear the old thumbnail
        else:
            self.thumbnail_label.configure(text="Thumbnail không khả dụng")
            self.thumbnail_label.image = None  # Clear the old thumbnail

        title = video_info['title']
        self.title_label.configure(text=f"Tiêu đề: {title}", wraplength=350)

        length = video_info['length']
        self.length_label.configure(text=f"Thời lượng: {length}")

        resolutions_text = f"Độ phân giải: {video_info['resolutions']}"
        self.resolutions_label.configure(text=resolutions_text, wraplength=350)

    # Show the right-click context menu
    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    # Copy text from the URL entry
    def copy_text(self):
        self.ggdrive_url_entry.clipboard_clear()
        self.ggdrive_url_entry.clipboard_append(self.ggdrive_url_entry.get())

    # Paste text into the URL entry
    def paste_text(self):
        self.ggdrive_url_entry.delete(0, END)
        self.ggdrive_url_entry.insert(0, self.ggdrive_url_entry.clipboard_get())
        self.on_url_entry_focus_out((self.ggdrive_url_entry.get()))

    # Choose the save location
    def choose_save_location(self):
        save_location = filedialog.askdirectory(title="Choose Save Location")
        if save_location:
            self.save_location_var.set(save_location)

    # Download the Google Drive video
    def download_ggdrive_video(self):
        ggdrive_url = self.ggdrive_url_var.get()
        save_location = self.save_location_var.get()
        if ggdrive_url and save_location:
            self.parent.status_bar.config(text="Đang tải xuống video từ Google Drive...", style="CustomStatusBar.TLabel")
            try:
                download_dir = save_location
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

                self.parent.status_bar.config(text="Video đã được tải xuống!", style="CustomStatusBar.TLabel")
            except (subprocess.CalledProcessError, yt_dlp.utils.DownloadError) as e:
                self.parent.status_bar.config(text="Lỗi không thể tải xuống video từ Google Drive.", style="CustomStatusBar.TLabel")
                print(f"Error: {e}")
        else:
            self.parent.status_bar.config(text="Vui lòng kiểm tra URL hoặc thư mục lưu.", style="CustomStatusBar.TLabel")

    # Display the progress of the download
    def show_progress(self, progress):
        if progress['status'] == 'downloading':
            percentage = progress['_percent_str']
            download_speed = self.format_bytes(progress.get('speed', 0))
            eta = self.format_time(progress.get('eta', 0))
            self.progress_bar['value'] = progress['downloaded_bytes'] / progress['total_bytes'] * 100
            self.progress_bar.update()
           # self.download_speed_label.configure(text=f"Tốc độ tải: {download_speed}/s | Còn lại: {eta}")
            self.parent.status_bar.config(text=f"Đang tải xuống... | Tốc độ tải: {download_speed}/s | Còn lại: {eta}", style="CustomStatusBar.TLabel")
        elif progress['status'] == 'finished':
            self.progress_bar['value'] = 100
            self.progress_bar.update()
            self.parent.status_bar.config(text="Video đã được tải xuống!", style="CustomStatusBar.TLabel")

    # Open the download folder
    def open_download_folder(self):
        save_location = self.save_location_var.get()
        if save_location:
            os.startfile(save_location)
        else:
            self.parent.status_bar.config(text="Chưa chọn Folder lưu.", style="CustomStatusBar.TLabel")

    # Helper functions to format download speed and time
    def format_bytes(self, bytes):
        if bytes is None:
            return "N/A"
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
        suffix_index = 0
        while bytes >= 1024 and suffix_index < len(suffixes) - 1:
            bytes /= 1024
            suffix_index += 1
        return f"{bytes:.2f} {suffixes[suffix_index]}"

    def format_time(self, seconds):
        if seconds is None:
            return "N/A"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
