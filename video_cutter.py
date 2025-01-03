import os
import subprocess
from tkinter import ttk, StringVar, filedialog
from tkinter.constants import END
from get_total_time_video import get_video_duration
from moviepy import VideoFileClip
import sys
import platform
from tkinter import messagebox

class VideoCutter:
    def __init__(self, master, app):
        self.master = master
        self.app = app

        # Video Cutting Select Frame
        self.video_cutting_frame = ttk.LabelFrame(master, text="Cắt Video Nhanh", style="CustomLabelFrame.TLabelframe")
        self.video_cutting_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.file_label = ttk.Label(self.video_cutting_frame, text="Chọn tệp:", style="CustomSmallLabel.TLabel")
        self.file_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.file_entry = ttk.Entry(self.video_cutting_frame, style="CustomEntry.TEntry", width=27)
        self.file_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")

        self.file_button = ttk.Button(self.video_cutting_frame, text="Chọn File", command=self.select_file, style="CustomButton.TButton")
        self.file_button.grid(row=0, column=2, padx=10, pady=5)

        # Save location Select Frame
        self.save_label = ttk.Label(self.video_cutting_frame, text="Chọn nơi lưu:", style="CustomSmallLabel.TLabel")
        self.save_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.save_entry = ttk.Entry(self.video_cutting_frame, style="CustomEntry.TEntry")
        self.save_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")

        self.save_button = ttk.Button(self.video_cutting_frame, text="Chọn Folder", command=self.select_save_location, style="CustomButton.TButton")
        self.save_button.grid(row=1, column=2, padx=10, pady=5)

        # Start time Frame
        self.start_label = ttk.Label(self.video_cutting_frame, text="Bắt đầu:", style="CustomSmallLabel.TLabel")
        self.start_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.start_time = StringVar()
        self.start_time.set("00:00:00")
        self.start_entry = ttk.Entry(self.video_cutting_frame, textvariable=self.start_time, style="CustomEntry.TEntry")
        self.start_entry.grid(row=2, column=1, padx=10, pady=5, sticky="we")

        self.start_hour_button = ttk.Button(self.video_cutting_frame, text="↑", command=lambda: self.increment_time("start", "hour"), style="CustomButton.TButton")
        self.start_hour_button.grid(row=2, column=2, padx=5, pady=5)
        self.start_minute_button = ttk.Button(self.video_cutting_frame, text="↑", command=lambda: self.increment_time("start", "minute"), style="CustomButton.TButton")
        self.start_minute_button.grid(row=2, column=3, padx=5, pady=5)
        self.start_second_button = ttk.Button(self.video_cutting_frame, text="↑", command=lambda: self.increment_time("start", "second"), style="CustomButton.TButton")
        self.start_second_button.grid(row=2, column=4, padx=5, pady=5)

        self.start_hour_button = ttk.Button(self.video_cutting_frame, text="↓", command=lambda: self.decrement_time("start", "hour"), style="CustomButton.TButton")
        self.start_hour_button.grid(row=3, column=2, padx=5, pady=5)
        self.start_minute_button = ttk.Button(self.video_cutting_frame, text="↓", command=lambda: self.decrement_time("start", "minute"), style="CustomButton.TButton")
        self.start_minute_button.grid(row=3, column=3, padx=5, pady=5)
        self.start_second_button = ttk.Button(self.video_cutting_frame, text="↓", command=lambda: self.decrement_time("start", "second"), style="CustomButton.TButton")
        self.start_second_button.grid(row=3, column=4, padx=5, pady=5)

        # End time Frame
        self.end_label = ttk.Label(self.video_cutting_frame, text="Kết thúc:", style="CustomSmallLabel.TLabel")
        self.end_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self.end_time = StringVar()
        self.end_time.set("00:00:00")
        self.end_entry = ttk.Entry(self.video_cutting_frame, textvariable=self.end_time, style="CustomEntry.TEntry")
        self.end_entry.grid(row=4, column=1, padx=10, pady=5, sticky="we")

        self.end_hour_button = ttk.Button(self.video_cutting_frame, text="↑", command=lambda: self.increment_time("end", "hour"), style="CustomButton.TButton")
        self.end_hour_button.grid(row=4, column=2, padx=5, pady=5)
        self.end_minute_button = ttk.Button(self.video_cutting_frame, text="↑", command=lambda: self.increment_time("end", "minute"), style="CustomButton.TButton")
        self.end_minute_button.grid(row=4, column=3, padx=5, pady=5)
        self.end_second_button = ttk.Button(self.video_cutting_frame, text="↑", command=lambda: self.increment_time("end", "second"), style="CustomButton.TButton")
        self.end_second_button.grid(row=4, column=4, padx=5, pady=5)

        self.end_hour_button = ttk.Button(self.video_cutting_frame, text="↓", command=lambda: self.decrement_time("end", "hour"), style="CustomButton.TButton")
        self.end_hour_button.grid(row=5, column=2, padx=5, pady=5)
        self.end_minute_button = ttk.Button(self.video_cutting_frame, text="↓", command=lambda: self.decrement_time("end", "minute"), style="CustomButton.TButton")
        self.end_minute_button.grid(row=5, column=3, padx=5, pady=5)
        self.end_second_button = ttk.Button(self.video_cutting_frame, text="↓", command=lambda: self.decrement_time("end", "second"), style="CustomButton.TButton")
        self.end_second_button.grid(row=5, column=4, padx=5, pady=5)

        # Timeline Frame
        self.timeline_frame = ttk.Frame(self.video_cutting_frame)
        self.timeline_frame.grid(row=6, column=0, columnspan=5, padx=10, pady=10)

        self.start_timeline = ttk.Scale(self.timeline_frame, from_=0, to=100, orient="horizontal", command=self.update_start_time)
        self.start_timeline.pack(side="left", fill="x", expand=True)

        self.end_timeline = ttk.Scale(self.timeline_frame, from_=0, to=100, orient="horizontal", command=self.update_end_time)
        self.end_timeline.pack(side="left", fill="x", expand=True)

        self.cut_button = ttk.Button(self.video_cutting_frame, text="Chạy", command=self.cut_video, style="CustomButton.TButton")
        self.cut_button.grid(row=7, column=0, padx=10, pady=5)

        self.open_folder_button = ttk.Button(self.video_cutting_frame, text="Mở thư mục xuất", command=self.open_output_folder, style="CustomButton.TButton")
        self.open_folder_button.grid(row=7, column=1, padx=10, pady=5)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(self.video_cutting_frame, mode='determinate', length=300)
        self.progress_bar.grid(row=8, column=0, columnspan=5, padx=10, pady=10, sticky="we")

    # Khối xử lý chọn file input
    def select_file(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv;*.webm")])
        if file_paths:
            self.file_entry.delete(0, END)
            self.file_entry.insert(0, ";".join(file_paths))
            self.update_timeline_bars(file_paths[0])

    # Khối xử lý chọn Folder output
    def select_save_location(self):
        save_location = filedialog.askdirectory()
        if save_location:
            self.save_entry.delete(0, END)
            self.save_entry.insert(0, save_location)

    # Khối xử lý update time khi kéo timeline & update total time video
    def update_timeline_bars(self, file_path):
        self.total_duration = get_video_duration(file_path)
        if self.total_duration:
            self.start_timeline.config(to=int(self.total_duration.total_seconds()))
            self.end_timeline.config(to=int(self.total_duration.total_seconds()))
        else:
            self.start_timeline.config(to=100)
            self.end_timeline.config(to=100)

    # Khối xử lý update time gửi lên ô start time
    def update_start_time(self, value):
        start_time = int(float(value))
        self.start_time.set(f"{start_time//3600:02d}:{(start_time//60)%60:02d}:{start_time%60:02d}")
    # tương tự với end time
    def update_end_time(self, value):
        end_time = int(float(value))
        self.end_time.set(f"{end_time//3600:02d}:{(end_time//60)%60:02d}:{end_time%60:02d}")

    # Khối xử lý cắt video
    def cut_video(self):
        file_paths = self.file_entry.get().split(";")
        save_location = self.save_entry.get()
        start_time = self.start_time.get()
        end_time = self.end_time.get()

        if file_paths and save_location and start_time and end_time:
            for file_path in file_paths:
                file_info = os.path.splitext(os.path.basename(file_path))
                filename_without_ext = file_info[0]
                output_file = os.path.join(save_location, f"{filename_without_ext}_cut{file_info[1]}")

                # Kiểm tra xem file output đã tồn tại chưa
                if os.path.exists(output_file):
                    # Cảnh báo ghi đè
                    overwrite_file = messagebox.askyesno("Cảnh báo ghi đè", f"File '{os.path.basename(output_file)}' đã tồn tại trong thư mục. Bạn có muốn ghi đè không?")
                    if not overwrite_file:
                        continue

                self.app.status_bar.config(text="Đang cắt Video...", style="CustomStatusBar.TLabel")
                self.master.update()

                try:
                    # Determine the path to the ffmpeg executable
                    script_dir = "ffmpeg.exe"
                    ffmpeg_path = script_dir
                    if platform.system() == 'Windows':

                    # Ẩn ffmpeg console
                        if sys.platform.startswith('win'):
                            startupinfo = subprocess.STARTUPINFO()
                            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                            process = subprocess.Popen([ffmpeg_path, "-ss", start_time, "-to", end_time, "-y", "-i", file_path, "-acodec", "copy", "-vcodec", "copy", "-async", "1", output_file], startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, errors='replace')
                        else:
                            process = subprocess.Popen([ffmpeg_path, "-ss", start_time, "-to", end_time, "-y", "-i", file_path, "-acodec", "copy", "-vcodec", "copy", "-async", "1", output_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, errors='replace')
                        
                    
                    # Theo dõi và cập nhật progress bar
                    current_duration = 0
                    while True:
                        try:
                            output = process.stderr.readline()
                        except UnicodeDecodeError:
                            # Xử lý UnicodeDecodeError bằng cách thay thế các ký tự có lỗi
                            output = process.stderr.readline(errors='replace')
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            if output.startswith("frame="):
                                # Extract the current duration from the ffmpeg output
                                current_duration = float(output.split("time=")[1].split(" ")[0].split(":")[0]) * 3600 + \
                                                   float(output.split("time=")[1].split(" ")[0].split(":")[1]) * 60 + \
                                                   float(output.split("time=")[1].split(" ")[0].split(":")[2])
                                progress_percentage = (current_duration / self.total_duration.total_seconds()) * 100
                                self.progress_bar.config(value=progress_percentage)
                                self.app.status_bar.config(text=f"Đang cắt Video... {progress_percentage:.2f}%", style="CustomStatusBar.TLabel")
                                self.master.update()

                    returncode = process.poll()
                    if returncode == 0:
                        self.app.status_bar.config(text=f"Cắt Video hoàn thành, Video được lưu tại: {output_file}", style="CustomStatusBar.TLabel")
                    else:
                        self.app.status_bar.config(text="Lỗi cắt video. Vui lòng kiểm tra các thông số đầu vào.", style="CustomStatusBar.TLabel")
                except subprocess.CalledProcessError as e:
                    self.app.status_bar.config(text="Lỗi cắt video. Vui lòng kiểm tra các thông số đầu vào.", style="CustomStatusBar.TLabel")
                except UnicodeDecodeError as e:
                    # Xử lý UnicodeDecodeError bằng cách thay thế các ký tự có lỗi
                    self.app.status_bar.config(text="Lỗi cắt video. Vui lòng kiểm tra các thông số đầu vào.", style="CustomStatusBar.TLabel")
                finally:
                    self.master.update()
                    self.progress_bar.config(value=0)

    #Xử lý hiển thị time chờ bằng giờ phút giây tuỳ trường hợp
    def increment_time(self, time_type, time_part):
        time_var = getattr(self, f"{time_type}_time")
        hours, minutes, seconds = map(int, time_var.get().split(":"))
        if time_part == "hour":
            hours = (hours + 1) % 24
        elif time_part == "minute":
            minutes = (minutes + 1) % 60
        elif time_part == "second":
            seconds = (seconds + 1) % 60
        time_var.set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    def decrement_time(self, time_type, time_part):
        time_var = getattr(self, f"{time_type}_time")
        hours, minutes, seconds = map(int, time_var.get().split(":"))
        if time_part == "hour":
            hours = (hours - 1) % 24
        elif time_part == "minute":
            minutes = (minutes - 1) % 60
        elif time_part == "second":
            seconds = (seconds - 1) % 60
        time_var.set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    #Xử lý open folder
    def open_output_folder(self):
        save_location = self.save_entry.get()
        if os.path.exists(save_location):
            if platform.system() == 'Windows':
                os.startfile(save_location)
            elif platform.system() == 'Darwin':
                subprocess.Popen(['open', save_location])
            else:
                subprocess.Popen(['xdg-open', save_location])
        else:
            self.app.status_bar.config(text="Chưa chọn Folder lưu.", style="CustomStatusBar.TLabel")
            self.master.update()

