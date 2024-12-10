from ShazamAPI import Shazam
from datetime import datetime
import json
import os
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
import webbrowser
import sys
import subprocess

class ShazamGUI:
    def __init__(self, master):
        self.master = master
        
        # Get the directory of the script
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Detect if ffmpeg.exe is in the same directory as the script
        self.ffmpeg_path = os.path.join(self.script_dir, 'ffmpeg.exe')
        if os.path.exists(self.ffmpeg_path):
            self.script_dir = os.path.dirname(os.path.abspath(self.ffmpeg_path))
        else:
            try:
                # Try to find ffmpeg in the system PATH
                subprocess.check_output(['ffmpeg', '-version'])
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("ffmpeg not found in the system PATH. Using the script directory instead.")

        # Detect Song button
        self.detect_song_button = ttk.Button(master, text="Phân tích âm thanh đang phát", command=self.detect_song, style="CustomButton.TButton")
        self.detect_song_button.pack(padx=20, pady=40)

        # Status label
        self.status_label = ttk.Label(master, text="", style="CustomLabel.TLabel")
        self.status_label.pack(padx=20, pady=10)

        # Video information frame
        self.video_info_frame = ttk.LabelFrame(master, text="Thông tin bài hát được phân tích")
        self.video_info_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Thumbnail frame
        self.thumbnail_frame = ttk.Frame(self.video_info_frame)
        self.thumbnail_frame.grid(row=0, column=0, rowspan=4, padx=10, pady=10)

        self.thumbnail_label = ttk.Label(self.thumbnail_frame)
        self.thumbnail_label.pack()

        # Load the sample.jpg image as the default thumbnail
        self.sample_image = Image.open(os.path.join(self.script_dir, 'sample.jpg'))
        self.sample_image = self.sample_image.resize((150, 150), resample=Image.BICUBIC)
        self.sample_photo = ImageTk.PhotoImage(self.sample_image)
        self.thumbnail_label.configure(image=self.sample_photo)
        self.thumbnail_label.image = self.sample_photo

        self.title_label = ttk.Label(self.video_info_frame, text="Tiêu đề:", style="CustomBoldLabel.TLabel")
        self.title_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.title_value = ttk.Label(self.video_info_frame, text="", style="CustomLabel.TLabel")
        self.title_value.grid(row=0, column=2, padx=10, pady=5, sticky="w")

        self.artist_label = ttk.Label(self.video_info_frame, text="Ca sĩ, Nhạc sĩ:", style="CustomBoldLabel.TLabel")
        self.artist_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.artist_value = ttk.Label(self.video_info_frame, text="", style="CustomLabel.TLabel")
        self.artist_value.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        self.tagid_label = ttk.Label(self.video_info_frame, text="Tag ID:", style="CustomBoldLabel.TLabel")
        self.tagid_label.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.tagid_value = ttk.Label(self.video_info_frame, text="", style="CustomLabel.TLabel")
        self.tagid_value.grid(row=2, column=2, padx=10, pady=5, sticky="w")

        self.search_href_label = ttk.Label(self.video_info_frame, text="Shazam URL:", style="CustomBoldLabel.TLabel")
        self.search_href_label.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        self.search_href_value = ttk.Label(self.video_info_frame, text="", style="CustomLabel.TLabel", wraplength=250)
        self.search_href_value.grid(row=3, column=2, padx=10, pady=5, sticky="w")
        self.search_href_value.bind("<Button-1>", self.open_search_url)  # Bind the left-click event to the open_search_url method

    def detect_song(self):
        try:
            self.status_label.config(text="Đang phân tích âm thanh...")
            self.master.update()

            # Record audio using rec.exe
            rec_exe_path = os.path.join(self.script_dir, 'rec.exe')
            if os.path.exists(rec_exe_path):
                subprocess.run([rec_exe_path], check=True)
            else:
                print("rec.exe not found in the script directory.")
                self.status_label.config(text="Không tìm thấy rec.exe. Vui lòng kiểm tra.")
                return

            # Process the recorded audio file
            mp3_file_path = os.path.join(self.script_dir, 'rec.mp3')
            if os.path.exists(mp3_file_path):
                mp3_file_content_to_recognize = open(mp3_file_path, 'rb').read()

                shazam = Shazam(mp3_file_content_to_recognize)
                recognize_generator = shazam.recognizeSong()
                response = next(recognize_generator)
                filtered_response = self.filter_shazam_response(response)
                if filtered_response:
                    self.display_song_info(filtered_response)
                    self.pretty_print_shazam_response(filtered_response)
                    self.status_label.config(text="")  # Clear the status label
                else:
                    self.status_label.config(text="Không tìm được kết quả nào.")

                # Automatically delete the rec.mp3 file
                os.remove(mp3_file_path)
                print("rec.mp3 file deleted.")
            else:
                print("rec.mp3 file not found.")
                self.status_label.config(text="Không tìm thấy tệp tin ghi âm. Vui lòng kiểm tra.")
        except StopIteration:
            print("Shazam đã hoàn thành phân tích.")
            self.status_label.config(text="")
        except FileNotFoundError:
            print(f"Không tìm thấy ffmpeg. Vui lòng đảm bảo rằng ffmpeg nằm trong cùng thư mục với tệp tin này hoặc trong thư mục {self.script_dir}, hoặc trong PATH của hệ thống.")
            self.status_label.config(text="Không tìm thấy ffmpeg. Vui lòng kiểm tra.")
        except Exception as e:
            print(f"Lỗi khi phân tích âm thanh: {e}")
            self.status_label.config(text="Đã xảy ra lỗi khi phân tích âm thanh.")

    def filter_shazam_response(self, response):
        offset, data = response
        
        if 'track' in data:
            track = data['track']
            filtered_response = {
                'offset': offset,
                'title': track['title'],
                'subtitle': track['subtitle'],
                'images': track['images']['coverart'],
                'share': track['share'],
                'search_href': track['share']['href'],
                'artists': track['artists'],
                'isrc': track.get('isrc', ''),
                'tagid': data.get('tagid', '')
            }
            return filtered_response
        else:
            return None

    def display_song_info(self, response):
        self.title_value.config(text=response['title'])
        self.artist_value.config(text=response['subtitle'])
        self.tagid_value.config(text=response['tagid'])
        self.search_href_value.config(text=response['search_href'])

        # Display the thumbnail
        try:
            image_url = response['images']
            if image_url:
                image = Image.open(requests.get(image_url, stream=True).raw)
                image = image.resize((150, 150), resample=Image.BICUBIC)
                photo = ImageTk.PhotoImage(image)
                self.thumbnail_label.configure(image=photo)
                self.thumbnail_label.image = photo
        except Exception as e:
            print(f"Thumbnail không khả dụng: {e}")
            # Reset the thumbnail to the sample image
            self.thumbnail_label.configure(image=self.sample_photo)
            self.thumbnail_label.image = self.sample_photo

        self.master.update()

    def pretty_print_shazam_response(self, response):
        if response:
            print("=" * 80)
            print(f"Shazam Response at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Title: {response['title']}")
            print(f"Artist: {response['subtitle']}")
            print(f"ISRC: {response['isrc']}")
            print(f"Search URL: {response['search_href']}")
            print(f"Tag ID: {response['tagid']}")
            print(f" Coverart: {json.dumps(response['images'])}")
            print("=" * 80)

    def open_search_url(self, event):
        """
        Open the search URL in the default web browser when the user clicks on the search URL label.
        """
        search_url = self.search_href_value.cget("text")
        if search_url:
            try:
                webbrowser.open(search_url)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open the search URL: {e}")

def main():
    root = ttk.Tk()
    app = ShazamGUI(root)
    root.mainloop()

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        # If the script is running as a PyInstaller bundle
        os.chdir(sys._MEIPASS)
    main()
