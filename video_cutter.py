import os
import subprocess
from tkinter import ttk, StringVar, filedialog
from tkinter.constants import END

class VideoCutter:
    def __init__(self, master, app):
        self.master = master
        self.app = app

        # Video Cutting Section
        self.video_cutting_frame = ttk.LabelFrame(master, text="Cắt Video Nhanh", style="CustomLabelFrame.TLabelframe")
        self.video_cutting_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.file_label = ttk.Label(self.video_cutting_frame, text="Chọn tệp:", style="CustomSmallLabel.TLabel")
        self.file_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.file_entry = ttk.Entry(self.video_cutting_frame, style="CustomEntry.TEntry")
        self.file_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")

        self.file_button = ttk.Button(self.video_cutting_frame, text="Chọn File", command=self.select_file, style="CustomButton.TButton")
        self.file_button.grid(row=0, column=2, padx=10, pady=5)

        self.start_label = ttk.Label(self.video_cutting_frame, text="Bắt đầu:", style="CustomSmallLabel.TLabel")
        self.start_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.start_time = StringVar()
        self.start_time.set("00:00:00")
        self.start_entry = ttk.Entry(self.video_cutting_frame, textvariable=self.start_time, style="CustomEntry.TEntry")
        self.start_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")

        self.start_hour_button = ttk.Button(self.video_cutting_frame, text="↑", command=lambda: self.increment_time("start", "hour"), style="CustomButton.TButton")
        self.start_hour_button.grid(row=1, column=2, padx=5, pady=5)
        self.start_minute_button = ttk.Button(self.video_cutting_frame, text="↑", command=lambda: self.increment_time("start", "minute"), style="CustomButton.TButton")
        self.start_minute_button.grid(row=1, column=3, padx=5, pady=5)
        self.start_second_button = ttk.Button(self.video_cutting_frame, text="↑", command=lambda: self.increment_time("start", "second"), style="CustomButton.TButton")
        self.start_second_button.grid(row=1, column=4, padx=5, pady=5)

        self.start_hour_button = ttk.Button(self.video_cutting_frame, text="↓", command=lambda: self.decrement_time("start", "hour"), style="CustomButton.TButton")
        self.start_hour_button.grid(row=2, column=2, padx=5, pady=5)
        self.start_minute_button = ttk.Button(self.video_cutting_frame, text="↓", command=lambda: self.decrement_time("start", "minute"), style="CustomButton.TButton")
        self.start_minute_button.grid(row=2, column=3, padx=5, pady=5)
        self.start_second_button = ttk.Button(self.video_cutting_frame, text="↓", command=lambda: self.decrement_time("start", "second"), style="CustomButton.TButton")
        self.start_second_button.grid(row=2, column=4, padx=5, pady=5)

        self.end_label = ttk.Label(self.video_cutting_frame, text="Kết thúc:", style="CustomSmallLabel.TLabel")
        self.end_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.end_time = StringVar()
        self.end_time.set("00:00:00")
        self.end_entry = ttk.Entry(self.video_cutting_frame, textvariable=self.end_time, style="CustomEntry.TEntry")
        self.end_entry.grid(row=3, column=1, padx=10, pady=5, sticky="we")

        self.end_hour_button = ttk.Button(self.video_cutting_frame, text="↑", command=lambda: self.increment_time("end", "hour"), style="CustomButton.TButton")
        self.end_hour_button.grid(row=3, column=2, padx=5, pady=5)
        self.end_minute_button = ttk.Button(self.video_cutting_frame, text="↑", command=lambda: self.increment_time("end", "minute"), style="CustomButton.TButton")
        self.end_minute_button.grid(row=3, column=3, padx=5, pady=5)
        self.end_second_button = ttk.Button(self.video_cutting_frame, text="↑", command=lambda: self.increment_time("end", "second"), style="CustomButton.TButton")
        self.end_second_button.grid(row=3, column=4, padx=5, pady=5)

        self.end_hour_button = ttk.Button(self.video_cutting_frame, text="↓", command=lambda: self.decrement_time("end", "hour"), style="CustomButton.TButton")
        self.end_hour_button.grid(row=4, column=2, padx=5, pady=5)
        self.end_minute_button = ttk.Button(self.video_cutting_frame, text="↓", command=lambda: self.decrement_time("end", "minute"), style="CustomButton.TButton")
        self.end_minute_button.grid(row=4, column=3, padx=5, pady=5)
        self.end_second_button = ttk.Button(self.video_cutting_frame, text="↓", command=lambda: self.decrement_time("end", "second"), style="CustomButton.TButton")
        self.end_second_button.grid(row=4, column=4, padx=5, pady=5)

        self.cut_button = ttk.Button(self.video_cutting_frame, text="Chạy", command=self.cut_video, style="CustomButton.TButton")
        self.cut_button.grid(row=5, column=0, padx=10, pady=5)

        self.open_folder_button = ttk.Button(self.video_cutting_frame, text="Mở thư mục xuất", command=lambda: self.open_folder("exported"), style="CustomButton.TButton")
        self.open_folder_button.grid(row=5, column=1, padx=10, pady=5)

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4")])
        if file_path:
            self.file_entry.delete(0, END)
            self.file_entry.insert(0, file_path)

    def cut_video(self):
        file_path = self.file_entry.get()
        start_time = self.start_time.get()
        end_time = self.end_time.get()

        if file_path and start_time and end_time:
            file_info = os.path.splitext(os.path.basename(file_path))
            filename_without_ext = file_info[0]
            output_file = f"./exported/{filename_without_ext}_cut.mp4"

            if not os.path.exists("./exported"):
                os.makedirs("./exported")

            self.app.status_bar.config(text="Đang cắt Video...", style="CustomStatusBar.TLabel")
            self.master.update()

            try:
                subprocess.run(["ffmpeg", "-ss", start_time, "-to", end_time, "-i", file_path, "-acodec", "copy", "-vcodec", "copy", "-async", "1", output_file], check=True)
                self.app.status_bar.config(text=f"Đã hoàn thành cut, Video được lưu tại: {output_file}", style="CustomStatusBar.TLabel")
            except subprocess.CalledProcessError as e:
                self.app.status_bar.config(text="Lỗi cắt video. Vui lòng kiểm tra các thông số đầu vào.", style="CustomStatusBar.TLabel")
            finally:
                self.master.update()

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

    def open_folder(self, folder_name):
        folder_path = os.path.join(os.getcwd(), folder_name)
        if os.path.exists(folder_path):
            subprocess.Popen(["explorer", folder_path])

