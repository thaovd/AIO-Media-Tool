import os
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
import google.generativeai as genai
import subprocess

class AutoSubApp(tk.Frame):
    def __init__(self, master, parent):
        super().__init__(master)
        self.master = master
        self.parent = parent  # Store the reference to the parent AIOMediaTool instance
        self.pack(fill="both", expand=True)

        # Create a frame for the model selection dropdown
        self.model_selection_frame = ttk.LabelFrame(self, text="Lựa chọn Model Gemini AI", style="CustomLabelFrame.TLabelframe")
        self.model_selection_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Create a dropdown menu for model selection
        model_options = ["gemini-1.5-pro", "gemini-2.0-flash-exp"]
        self.selected_model = tk.StringVar(self)
        self.selected_model.set("gemini-1.5-pro")  # Set the default model

        self.model_dropdown = ttk.Combobox(self.model_selection_frame, textvariable=self.selected_model, values=model_options)
        self.model_dropdown.pack(pady=10)

        # Create a frame for the audio upload and subtitle generation
        self.media_conversion_frame = ttk.LabelFrame(self, text="Lựa chọn file âm thanh để tạo subtitle", style="CustomLabelFrame.TLabelframe")
        self.media_conversion_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.upload_button = tk.Button(self.media_conversion_frame, text="Upload Audio", command=self.upload_audio)
        self.upload_button.pack(pady=20)

        # Create a preview box for the subtitle
        self.subtitle_preview = scrolledtext.ScrolledText(self.media_conversion_frame, width=80, height=10)
        self.subtitle_preview.pack(pady=20)

        # Create a button to export the subtitle
        self.export_button = tk.Button(self.media_conversion_frame, text="Lưu Subtitle", command=lambda: self.save_subtitle(self.subtitle_preview.get("1.0", tk.END).strip()))
        self.export_button.pack(pady=20)

    def upload_audio(self):
        try:
            audio_file = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav;*.ogg;*.mp4;*.avi;*.mov")])
            if audio_file:
                self.parent.status_bar.config(text="Đang phân tích và tạo subtitle...", style="CustomStatusBar.TLabel")
                self.master.update()
                converted_audio = self.convert_to_mp3(audio_file)
                myfile = genai.upload_file(converted_audio)
                print(f"{myfile=}")
                self.generate_subtitle(myfile, self.selected_model.get(), self.parent.get_gemini_api_key())
        except Exception as e:
            print(f"Lỗi khi tải tệp âm thanh lên: {e}")
            self.parent.status_bar.config(text="Lỗi khi tải tệp âm thanh lên!", style="CustomStatusBar.TLabel")
            self.master.update()
            tk.messagebox.showerror("Lỗi", f"Lỗi khi tải tệp âm thanh lên: {e}")

    def convert_to_mp3(self, input_file):
        try:
            # Create a temporary output file name
            output_file = os.path.splitext(input_file)[0] + ".mp3"

            # Use ffmpeg to convert the input file to MP3 64kbps
            subprocess.run(["ffmpeg", "-y", "-i", input_file, "-b:a", "96k", "-c:a", "libmp3lame", output_file], check=True)

            return output_file
        except subprocess.CalledProcessError as e:
            print(f"Lỗi khi chuyển đổi tệp âm thanh: {e}")
            self.parent.status_bar.config(text="Lỗi khi chuyển đổi tệp âm thanh!", style="CustomStatusBar.TLabel")
            self.master.update()
            tk.messagebox.showerror("Lỗi", f"Lỗi khi chuyển đổi tệp âm thanh: {e}")
            raise e

    def generate_subtitle(self, audio_file, model_name, gemini_api_key):
        try:
            model = genai.GenerativeModel(model_name)
            model.api_key = gemini_api_key  # Use the api_key attribute directly
            prompt = "Create full subtitle for this audio file, SRT format, Vietnamese language, Use only 1 display line, identify exact time, After a period or question mark is the end of a subtitle, sample: 1 <line break> 00:01:17,757 --> 00:01:18,757 <line break> Copy boy! <line break>."
            response = model.generate_content([prompt, audio_file])
            subtitle_text = response.text
            self.update_preview(subtitle_text)
            self.parent.status_bar.config(text="Đã tạo subtitle!", style="CustomStatusBar.TLabel")
            self.master.update()
            tk.messagebox.showinfo(title="Hoàn thành", message="Subtitle đã được tạo, hãy kiểm tra nếu có phát sinh lỗi trước khi export SRT.")
        except Exception as e:
            print(f"Lỗi tạo subtitle: {e}")
            self.parent.status_bar.config(text="Lỗi tạo subtitle!", style="CustomStatusBar.TLabel")
            self.master.update()
            tk.messagebox.showerror("Lỗi", f"Lỗi tạo subtitle: {e}")

    def save_subtitle(self, subtitle_text):
        try:
            subtitle_file = filedialog.asksaveasfilename(defaultextension=".srt", filetypes=[("Subtitle Files", "*.srt")])
            if subtitle_file:
                with open(subtitle_file, "w", encoding="utf-8") as file:
                    file.write(subtitle_text)
                print("Subtitle đã được lưu.")
                self.parent.status_bar.config(text="Subtitle đã được lưu!", style="CustomStatusBar.TLabel")
                self.master.update()
                tk.messagebox.showinfo(title="Đã lưu", message="Subtitle đã được lưu.")
        except Exception as e:
            print(f"Error saving subtitle: {e}")
            self.parent.status_bar.config(text="Lỗi lưu subtitle!", style="CustomStatusBar.TLabel")
            self.master.update()
            tk.messagebox.showerror("Lỗi", f"Lỗi lưu subtitle: {e}")

    def update_preview(self, subtitle_text):
        self.subtitle_preview.delete("1.0", tk.END)
        self.subtitle_preview.insert(tk.END, subtitle_text)
