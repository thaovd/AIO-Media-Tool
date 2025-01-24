import os
import subprocess
import sys
from tkinter import Tk, ttk, StringVar
from tkinter.constants import END
from video_cutter import VideoCutter
from yt_downloader import YTDownloader
from media_converter import MediaConverter
import tkinter as tk
from tkinter.font import Font
import json
from tkinter.messagebox import showinfo
import time
from autosub import AutoSubGUI
from shazam import ShazamGUI
from genmini_sub import AutoSubApp
from renamer import BatchFileRenamer  # Import the BatchFileRenamer class
import multiprocessing
import google.generativeai as genai
import webbrowser


class AIOMediaTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AIO Media Tool")
        self.geometry("650x670")
        self.minsize(650, 580) 
        self.resizable(False, False)
        self.configure(bg="#f5f5f5")

        # Set icon ứng dụng
        try:
            self.iconbitmap(os.path.join(os.path.dirname(__file__), 'icon.ico'))       
        except:
            print("Không load được icon.")

        # Tab lựa chọn tính năng
        self.feature_selection_tab = ttk.Notebook(self)
        self.feature_selection_tab.pack(fill="both", expand=True, padx=20, pady=20)

        # Video Cutter tab
        self.video_cutter_tab = ttk.Frame(self.feature_selection_tab)
        self.feature_selection_tab.add(self.video_cutter_tab, text="✂ Cắt Video")
        self.video_cutter = VideoCutter(self.video_cutter_tab, self)

        # YouTube Downloader tab
        self.yt_downloader_tab = ttk.Frame(self.feature_selection_tab)
        self.feature_selection_tab.add(self.yt_downloader_tab, text="⬇ Social DL")
        self.yt_downloader = YTDownloader(self.yt_downloader_tab, self)

        # Media Converter tab
        self.media_converter_tab = ttk.Frame(self.feature_selection_tab)
        self.feature_selection_tab.add(self.media_converter_tab, text="⇄ Converter")
        self.media_converter = MediaConverter(self.media_converter_tab, self)

        # AutoSub tab
        self.autosub_tab = ttk.Frame(self.feature_selection_tab)
        self.feature_selection_tab.add(self.autosub_tab, text="💬 AutoSub")
        self.autosub = AutoSubGUI(self.autosub_tab, self.update_status_bar)

        # Genmini Sub tab
        self.genmini_sub_tab = ttk.Frame(self.feature_selection_tab)
        self.feature_selection_tab.add(self.genmini_sub_tab, text="✨Genmini Sub")
        self.genmini_sub = AutoSubApp(self.genmini_sub_tab, self)  # Pass the AIOMediaTool instance to AutoSubApp

        # Shazam tab
        self.shazam_tab = ttk.Frame(self.feature_selection_tab)
        self.feature_selection_tab.add(self.shazam_tab, text="🔍 Tìm nhạc")
        self.shazam = ShazamGUI(self.shazam_tab)

        # Renamer tab
        self.renamer_tab = ttk.Frame(self.feature_selection_tab)
        self.feature_selection_tab.add(self.renamer_tab, text="✎ Renamer")
        self.renamer = BatchFileRenamer(self.renamer_tab)

        # Settings tab
        self.settings_tab = ttk.Frame(self.feature_selection_tab)
        self.feature_selection_tab.add(self.settings_tab, text="⚙️ Settings")
        self.create_settings_tab()

        # Status Bar
        self.status_bar_font = Font(family="Roboto", size=11)
        self.status_bar = ttk.Label(self, text="", anchor="w", style="StatusBar.TLabel")
        self.status_bar.pack(side="bottom", fill="x", padx=20, pady=10)
        self.status_bar.config(font=self.status_bar_font)
        self.status_bar.configure(background="#f5f5f5")
        self.status_bar_update_time = time.time()

        # Version
        self.version = "2.7.6"
        self.version_label = ttk.Label(self, text=f"Version {self.version} @ vuthao.id.vn", anchor="e", style="VersionLabel.TLabel")
        self.version_label.pack(side="bottom", fill="x", padx=10, pady=0)
        self.version_label.configure(background="#f5f5f5")

        # Bind version label click event
        self.version_label.bind("<Button-1>", lambda event: webbrowser.open("https://vuthao.id.vn/aio-tool-media-phan-mem-tong-hop-cac-cong-cu-nhanh-tien-loi-danh-cho-editer-creative/"))


        # Apply custom styles
        self.apply_custom_styles()

        # Load settings trong config.json
        self.load_settings()

    def create_settings_tab(self):
        # Existing settings tab code
        self.startup_tab_var = StringVar()
        self.startup_tab_label = ttk.Label(self.settings_tab, text="Trang khởi động mặc định:")
        self.startup_tab_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.startup_tab_combobox = ttk.Combobox(self.settings_tab, textvariable=self.startup_tab_var, state="readonly")
        self.startup_tab_combobox["values"] = ["✂ Cắt Video", "⬇ Social DL", "⇄ Converter", "💬 AutoSub", "✨Genmini Sub", "🔍 Tìm nhạc", "✎ Renamer"]
        self.startup_tab_combobox.grid(row=0, column=1, padx=10, pady=10)

        # Add Gemini API Key setting
        self.gemini_api_key_label = ttk.Label(self.settings_tab, text="Gemini API Key:")
        self.gemini_api_key_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.gemini_api_key_entry = ttk.Entry(self.settings_tab)
        self.gemini_api_key_entry.grid(row=1, column=1, padx=10, pady=10)

        # Add button next to entry
        self.save_button = ttk.Button(self.settings_tab, text="Lấy APIKey", command=lambda: webbrowser.open("https://aistudio.google.com/app/apikey"))
        self.save_button.grid(row=1, column=2, padx=10, pady=10)
        self.gemini_api_key_entry.insert(0, self.get_gemini_api_key())



        # Arrange the buttons in a horizontal row
        self.save_settings_button = ttk.Button(self.settings_tab, text="💾 Lưu cài đặt", command=self.save_all_settings)
        self.check_update_button = ttk.Button(self.settings_tab, text="⟳ Kiểm tra cập nhật", command=self.check_for_update)
        self.donate_button = ttk.Button(self.settings_tab, text="☕ Buy Me a Coffee", command=self.open_donate_page)

        self.save_settings_button.grid(row=2, column=0, padx=10, pady=10)
        self.check_update_button.grid(row=2, column=1, padx=10, pady=10)
        self.donate_button.grid(row=2, column=2, padx=30, pady=10)

    def open_donate_page(self):
        webbrowser.open("https://img.vietqr.io/image/TPB-0964710413-print.png?addInfo=Donate%20AIO%20Tool%20Media&accountName=VU%20DUY%20THAO")

    def check_for_update(self):
        try:
            # Run the update.exe application
            subprocess.Popen(["update.exe"])
            
            # Close the current application
            self.destroy()
        except FileNotFoundError:
            self.update_status_bar("Error: update.exe not found.")
        except Exception as e:
            self.update_status_bar(f"Error: {str(e)}")

    def load_settings(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                if config["version"] != self.version:
                    # Update the config.json file with the current version
                    config["version"] = self.version
                    with open("config.json", "w") as f:
                        json.dump(config, f)
                        self.status_bar.config(text=f"Ứng dụng đã được cập nhật phiên bản {self.version}")
                self.startup_tab_var.set(config["startup_tab"])
                self.set_gemini_api_key(config["gemini_api_key"])
                self.feature_selection_tab.select(self.get_tab_by_index(self.startup_tab_combobox.current()))
        except FileNotFoundError:
            # Nếu config.json không có, sử dụng giá trị mặc định
            self.startup_tab_var.set("✂ Cắt Video")
            self.set_gemini_api_key("")
            self.feature_selection_tab.select(self.video_cutter_tab)

    def save_all_settings(self):
        """
        Save all settings, including the Gemini API key, to the config.json file.
        """
        config = {
            "startup_tab": self.startup_tab_var.get(),
            "version": self.version,
            "gemini_api_key": self.gemini_api_key_entry.get().strip()
        }
        with open("config.json", "w") as f:
            json.dump(config, f)
        self.status_bar.config(text="Cài đặt đã được lưu.")
        showinfo("Cài đặt đã được lưu.", "Cài đặt đã được lưu! Vui lòng khởi động lại ứng dụng để áp dụng cài đặt mới.")

    def apply_custom_styles(self):
        self.style = ttk.Style()
        self.style.configure("StatusBar.TLabel", background="#f5f5f5", foreground="black")
        self.style.configure("VersionLabel.TLabel", background="#f5f5f5", foreground="gray")
        self.style.configure("CustomLabelFrame.TLabelframe", background="#f5f5f5")

    def update_status_bar(self, text):
        self.status_bar.config(text=text)
        self.status_bar_update_time = time.time()

    def get_gemini_api_key(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                return config["gemini_api_key"]
        except (FileNotFoundError, KeyError):
            return ""

    def set_gemini_api_key(self, api_key):
        self.gemini_api_key = api_key
        self.gemini_api_key_entry.delete(0, tk.END)
        self.gemini_api_key_entry.insert(0, api_key)

    def get_tab_by_index(self, index):
        """
        Get the tab widget by its index in the feature_selection_tab.
        """
        return self.feature_selection_tab.tabs()[index]

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = AIOMediaTool()
    
    # Manually pass the Gemini API key
    my_api_key = app.get_gemini_api_key()
    genai.configure(api_key=my_api_key)
    
    app.mainloop()
