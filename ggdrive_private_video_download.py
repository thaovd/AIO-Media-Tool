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

    # Delay 100ms sau khi paste link
    def on_url_entry_paste(self, event):
        self.ggdrive_url_entry.after(100, self.on_url_entry_focus_out)

    #Khối xử lý thông báo và nhận diện thao tác paste link xử lý get info
    def on_url_entry_focus_out(self, event=None):
        ggdrive_url = self.ggdrive_url_var.get()
        if ggdrive_url:
            # Thông báo đang lấy thông tin
            self.parent.status_bar.config(text="Đang lấy thông tin video...", style="CustomStatusBar.TLabel")
            self.master.update()

            video_info = get_video_info(ggdrive_url)
            self.update_video_info(video_info)

            # Reset thông báo thanh trạng thái
            self.parent.status_bar.config(text="", style="CustomStatusBar.TLabel")
            self.master.update()

    # Khối xử lý lấy và hiển thị ảnh thumb
    def update_video_info(self, video_info):
        # Update the video info
        thumbnail_url = video_info['thumbnail']
        if thumbnail_url:
            try:
                response = requests.get(video_info['thumbnail'])
                img_data = response.content
                img = Image.open(BytesIO(img_data))
                photo = ImageTk.PhotoImage(img)
                self.thumbnail_label.configure(image=photo)
                self.thumbnail_label.image = photo
            except Exception as e:
                # Xử lý lỗi xảy ra trong quá trình tải xuống hình thumb
                print(f"Error downloading thumbnail: {e}")
                self.thumbnail_label.configure(text="Thumbnail không khả dụng")
                self.thumbnail_label.image = None  # Clear hình thumb cũ
        else:
            self.thumbnail_label.configure(text="Thumbnail không khả dụng")
            self.thumbnail_label.image = None  # Clear hình thumb cũ

        title = video_info['title']
        self.title_label.configure(text=f"Tiêu đề: {title}", wraplength=350)

        length = video_info['length']
        self.length_label.configure(text=f"Thời lượng: {length}")

        resolutions_text = f"Độ phân giải: {video_info['resolutions']}"
        self.resolutions_label.configure(text=resolutions_text, wraplength=350)

    # Khối xử lý hiển thị menu context
    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    # Khối xử lý Copy ở menu context
    def copy_text(self):
        self.ggdrive_url_entry.clipboard_clear()
        self.ggdrive_url_entry.clipboard_append(self.ggdrive_url_entry.get())

    # Khối xử lý Paste ở menu context
    def paste_text(self):
        self.ggdrive_url_entry.delete(0, END)
        self.ggdrive_url_entry.insert(0, self.ggdrive_url_entry.clipboard_get())
        self.on_url_entry_focus_out((self.ggdrive_url_entry.get()))

    # Khối xử lý Chọn Folder
    def choose_save_location(self):
        save_location = filedialog.askdirectory(title="Choose Save Location")
        if save_location:
            self.save_location_var.set(save_location)

    # Khối xử lý Download
    def download_ggdrive_video(self):
        ggdrive_url = self.ggdrive_url_var.get()
        save_location = self.save_location_var.get()
        if ggdrive_url and save_location:
            self.parent.status_bar.config(text="Đang tải xuống video từ Google Drive...")
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

                self.parent.status_bar.config(text="Video đã được tải xuống!")
            except (subprocess.CalledProcessError, yt_dlp.utils.DownloadError) as e:
                self.parent.status_bar.config(text="Lỗi không thể tải xuống video từ Google Drive.")
                print(f"Error: {e}")
        else:
            self.parent.status_bar.config(text="Vui lòng kiểm tra URL hoặc thư mục lưu.")

    # Khối xử lý hiển thị progressbar
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

    # Khối xử lý Open Folder
    def open_download_folder(self):
        save_location = self.save_location_var.get()
        if save_location:
            os.startfile(save_location)
        else:
            self.parent.status_bar.config(text="Chưa chọn Folder lưu.")
