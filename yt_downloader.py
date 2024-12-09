import os
import yt_dlp
from tkinter import ttk, StringVar, Menu, Toplevel, Label, Button, Text, BOTH, WORD, messagebox, filedialog
import tkinter as tk
from getinfo import get_video_info
from io import BytesIO
from PIL import Image, ImageTk
import requests
import re

script_dir = os.path.dirname(os.path.abspath(__file__))
ffmpeg_path = os.path.join(script_dir, 'ffmpeg.exe')

class YTDownloader:
    def __init__(self, master, app):
        self.master = master
        self.app = app

        # Input Select Frame
        self.yt_downloader_frame = ttk.LabelFrame(master, text="Tiktok, YouTube, Facebook, Drive Downloader v.v..", style="CustomLabelFrame.TLabelframe")
        self.yt_downloader_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.yt_url_label = ttk.Label(self.yt_downloader_frame, text="Link Video:", style="CustomSmallLabel.TLabel")
        self.yt_url_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.yt_url_entry = ttk.Entry(self.yt_downloader_frame, style="CustomEntry.TEntry")
        self.yt_url_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=5, sticky="we")
        self.yt_url_entry.bind("<Control-v>", self.on_url_entry_paste)  # Gắn sự kiện Ctrl+V
        self.yt_url_entry.bind("<Button-3>", self.show_right_click_menu)  # Gắn sự kiện chuột phải

        self.right_click_menu = Menu(self.yt_url_entry, tearoff=0)
        self.right_click_menu.add_command(label="Copy", command=self.copy_text)
        self.right_click_menu.add_command(label="Paste", command=self.paste_text)

        # Save Folder Select Frame
        self.save_location_label = ttk.Label(self.yt_downloader_frame, text="Chọn nơi lưu:", style="CustomSmallLabel.TLabel")
        self.save_location_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.save_location_var = StringVar()
        self.save_location_entry = ttk.Entry(self.yt_downloader_frame, textvariable=self.save_location_var, style="CustomEntry.TEntry")
        self.save_location_entry.grid(row=1, column=1, padx=10, pady=20, sticky="we")

        self.save_location_button = ttk.Button(self.yt_downloader_frame, text="Chọn Folder", command=self.choose_save_location, style="CustomButton.TButton")
        self.save_location_button.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        self.audio_only_button = ttk.Button(self.yt_downloader_frame, text="Audio only", command=lambda: self.download_audio_only(), style="CustomButton.TButton")
        self.audio_only_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.video_only_button = ttk.Button(self.yt_downloader_frame, text="Video only (Max)", command=lambda: self.download_video_only(), style="CustomButton.TButton")
        self.video_only_button.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.audio_video_button = ttk.Button(self.yt_downloader_frame, text="A+V (Max)", command=lambda: self.download_audio_and_video(), style="CustomButton.TButton")
        self.audio_video_button.grid(row=2, column=2, padx=10, pady=5, sticky="w")

        self.tiktok_button = ttk.Button(self.yt_downloader_frame, text="A+V Tiktok (Max)", command=lambda: self.download_tiktok(), style="CustomButton.TButton")
        self.tiktok_button.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.custom_download_button = ttk.Button(self.yt_downloader_frame, text="Lựa chọn chất lượng khác", command=self.show_custom_download_popup, style="CustomButton.TButton")
        self.custom_download_button.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        self.m3u8_button = ttk.Button(self.yt_downloader_frame, text="Download m3u8 Video", command=lambda: self.download_m3u8(), style="CustomButton.TButton")
        self.m3u8_button.grid(row=3, column=2, padx=10, pady=5, sticky="w")

        # Playlist download button
        self.playlist_download_button = ttk.Button(self.yt_downloader_frame, text="Download Playlist", command=self.download_playlist, style="CustomButton.TButton")
        self.playlist_download_button.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self.open_yt_folder_button = ttk.Button(self.yt_downloader_frame, text="Mở thư mục Download", command=self.open_folder, style="CustomButton.TButton")
        self.open_yt_folder_button.grid(row=4, column=1, columnspan=2, padx=10, pady=5, sticky="w")

        self.progress_bar = ttk.Progressbar(self.yt_downloader_frame, mode='determinate', length=540)  # Increased progress bar length to 500 pixels
        self.progress_bar.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

        # Guide Button
        self.user_guide_button = ttk.Button(self.yt_downloader_frame, text="Hướng Dẫn Sử Dụng", command=self.show_user_guide, style="CustomButton.TButton")
        self.user_guide_button.grid(row=4, column=2, padx=10, pady=5, sticky="w" )

        # Video information
        self.video_info_frame = ttk.Frame(self.yt_downloader_frame)
        self.video_info_frame.grid(row=6, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        self.thumbnail_label = ttk.Label(self.video_info_frame)
        self.thumbnail_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.video_info_container = ttk.Frame(self.video_info_frame)
        self.video_info_container.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.title_label = ttk.Label(self.video_info_container, text="", style="CustomBoldLabel.TLabel", wraplength=400)
        self.title_label.pack(pady=5, anchor="w")

        self.length_label = ttk.Label(self.video_info_container, text="", style="CustomLabel.TLabel")
        self.length_label.pack(pady=5, anchor="w")

        self.resolutions_label = ttk.Label(self.video_info_container, text="", style="CustomLabel.TLabel", wraplength=400)
        self.resolutions_label.pack(pady=5, anchor="w")

    def on_url_entry_paste(self, event):
        self.yt_url_entry.after(100, self.on_url_entry_focus_out)  # Delay 100ms xong mới gọi on_url_entry_focus_out

    def on_url_entry_focus_out(self, event=None):
        video_url = self.yt_url_entry.get()
        if video_url:
            # Kiểm tra xem URL có phải là playlist không
            if 'list=' in video_url:
                self.app.status_bar.config(text="URL playlist. Sử dụng tính năng Download Playlist.", style="CustomStatusBar.TLabel")
                self.master.update()
                self.custom_download_button.config(state='disabled')
                self.audio_only_button.config(state='disabled')
                self.video_only_button.config(state='disabled')
                self.audio_video_button.config(state='disabled')
                self.tiktok_button.config(state='disabled')
                self.m3u8_button.config(state='disabled')
                self.playlist_download_button.config(state='normal')
                
                return

            # Kiểm tra xem URL có phải là Google Drive không
            if 'drive.google.com' in video_url:
                self.app.status_bar.config(text="Đang lấy thông tin video...", style="CustomStatusBar.TLabel")
                self.master.update()
                video_info = get_video_info(video_url)
                self.update_video_info(video_info)
                self.app.status_bar.config(text="URL Google Drive. Sử dụng tính năng 'Lựa chọn chất lượng khác' để tải xuống.", style="CustomStatusBar.TLabel")
                self.master.update()
                self.custom_download_button.config(state='normal')
                self.audio_only_button.config(state='disabled')
                self.video_only_button.config(state='disabled')
                self.audio_video_button.config(state='disabled')
                self.tiktok_button.config(state='disabled')
                self.m3u8_button.config(state='disabled')
                self.playlist_download_button.config(state='disabled')
                return
            if 'tiktok.com' in video_url:
                self.app.status_bar.config(text="Đang lấy thông tin video...", style="CustomStatusBar.TLabel")
                self.master.update()
                video_info = get_video_info(video_url)
                self.update_video_info(video_info)
                self.app.status_bar.config(text="", style="CustomStatusBar.TLabel")
                self.master.update()
                self.custom_download_button.config(state='normal')
                self.audio_only_button.config(state='disabled')
                self.video_only_button.config(state='disabled')
                self.audio_video_button.config(state='disabled')
                self.tiktok_button.config(state='normal')
                self.m3u8_button.config(state='disabled')
                self.playlist_download_button.config(state='disabled')
                return
            if 'youtube.com' in video_url:
                self.app.status_bar.config(text="Đang lấy thông tin video...", style="CustomStatusBar.TLabel")
                self.master.update()
                video_info = get_video_info(video_url)
                self.update_video_info(video_info)
                self.app.status_bar.config(text="", style="CustomStatusBar.TLabel")
                self.master.update()
                self.custom_download_button.config(state='normal')
                self.audio_only_button.config(state='normal')
                self.video_only_button.config(state='normal')
                self.audio_video_button.config(state='normal')
                self.tiktok_button.config(state='disabled')
                self.m3u8_button.config(state='disabled')
                self.playlist_download_button.config(state='disabled')
                return
            if 'facebook.com' in video_url:
                self.app.status_bar.config(text="Đang lấy thông tin video...", style="CustomStatusBar.TLabel")
                self.master.update()
                video_info = get_video_info(video_url)
                self.update_video_info(video_info)
                self.app.status_bar.config(text="", style="CustomStatusBar.TLabel")
                self.master.update()
                self.custom_download_button.config(state='normal')
                self.audio_only_button.config(state='normal')
                self.video_only_button.config(state='normal')
                self.audio_video_button.config(state='normal')
                self.tiktok_button.config(state='disabled')
                self.m3u8_button.config(state='disabled')
                self.playlist_download_button.config(state='disabled')
                return


            # Hiển thị thông báo "Đang lấy thông tin video" trên thanh trạng thái
            self.app.status_bar.config(text="Đang lấy thông tin video...", style="CustomStatusBar.TLabel")
            self.master.update()
            video_info = get_video_info(video_url)
            self.update_video_info(video_info)

            # Reset thông báo thanh trạng thái
            self.app.status_bar.config(text="", style="CustomStatusBar.TLabel")
            self.master.update()

    # Khối xử lý lấy thông tin video
    def update_video_info(self, video_info):
        self.thumbnail_label.configure(image=None) 
        self.thumbnail_label.image = None 

        if video_info['thumbnail']:
            try:
                # Download the thumbnail image
                response = requests.get(video_info['thumbnail'])
                img_data = response.content
                img = Image.open(BytesIO(img_data))

                # Resize the thumbnail to fit the desired dimensions
                if img.width > img.height:
                    img = img.resize((120, 90), resample=Image.BICUBIC)
                else:
                    img = img.resize((90, 120), resample=Image.BICUBIC)

                photo = ImageTk.PhotoImage(img)
                self.thumbnail_label.configure(image=photo)
                self.thumbnail_label.image = photo
            except Exception as e:
                print(f"Lỗi tải xuống thumbnail: {e}")
                self.thumbnail_label.configure(text="Thumbnail không khả dụng")
                self.thumbnail_label.image = None 
        else:
            self.thumbnail_label.configure(text="Thumbnail không khả dụng")
            self.thumbnail_label.image = None 

        title = video_info['title']
        self.title_label.configure(text=f"Tiêu đề: {title}", wraplength=350) 

        resolutions_text = f"Độ phân giải: {video_info['resolutions']}"
        self.resolutions_label.configure(text=resolutions_text, wraplength=350)

        self.length_label.configure(text=f"Thời lượng: {video_info['length']}")

    def show_user_guide(self):
        user_guide_window = Toplevel(self.master)
        user_guide_window.title("Hướng Dẫn Sử Dụng")
        user_guide_window.geometry("600x400")

        # Căn giữa cửa sổ
        screen_width = user_guide_window.winfo_screenwidth()
        screen_height = user_guide_window.winfo_screenheight()
        window_width = 600
        window_height = 400
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        user_guide_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        user_guide_text = Text(user_guide_window, wrap=WORD)
        user_guide_text.pack(fill=BOTH, expand=True)

        with open("guildesocialdownload.txt", "r", encoding="utf-8") as file:
            user_guide_content = file.read()
        user_guide_text.insert("1.0", user_guide_content)
        user_guide_text.config(state="disabled")

        # Close button
        close_button = ttk.Button(user_guide_window, text="Đóng", command=user_guide_window.destroy)
        close_button.pack(pady=10)

    def show_right_click_menu(self, event):
        self.right_click_menu.post(event.x_root, event.y_root)

    def copy_text(self):
        self.yt_url_entry.clipboard_clear()
        self.yt_url_entry.clipboard_append(self.yt_url_entry.get())

    def paste_text(self):
        self.yt_url_entry.delete(0, tk.END)
        self.yt_url_entry.insert(0, self.yt_url_entry.clipboard_get())
        self.on_url_entry_focus_out((self.yt_url_entry.get()))

    def choose_save_location(self):
        save_location = filedialog.askdirectory(title="Choose Save Location")
        if save_location:
            self.save_location_var.set(save_location)

    def download_audio_only(self):
        if self.save_location_var.get():
            self.download_video(format='bestaudio[ext=m4a]')
        else:
            self.app.status_bar.config(text="Vui lòng chọn Folder lưu trước khi tải xuống.", style="CustomStatusBar.TLabel")
            self.master.update()

    def download_video_only(self):
        if self.save_location_var.get():
            self.download_video(format='bv[ext=mp4]')
        else:
            self.app.status_bar.config(text="Vui lòng chọn Folder lưu trước khi tải xuống.", style="CustomStatusBar.TLabel")
            self.master.update()


    def download_audio_and_video(self):
        if self.save_location_var.get():
            self.download_video(format='bv*[ext=mp4]+ba')
        else:
            self.app.status_bar.config(text="Vui lòng chọn Folder lưu trước khi tải xuống.", style="CustomStatusBar.TLabel")
            self.master.update()

    def download_tiktok(self):
        if self.save_location_var.get():
            self.download_video()
        else:
            self.app.status_bar.config(text="Vui lòng chọn Folder lưu trước khi tải xuống.", style="CustomStatusBar.TLabel")
            self.master.update()

    def show_custom_download_popup(self):
        # Check if save location is selected
        if not self.save_location_var.get():
            self.app.status_bar.config(text="Vui lòng chọn Folder lưu trước khi tải xuống.", style="CustomStatusBar.TLabel")
            self.master.update()
            return

        video_url = self.yt_url_entry.get()
        if video_url:
            # Kiểm tra xem URL có phải là playlist không
            if 'list=' in video_url:
                self.app.status_bar.config(text="URL này là Playlist video. Sử dụng tính năng Download Playlist.", style="CustomStatusBar.TLabel")
                self.master.update()
                return


            self.custom_download_popup = Toplevel(self.master)
            self.custom_download_popup.title("Lựa chọn chất lượng Video")

            # Căn giữa cửa sổ
            screen_width = self.custom_download_popup.winfo_screenwidth()
            screen_height = self.custom_download_popup.winfo_screenheight()
            window_width = 400
            window_height = 200
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            self.custom_download_popup.geometry(f"{window_width}x{window_height}+{x}+{y}")

            # Hiển thị thông báo "Đang lấy dữ liệu video" trong khi tải dữ liệu
            self.custom_download_popup.protocol("WM_DELETE_WINDOW", self.on_custom_download_popup_close)
            loading_label = Label(self.custom_download_popup, text="Đang lấy dữ liệu video...")
            loading_label.pack(pady=20)
            self.custom_download_popup.update()

            # Lấy video formats có sẵn
            ydl_opts = {}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                formats = info.get('formats', [])

            # Tạo danh sách chất lượng video
            quality_options = []
            seen_qualities = set()
            for format in formats:
                if format.get('vcodec') != 'none':
                    quality = f"{format.get('height')}p {format.get('ext')}"
                    if quality not in seen_qualities:
                        quality_options.append(quality)
                        seen_qualities.add(quality)

            # Xoá những thông tin video ko cần thiết
            loading_label.destroy()
            self.selected_quality = StringVar()
            self.selected_quality.set(quality_options[0])

            quality_label = Label(self.custom_download_popup, text="Lựa chọn chất lượng Video:")
            quality_label.pack(pady=10)

            quality_dropdown = ttk.Combobox(self.custom_download_popup, textvariable=self.selected_quality, values=quality_options)
            quality_dropdown.pack(pady=10)

            download_button = Button(self.custom_download_popup, text="Download", command=self.download_custom_video_and_close)
            download_button.pack(pady=10)

    def on_custom_download_popup_close(self):
        self.custom_download_popup.destroy()

    def download_custom_video_and_close(self):
        self.custom_download_popup.destroy()
        self.download_custom_video()

    def download_custom_video(self):
        video_url = self.yt_url_entry.get()
        save_location = self.save_location_var.get()
        if save_location:
            selected_quality = self.selected_quality.get()
            height, ext = selected_quality.split(" ")
            height = int(height[:-1])

            output_file = f"{save_location}/%(title)s.%(id)s.%(ext)s"
            self.app.status_bar.config(text="Đang tải xuống...", style="CustomStatusBar.TLabel")
            self.master.update()

            try:
                ydl_opts = {
                    'outtmpl': output_file,
                    'format': f'bestvideo[height<={height}][ext={ext}]+bestaudio[ext=m4a]/best[ext={ext}]',
                    'quiet': True,
                    'no_warnings': True,
                    'ignoreerrors': True,
                    'progress_hooks': [self.show_progress],
                    'ffmpeg_location': ffmpeg_path,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                self.app.status_bar.config(text="Đã tải xuống.", style="CustomStatusBar.TLabel")
                self.custom_download_popup.destroy()
            except Exception as e:
                self.app.status_bar.config(text="Lỗi không xác định, vui lòng thử lại sau.", style="CustomStatusBar.TLabel")
        else:
            self.app.status_bar.config(text="Vui lòng chọn Folder lưu trước khi tải xuống.", style="CustomStatusBar.TLabel")
            self.master.update()

    def download_m3u8(self):
        video_url = self.yt_url_entry.get()
        save_location = self.save_location_var.get()
        if video_url and save_location:
            # Check playlist
            if 'list=' in video_url:
                self.app.status_bar.config(text="Hãy sử dụng tính năng Download Playlist để tải xuống.", style="CustomStatusBar.TLabel")
                self.master.update()
                return

            # Kiểm tra xem URL có phải là Google Drive không
            if 'drive.google.com' in video_url:
                self.app.status_bar.config(text="Đây là URL Google Drive. Vui lòng sử dụng tính năng 'Lựa chọn chất lượng khác' để tải xuống.", style="CustomStatusBar.TLabel")
                self.master.update()
                return

            output_file = f"{save_location}/%(title)s.%(id)s.%(ext)s"
            self.app.status_bar.config(text="Đang tải xuống...", style="CustomStatusBar.TLabel")
            self.master.update()

            try:
                ydl_opts = {
                    'outtmpl': output_file,
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'quiet': True,
                    'no_warnings': True,
                    'ignoreerrors': True,
                    'progress_hooks': [self.show_progress],
                    'cookiefile': 'cookies.txt',
                    'ffmpeg_location': ffmpeg_path,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                self.app.status_bar.config(text="Đã tải xuống.", style="CustomStatusBar.TLabel")
            except Exception as e:
                self.app.status_bar.config(text="Lỗi không xác định, vui lòng thử lại sau.", style="CustomStatusBar.TLabel")
        else:
            self.app.status_bar.config(text="Vui lòng chọn Folder lưu trước khi tải xuống.", style="CustomStatusBar.TLabel")
            self.master.update()

    def download_playlist(self):
        video_url = self.yt_url_entry.get()
        save_location = self.save_location_var.get()
        if video_url and save_location:
            # Check playlist
            if 'list=' in video_url:
                self.app.status_bar.config(text="Đang lấy dữ liệu...", style="CustomStatusBar.TLabel")
                self.master.update()

                # Lấy số lượng video có trong playlist
                ydl_opts = {}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    num_videos = len(info.get('entries', []))

                # Hiển thị số lượng video trong playlist & hỏi
                if messagebox.askyesno("Xác nhận Download Playlist", f"Playlist này có {num_videos} videos. Bạn có muốn tiếp tục tải xuống không?"):
                    output_file = f"{save_location}/%(playlist_title)s/%(title)s.%(id)s.%(ext)s"
                    self.app.status_bar.config(text="Đang tải xuống playlist...", style="CustomStatusBar.TLabel")
                    self.master.update()

                    try:
                        ydl_opts = {
                            'outtmpl': output_file,
                            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                            'quiet': True,
                            'no_warnings': True,
                            'ignoreerrors': True,
                            'progress_hooks': [self.show_progress],
                            'ffmpeg_location': ffmpeg_path,
                        }
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([video_url])
                        self.app.status_bar.config(text="Đã tải xuống playlist.", style="CustomStatusBar.TLabel")
                    except Exception as e:
                        self.app.status_bar.config(text="Lỗi không xác định, vui lòng thử lại sau.", style="CustomStatusBar.TLabel")
                    finally:
                        self.master.update()
            else:
                self.app.status_bar.config(text="URL không phải là playlist.", style="CustomStatusBar.TLabel")
                self.master.update()
        else:
            self.app.status_bar.config(text="Vui lòng chọn Folder lưu trước khi tải xuống.", style="CustomStatusBar.TLabel")
            self.master.update()

    def download_video(self, format=None):
        video_url = self.yt_url_entry.get()
        save_location = self.save_location_var.get()
        if video_url and save_location:
            # Check playlist
            if 'list=' in video_url:
                self.app.status_bar.config(text="Hãy sử dụng tính năng Download Playlist để tải xuống.", style="CustomStatusBar.TLabel")
                self.master.update()
                return

            # Kiểm tra xem URL có phải là Google Drive không
            if 'drive.google.com' in video_url:
                self.app.status_bar.config(text="Đây là URL Google Drive. Vui lòng sử dụng tính năng 'Lựa chọn chất lượng khác' để tải xuống.", style="CustomStatusBar.TLabel")
                self.master.update()
                return

            # Get video information
            ydl_opts = {}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                title = info.get('title', 'Unknown')

            # Sanitize the title to remove special characters
            sanitized_title = self.sanitize_filename(title)
            output_file = f"{save_location}/{sanitized_title}.%(id)s.%(ext)s"

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
                    'ffmpeg_location': ffmpeg_path,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                self.app.status_bar.config(text="Đã tải xuống.", style="CustomStatusBar.TLabel")
            except Exception as e:
                self.app.status_bar.config(text="Lỗi không xác định, vui lòng thử lại sau.", style="CustomStatusBar.TLabel")
        else:
            self.app.status_bar.config(text="Vui lòng chọn Folder lưu trước khi tải xuống.", style="CustomStatusBar.TLabel")
            self.master.update()

    def sanitize_filename(self, filename):
        """
        Sanitize the filename by removing special characters that may cause issues when saving the file.
        """
        return re.sub(r'[^\w\-_\. ]', '_', filename)

    def open_folder(self):
        save_location = self.save_location_var.get()
        if save_location:
            os.startfile(save_location)
        else:
            self.app.status_bar.config(text="Chưa chọn Folder lưu.", style="CustomStatusBar.TLabel")


    def show_progress(self, progress):
        if progress['status'] == 'downloading':
            percentage = progress['_percent_str']
            download_speed = self.format_bytes(progress.get('speed', 0))
            eta = self.format_time(progress.get('eta', 0))
            if 'total_bytes' in progress:
                self.progress_bar['value'] = progress['downloaded_bytes'] / progress['total_bytes'] * 100
            elif 'total_bytes_estimate' in progress:
                self.progress_bar['value'] = progress['downloaded_bytes'] / progress['total_bytes_estimate'] * 100
            else:
                self.progress_bar['value'] = 0 
            self.app.status_bar.config(text=f"Đang tải xuống... | Tốc độ: {download_speed}/s | Còn lại: {eta}")
            self.master.update()

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
