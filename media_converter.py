import os
import subprocess
from tkinter import ttk, StringVar, filedialog, simpledialog
from tkinter.constants import END

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

        self.output_format_label = ttk.Label(self.media_conversion_frame, text="Định dạng xuất:", style="CustomSmallLabel.TLabel")
        self.output_format_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.output_format_var = StringVar()
        self.output_format_var.set("mp4")
        self.output_format_dropdown = ttk.Combobox(self.media_conversion_frame, textvariable=self.output_format_var, values=["mp4", "avi", "mov", "webm", "png", "jpg"], state="readonly", style="CustomCombobox.TCombobox")
        self.output_format_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="we")

        self.bitrate_label = ttk.Label(self.media_conversion_frame, text="Bitrate (kbps):", style="CustomSmallLabel.TLabel")
        self.bitrate_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.bitrate_var = StringVar()
        self.bitrate_var.set("default")
        self.bitrate_dropdown = ttk.Combobox(self.media_conversion_frame, textvariable=self.bitrate_var, values=["default", "1000", "5000", "10000", "15000", "20000", "25000", "30000", "custom"], state="readonly", style="CustomCombobox.TCombobox")
        self.bitrate_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky="we")
        self.bitrate_dropdown.bind("<<ComboboxSelected>>", self.on_bitrate_dropdown_select)

        self.convert_button = ttk.Button(self.media_conversion_frame, text="Chuyển Đổi", command=self.convert_media, style="CustomButton.TButton")
        self.convert_button.grid(row=3, column=0, padx=10, pady=5)

        self.open_output_folder_button = ttk.Button(self.media_conversion_frame, text="Mở thư mục xuất", command=lambda: self.open_folder("converted"), style="CustomButton.TButton")
        self.open_output_folder_button.grid(row=3, column=1, padx=10, pady=5)

    def on_bitrate_dropdown_select(self, event):
        """
        Handles the event when the user selects an option from the bitrate dropdown.
        If the user selects the "custom" option, it prompts the user to enter a custom bitrate value.
        If the user does not accept the custom bitrate or cancels, it returns to the default selection.
        """
        selected_bitrate = self.bitrate_var.get()
        if selected_bitrate == "custom":
            custom_bitrate = self.get_custom_bitrate()
            if custom_bitrate is not None:
                self.bitrate_var.set(str(custom_bitrate))
            else:
                self.bitrate_var.set("default")  # Revert to default bitrate

    def select_input_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Media Files", "*.mp4;*.avi;*.mov;*.webm;*.jpg;*.png;*.gif")])
        if file_path:
            self.input_file_entry.delete(0, END)
            self.input_file_entry.insert(0, file_path)

    def convert_media(self):
        input_file = self.input_file_entry.get()
        output_format = self.output_format_var.get()
        bitrate = self.bitrate_var.get()

        if input_file and output_format:
            file_info = os.path.splitext(os.path.basename(input_file))
            filename_without_ext = file_info[0]
            output_file = f"./converted/{filename_without_ext}.{output_format}"

            if not os.path.exists("./converted"):
                os.makedirs("./converted")

            self.app.status_bar.config(text="Đang chuyển đổi media...", style="CustomStatusBar.TLabel")
            self.master.update()

            try:
                if bitrate == "default":
                    subprocess.run(["ffmpeg", "-y", "-vsync", "0", "-hwaccel", "cuda", "-i", input_file, "-init_hw_device", "qsv=hw", output_file], check=True)
                elif bitrate == "custom":
                    custom_bitrate = self.bitrate_var.get()
                    subprocess.run(["ffmpeg", "-y", "-vsync", "0", "-hwaccel", "cuda", "-i", input_file, "-b:v", f"{custom_bitrate}k", "-init_hw_device", "qsv=hw", output_file], check=True)
                else:
                    subprocess.run(["ffmpeg", "-y", "-vsync", "0", "-hwaccel", "cuda", "-i", input_file, "-b:v", f"{bitrate}k", "-init_hw_device", "qsv=hw", output_file], check=True)
                self.app.status_bar.config(text=f"Đã chuyển đổi thành công. File lưu tại: {output_file}", style="CustomStatusBar.TLabel")
            except subprocess.CalledProcessError as e:
                self.app.status_bar.config(text="Lỗi chuyển đổi, vui lòng kiểm tra lại.", style="CustomStatusBar.TLabel")
            finally:
                self.master.update()

    def get_custom_bitrate(self):
        """
        Prompts the user to enter a custom bitrate value.
        Returns the custom bitrate value as an integer, or None if the user does not accept the custom bitrate or cancels.
        """
        custom_bitrate = simpledialog.askstring("Custom Bitrate", "Nhập bitrate tùy chỉnh (kbps):")
        if custom_bitrate and custom_bitrate.isdigit():
            return int(custom_bitrate)
        else:
            return None  # Return None if no valid input is provided

    def open_folder(self, folder_name):
        folder_path = os.path.join(os.getcwd(), folder_name)
        if os.path.exists(folder_path):
            subprocess.Popen(["explorer", folder_path])
