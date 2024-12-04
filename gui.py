import os
from tkinter import Tk, ttk, StringVar
from tkinter.constants import END
from video_cutter import VideoCutter
from yt_downloader import YTDownloader
from media_converter import MediaConverter
from ggdrive_private_video_download import GGDriveDownloader
import tkinter as tk
from tkinter.font import Font
import json
from tkinter.messagebox import showinfo
import time

class AIOMediaTool:
    def __init__(self, master):
        self.master = master
        master.title("AIO Media Tool")
        master.geometry("650x590")
        master.minsize(650, 580) 
        master.resizable(False, False)
        master.configure(bg="#f5f5f5")

        # Set icon ứng dụng
        try:
            self.master.iconbitmap(os.path.join(os.path.dirname(__file__), 'icon.ico'))
        except:
            print("Không load được icon.")

        # Tab lựa chọn tính năng
        self.feature_selection_tab = ttk.Notebook(master)
        self.feature_selection_tab.pack(fill="both", expand=True, padx=20, pady=20)

        # Video Cutter tab
        self.video_cutter_tab = ttk.Frame(self.feature_selection_tab)
        self.feature_selection_tab.add(self.video_cutter_tab, text="Cắt Video")
        self.video_cutter = VideoCutter(self.video_cutter_tab, self)

        # YouTube Downloader tab
        self.yt_downloader_tab = ttk.Frame(self.feature_selection_tab)
        self.feature_selection_tab.add(self.yt_downloader_tab, text="Social DL")
        self.yt_downloader = YTDownloader(self.yt_downloader_tab, self)

        # Google Drive Downloader tab
        self.ggdrive_downloader_tab = ttk.Frame(self.feature_selection_tab)
        self.feature_selection_tab.add(self.ggdrive_downloader_tab, text="GG Drive Video DL")
        self.ggdrive_downloader = GGDriveDownloader(self.ggdrive_downloader_tab, self)

        # Media Converter tab
        self.media_converter_tab = ttk.Frame(self.feature_selection_tab)
        self.feature_selection_tab.add(self.media_converter_tab, text="Media Converter")
        self.media_converter = MediaConverter(self.media_converter_tab, self)

        # Settings tab
        self.settings_tab = ttk.Frame(self.feature_selection_tab)
        self.feature_selection_tab.add(self.settings_tab, text="Settings")
        self.create_settings_tab()

        # Status Bar
        self.status_bar_font = Font(family="Roboto", size=11)
        self.status_bar = ttk.Label(master, text="", anchor="w", style="StatusBar.TLabel")
        self.status_bar.pack(side="bottom", fill="x", padx=20, pady=10)
        self.status_bar.config(font=self.status_bar_font)
        self.status_bar.configure(background="#f5f5f5")
        self.status_bar_update_time = time.time()  # Initialize the status bar update time

        # Version
        self.version_label = ttk.Label(master, text="Version 2.4.1 @ vuthao.id.vn", anchor="e", style="VersionLabel.TLabel")
        self.version_label.pack(side="bottom", fill="x", padx=10, pady=0)
        self.version_label.configure(background="#f5f5f5")

        # Apply custom styles
        self.apply_custom_styles()

        # Load settings trong config.json
        self.load_settings()

    def create_settings_tab(self):
        # Giao diện cài đặt
        self.startup_tab_var = StringVar()
        self.startup_tab_label = ttk.Label(self.settings_tab, text="Trang khởi động mặc định:")
        self.startup_tab_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.startup_tab_combobox = ttk.Combobox(self.settings_tab, textvariable=self.startup_tab_var, state="readonly")
        self.startup_tab_combobox["values"] = ["Cắt Video", "Social DL", "GG Drive Video DL", "Media Converter"]
        self.startup_tab_combobox.grid(row=0, column=1, padx=10, pady=10)

        self.save_settings_button = ttk.Button(self.settings_tab, text="Save Settings", command=self.save_settings)
        self.save_settings_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    def load_settings(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                self.startup_tab_var.set(config["startup_tab"])
                self.feature_selection_tab.select(self.get_tab_by_name(config["startup_tab"]))
        except FileNotFoundError:
            # Nếu config.json không có, sử dụng giá trị mặc định
            self.startup_tab_var.set("Cắt Video")
            self.feature_selection_tab.select(self.video_cutter_tab)

    def get_tab_by_name(self, tab_name):
        for i in range(self.feature_selection_tab.index("end")):
            if self.feature_selection_tab.tab(i, "text") == tab_name:
                return self.feature_selection_tab.tabs()[i]
        return None

    def save_settings(self):
        config = {
            "startup_tab": self.startup_tab_var.get()
        }
        with open("config.json", "w") as f:
            json.dump(config, f)
        self.status_bar.config(text="Cài đặt đã được lưu.")
        showinfo("Cài đặt đã được lưu.", "Cài đặt đã được lưu! Vui lòng khởi động lại ứng dụng để áp dụng cài đặt mới.")

    def apply_custom_styles(self):
        # Xác định custom styles
        self.master.style = ttk.Style()
        self.master.style.configure("StatusBar.TLabel", background="#f5f5f5", foreground="black")
        self.master.style.configure("VersionLabel.TLabel", background="#f5f5f5", foreground="gray")

    def update_status_bar(self, text):
        self.status_bar.config(text=text)
        self.status_bar_update_time = time.time()

root = Tk()
app = AIOMediaTool(root)
root.mainloop()
