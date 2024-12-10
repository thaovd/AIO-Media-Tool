import os
import subprocess
from tkinter import ttk, StringVar, filedialog, simpledialog, Toplevel, Text, BOTH, WORD
from tkinter.constants import END
from get_total_time_video import get_video_duration
import sys
import codecs

class MediaConverter:
    def __init__(self, master, app):
        self.master = master
        self.app = app

        # Media Conversion Section
        self.media_conversion_frame = ttk.LabelFrame(master, text="Chuyển Đổi Media, giảm dung lượng", style="CustomLabelFrame.TLabelframe")
        self.media_conversion_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.input_file_label = ttk.Label(self.media_conversion_frame, text="Chọn tệp:", style="CustomSmallLabel.TLabel")
        self.input_file_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.input_file_entry = ttk.Entry(self.media_conversion_frame, style="CustomEntry.TEntry")
        self.input_file_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")

        self.input_file_button = ttk.Button(self.media_conversion_frame, text="Chọn File", command=self.select_input_file, style="CustomButton.TButton")
        self.input_file_button.grid(row=0, column=2, padx=10, pady=5)

        self.output_folder_label = ttk.Label(self.media_conversion_frame, text="Chọn Folder:", style="CustomSmallLabel.TLabel")
        self.output_folder_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.output_folder_entry = ttk.Entry(self.media_conversion_frame, style="CustomEntry.TEntry")
        self.output_folder_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")

        self.output_folder_button = ttk.Button(self.media_conversion_frame, text="Chọn Thư Mục", command=self.select_output_folder, style="CustomButton.TButton")
        self.output_folder_button.grid(row=1, column=2, padx=10, pady=5)

        self.output_format_label = ttk.Label(self.media_conversion_frame, text="Định dạng xuất:", style="CustomSmallLabel.TLabel")
        self.output_format_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.output_format_var = StringVar()
        self.output_format_var.set("mp4")
        self.output_format_dropdown = ttk.Combobox(self.media_conversion_frame, textvariable=self.output_format_var, values=["mp4", "avi", "mov", "webm", "png", "jpg"], state="readonly", style="CustomCombobox.TCombobox")
        self.output_format_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky="we")

        self.bitrate_label = ttk.Label(self.media_conversion_frame, text="Bitrate (kbps):", style="CustomSmallLabel.TLabel")
        self.bitrate_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.bitrate_var = StringVar()
        self.bitrate_var.set("default")
        self.bitrate_dropdown = ttk.Combobox(self.media_conversion_frame, textvariable=self.bitrate_var, values=["default", "1000", "5000", "10000", "15000", "20000", "25000", "30000", "custom"], state="readonly", style="CustomCombobox.TCombobox")
        self.bitrate_dropdown.grid(row=3, column=1, padx=10, pady=5, sticky="we")
        self.bitrate_dropdown.bind("<<ComboboxSelected>>", self.on_bitrate_dropdown_select)

        self.fps_label = ttk.Label(self.media_conversion_frame, text="FPS:", style="CustomSmallLabel.TLabel")
        self.fps_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self.fps_var = StringVar()
        self.fps_var.set("default")
        self.fps_dropdown = ttk.Combobox(self.media_conversion_frame, textvariable=self.fps_var, values=["default", "24", "25", "30", "60", "custom"], state="readonly", style="CustomCombobox.TCombobox")
        self.fps_dropdown.grid(row=4, column=1, padx=10, pady=5, sticky="we")
        self.fps_dropdown.bind("<<ComboboxSelected>>", self.on_fps_dropdown_select)

        self.resolution_label = ttk.Label(self.media_conversion_frame, text="Độ phân giải:", style="CustomSmallLabel.TLabel")
        self.resolution_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")

        self.resolution_var = StringVar()
        self.resolution_var.set("default")
        self.resolution_dropdown = ttk.Combobox(self.media_conversion_frame, textvariable=self.resolution_var, values=["default", "720p", "1080p", "1440p", "2160p", "custom"], state="readonly", style="CustomCombobox.TCombobox")
        self.resolution_dropdown.grid(row=5, column=1, padx=10, pady=5, sticky="we")
        self.resolution_dropdown.bind("<<ComboboxSelected>>", self.on_resolution_dropdown_select)

        self.codec_label = ttk.Label(self.media_conversion_frame, text="Video Codec:", style="CustomSmallLabel.TLabel")
        self.codec_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")

        self.codec_var = StringVar()
        self.codec_var.set("libx264")
        self.codec_dropdown = ttk.Combobox(self.media_conversion_frame, textvariable=self.codec_var, values=["libx264", "libx265", "libvpx-vp9"], state="readonly", style="CustomCombobox.TCombobox")
        self.codec_dropdown.grid(row=6, column=1, padx=10, pady=5, sticky="we")

        self.convert_button = ttk.Button(self.media_conversion_frame, text="Chuyển Đổi", command=self.convert_media, style="CustomButton.TButton")
        self.convert_button.grid(row=7, column=0, padx=10, pady=5)

        self.open_output_folder_button = ttk.Button(self.media_conversion_frame, text="Mở thư mục xuất", command=self.open_output_folder, style="CustomButton.TButton")
        self.open_output_folder_button.grid(row=7, column=1, padx=10, pady=5)

        self.progress_bar = ttk.Progressbar(self.media_conversion_frame, mode='determinate', length=530)
        self.progress_bar.grid(row=8, column=0, columnspan=3, padx=10, pady=10, sticky="we")
        

        # User Guide Button
        self.user_guide_button = ttk.Button(self.media_conversion_frame, text="Hướng Dẫn Sử Dụng", command=self.show_user_guide, style="CustomButton.TButton")
        self.user_guide_button.grid(row=7, column=2, padx=10, pady=5)

    def show_user_guide(self):
        user_guide_window = Toplevel(self.master)
        user_guide_window.title("Hướng Dẫn Sử Dụng")
        user_guide_window.geometry("600x400")

        # Center the window using the `winfo_screenwidth()` and `winfo_screenheight()` methods
        screen_width = user_guide_window.winfo_screenwidth()
        screen_height = user_guide_window.winfo_screenheight()
        window_width = 600
        window_height = 400
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        user_guide_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        user_guide_text = Text(user_guide_window, wrap=WORD)
        user_guide_text.pack(fill=BOTH, expand=True)

        with open("guildeconverter.txt", "r", encoding="utf-8") as file:
            user_guide_content = file.read()
        user_guide_text.insert("1.0", user_guide_content)
        user_guide_text.config(state="disabled")

        # Add a close button
        close_button = ttk.Button(user_guide_window, text="Đóng", command=user_guide_window.destroy)
        close_button.pack(pady=10)

    def on_bitrate_dropdown_select(self, event):
        selected_bitrate = self.bitrate_var.get()
        if selected_bitrate == "custom":
            custom_bitrate = self.get_custom_bitrate()
            if custom_bitrate is not None:
                self.bitrate_var.set(str(custom_bitrate))
            else:
                self.bitrate_var.set("default")  # Revert to default bitrate

    def on_fps_dropdown_select(self, event):
        selected_fps = self.fps_var.get()
        if selected_fps == "custom":
            custom_fps = self.get_custom_fps()
            if custom_fps is not None:
                self.fps_var.set(str(custom_fps))
            else:
                self.fps_var.set("default")  # Revert to default FPS

    def on_resolution_dropdown_select(self, event):
        selected_resolution = self.resolution_var.get()
        if selected_resolution == "custom":
            custom_resolution = self.get_custom_resolution()
            if custom_resolution is not None:
                self.resolution_var.set(custom_resolution)
            else:
                self.resolution_var.set("default")  # Revert to default resolution

    def select_input_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Media Files", "*.mp4;*.avi;*.mov;*.mkv;*.webm;*.jpg;*.png;*.gif")])
        if file_path:
            self.input_file_entry.delete(0, END)
            self.input_file_entry.insert(0, file_path)

    def select_output_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_folder_entry.delete(0, END)
            self.output_folder_entry.insert(0, folder_path)

    def convert_media(self):
        input_file = self.input_file_entry.get()
        output_folder = self.output_folder_entry.get()
        output_format = self.output_format_var.get()
        bitrate = self.bitrate_var.get()
        fps = self.fps_var.get()
        resolution = self.resolution_var.get()
        codec = self.codec_var.get()

        if input_file and output_folder and output_format:
            file_info = os.path.splitext(os.path.basename(input_file))
            filename_without_ext = file_info[0]
            output_file = os.path.join(output_folder, f"{filename_without_ext}.{output_format}")

            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            self.app.status_bar.config(text="Đang chuyển đổi media...", style="CustomStatusBar.TLabel")
            self.master.update()

            try:
                # Get the duration of the input video
                video_duration = get_video_duration(input_file)
                if video_duration is None:
                    self.app.status_bar.config(text="Lỗi: Không thể lấy thời lượng video.", style="CustomStatusBar.TLabel")
                    return

                # Determine the path to the ffmpeg executable
                script_dir = "ffmpeg.exe"
                ffmpeg_path = script_dir
                #script_dir = os.path.dirname(os.path.abspath(__file__))
                #ffmpeg_path = os.path.join(script_dir, 'ffmpeg.exe')

                ffmpeg_command = [ffmpeg_path, "-y", "-hwaccel", "cuda", "-i", input_file]

                if bitrate != "default":
                    if bitrate == "custom":
                        custom_bitrate = self.get_custom_bitrate()
                        if custom_bitrate is not None:
                            ffmpeg_command.extend(["-b:v", f"{custom_bitrate}k"])
                    else:
                        ffmpeg_command.extend(["-b:v", f"{bitrate}k"])

                if fps != "default":
                    if fps == "custom":
                        custom_fps = self.get_custom_fps()
                        if custom_fps is not None:
                            ffmpeg_command.extend(["-r", f"{custom_fps}"])
                    else:
                        ffmpeg_command.extend(["-r", f"{fps}"])

                if resolution != "default":
                    if resolution == "custom":
                        custom_resolution = self.get_custom_resolution()
                        if custom_resolution is not None:
                            ffmpeg_command.extend(["-s", custom_resolution])
                    else:
                        # Check if the selected resolution is valid
                        if resolution == "1080p":
                            ffmpeg_command.extend(["-s", "1920x1080"])
                        elif resolution == "720p":
                            ffmpeg_command.extend(["-s", "1280x720"])
                        elif resolution == "1440p":
                            ffmpeg_command.extend(["-s", "2560x1440"])
                        elif resolution == "2160p":
                            ffmpeg_command.extend(["-s", "3840x2160"])
                        else:
                            self.app.status_bar.config(text="Lỗi: Độ phân giải không hợp lệ.", style="CustomStatusBar.TLabel")
                            return

                ffmpeg_command.extend(["-c:v", codec, "-preset", "medium", "-crf", "28", "-c:a", "copy", output_file])

                # Run the ffmpeg command and monitor the progress
                process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
                total_duration = video_duration.total_seconds()
                current_duration = 0
                while True:
                    try:
                        output = process.stderr.readline().strip()
                    except UnicodeDecodeError:
                        # Handle the UnicodeDecodeError by using a different encoding
                        output = process.stderr.readline().decode('utf-8', errors='replace').strip()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        if output.startswith("frame="):
                            # Extract the current duration from the ffmpeg output
                            current_duration = float(output.split("time=")[1].split(" ")[0].split(":")[0]) * 3600 + \
                                            float(output.split("time=")[1].split(" ")[0].split(":")[1]) * 60 + \
                                            float(output.split("time=")[1].split(" ")[0].split(":")[2])
                            progress_percentage = (current_duration / total_duration) * 100
                            self.progress_bar.config(value=progress_percentage)
                            self.master.update()

                returncode = process.poll()
                if returncode == 0:
                    self.app.status_bar.config(text=f"Đã chuyển đổi thành công. File lưu tại: {output_file}", style="CustomStatusBar.TLabel")
                else:
                    self.app.status_bar.config(text="Lỗi chuyển đổi, vui lòng kiểm tra lại.", style="CustomStatusBar.TLabel")
            except subprocess.CalledProcessError as e:
                self.app.status_bar.config(text="Lỗi chuyển đổi, vui lòng kiểm tra lại.", style="CustomStatusBar.TLabel")
            finally:
                self.master.update()


    def get_custom_bitrate(self):
        custom_bitrate = simpledialog.askstring("Tuỳ chỉnh Bitrate", "Nhập bitrate tùy chỉnh (kbps):")
        if custom_bitrate and custom_bitrate.isdigit():
            return int(custom_bitrate)
        else:
            return None  # Return None if no valid input is provided

    def get_custom_fps(self):
        custom_fps = simpledialog.askstring("Tuỳ chỉnh FPS", "Nhập FPS tùy chỉnh:")
        if custom_fps and custom_fps.isdigit():
            return int(custom_fps)
        else:
            return None  # Return None if no valid input is provided

    def get_custom_resolution(self):
        custom_resolution = simpledialog.askstring("Tuỳ chỉnh Độ phân giải", "Nhập độ phân giải tùy chỉnh (WIDTHxHEIGHT):")
        if custom_resolution and "x" in custom_resolution:
            return custom_resolution
        else:
            return None  # Return None if no valid input is provided

    def open_output_folder(self):

        output_folder = self.output_folder_entry.get()
        if os.path.exists(output_folder):
            if os.name == 'nt':  # Windows
                os.startfile(output_folder)
        else:
            self.app.status_bar.config(text="Output folder does not exist.", style="CustomStatusBar.TLabel")


