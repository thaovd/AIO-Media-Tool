import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import argparse
import audioop
from googleapiclient.discovery import build
import json
import math
import multiprocessing
import requests
import subprocess
import tempfile
import wave
from progressbar import ProgressBar, Percentage, Bar, ETA

from constants import LANGUAGE_CODES, GOOGLE_SPEECH_API_KEY, GOOGLE_SPEECH_API_URL
from formatters import FORMATTERS

class AutoSubGUI:
    def __init__(self, master, status_bar_update_func):
        self.master = master
        self.status_bar_update_func = status_bar_update_func
        self.subtitle_generation_in_progress = False  # Flag to track subtitle generation status

        # File selection
        self.file_label = tk.Label(master, text="Chọn Media File:")
        self.file_label.grid(row=0, column=0, padx=10, pady=10)

        self.file_path = tk.StringVar()
        self.file_entry = tk.Entry(master, textvariable=self.file_path, width=60)
        self.file_entry.grid(row=0, column=1, padx=10, pady=10)

        self.file_button = tk.Button(master, text="Chọn file", command=self.select_file)
        self.file_button.grid(row=0, column=2, padx=10, pady=10)

        # Source language selection
        self.src_label = tk.Label(master, text="Ngôn ngữ Source:")
        self.src_label.grid(row=1, column=0, padx=10, pady=10)

        self.src_language = tk.StringVar()
        self.src_language.set("Vietnamese")
        self.src_dropdown = ttk.Combobox(master, textvariable=self.src_language, values=sorted(LANGUAGE_CODES.values()))
        self.src_dropdown.grid(row=1, column=1, padx=10, pady=10)

        # Destination language selection
        self.dst_label = tk.Label(master, text="Ngôn ngữ Subtitle:")
        self.dst_label.grid(row=2, column=0, padx=10, pady=10)

        self.dst_language = tk.StringVar()
        self.dst_language.set("Vietnamese")
        self.dst_dropdown = ttk.Combobox(master, textvariable=self.dst_language, values=sorted(LANGUAGE_CODES.values()))
        self.dst_dropdown.grid(row=2, column=1, padx=10, pady=10)

        # Submit button
        self.submit_button = tk.Button(master, text="Tạo Subtitles", command=self.submit)
        self.submit_button.grid(row=3, column=1, padx=10, pady=10)

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Media Files", "*.mp4 *.avi *.mov *.wav *.mp3")])
        self.file_path.set(file_path)

    def submit(self):
        if self.subtitle_generation_in_progress:
            self.status_bar_update_func("Subtitle generation is already in progress, please wait...")
            return

        source_path = self.file_path.get()
        source_lang = next(k for k, v in LANGUAGE_CODES.items() if v == self.src_language.get())
        dst_lang = next(k for k, v in LANGUAGE_CODES.items() if v == self.dst_language.get())
        self.status_bar_update_func("Generating subtitles, please wait...")
        self.subtitle_generation_in_progress = True
        main(source_path, source_lang, dst_lang, self.status_bar_update_func, self.show_completion_notification)

    def show_completion_notification(self):
        self.subtitle_generation_in_progress = False  # Reset the flag to indicate subtitle generation is complete
        messagebox.showinfo("Đã tạo subtitle", "Đã tạo Subtitle thành công, file subtitle được nằm trong cùng thư mục file ban đầu.")
        self.status_bar_update_func("Hoàn thành")

def percentile(arr, percent):
    arr = sorted(arr)
    k = (len(arr) - 1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c: return arr[int(k)]
    d0 = arr[int(f)] * (c - k)
    d1 = arr[int(c)] * (k - f)
    return d0 + d1

def is_same_language(lang1, lang2):
    return lang1.split("-")[0] == lang2.split("-")[0]

class FLACConverter(object):
    def __init__(self, source_path, include_before=0.25, include_after=0.25):
        self.source_path = source_path
        self.include_before = include_before
        self.include_after = include_after

    def __call__(self, region):
        try:
            start, end = region
            start = max(0, start - self.include_before)
            end += self.include_after
            temp = tempfile.NamedTemporaryFile(suffix='.flac', delete=False)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            ffmpeg_path = os.path.join(script_dir, "ffmpeg.exe")
            command = [ffmpeg_path, "-ss", str(start), "-t", str(end - start),
                       "-y", "-i", self.source_path,
                       "-loglevel", "error", temp.name]
            subprocess.check_output(command, stdin=open(os.devnull))
            return temp.read()

        except KeyboardInterrupt:
            temp.close()
            os.remove(temp.name)
            return

        finally:
            if os.path.exists(temp.name):
                temp.close()
                os.remove(temp.name)

class SpeechRecognizer(object):
    def __init__(self, language="en", rate=44100, retries=3, api_key=GOOGLE_SPEECH_API_KEY):
        self.language = language
        self.rate = rate
        self.api_key = api_key
        self.retries = retries

    def __call__(self, data):
        try:
            for i in range(self.retries):
                url = GOOGLE_SPEECH_API_URL.format(lang=self.language, key=self.api_key)
                headers = {"Content-Type": "audio/x-flac; rate=%d" % self.rate}

                try:
                    resp = requests.post(url, data=data, headers=headers)
                    if resp.status_code == 200:
                        for line in resp.content.decode("utf-8").split("\n"):
                            try:
                                line = json.loads(line)
                                line = line['result'][0]['alternative'][0]['transcript']
                                return line[:1].upper() + line[1:]
                            except:
                                # no result
                                continue
                    else:
                        continue
                except requests.exceptions.ConnectionError:
                    continue

        except KeyboardInterrupt:
            return

class Translator(object):
    def __init__(self, language, api_key, src, dst):
        self.language = language
        self.api_key = api_key
        self.service = build('translate', 'v2',
                             developerKey=self.api_key)
        self.src = src
        self.dst = dst

    def __call__(self, sentence):
        try:
            if not sentence: return
            result = self.service.translations().list(
                source=self.src,
                target=self.dst,
                q=[sentence]
            ).execute()
            if 'translations' in result and len(result['translations']) and \
                            'translatedText' in result['translations'][0]:
                return result['translations'][0]['translatedText']
            return ""

        except KeyboardInterrupt:
            return

def extract_audio(filename, channels=1, rate=16000):
    temp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    if not os.path.isfile(filename):
        raise Exception("Invalid filepath: {0}".format(filename))

    # Get the full path to the ffmpeg executable
    if getattr(sys, 'frozen', False):
        # If the application is running as a PyInstaller bundle
        script_dir = os.path.dirname(sys.executable)
    else:
        # If the application is running from the source code
        script_dir = os.path.dirname(os.path.abspath(__file__))

    ffmpeg_path = os.path.join(script_dir, "ffmpeg", "ffmpeg.exe")

    if not os.path.exists(ffmpeg_path):
        # If the ffmpeg executable is not found in the expected location, try to find it in the system PATH
        try:
            ffmpeg_path = subprocess.check_output(["where", "ffmpeg"], universal_newlines=True).strip()
        except subprocess.CalledProcessError:
            print("Error: ffmpeg executable not found. Please ensure ffmpeg is installed and available in the system PATH.")
            raise Exception("ffmpeg executable not found")

    command = [ffmpeg_path, "-y", "-i", filename, "-ac", str(channels), "-ar", str(rate), "-loglevel", "error", temp.name]
    try:
        subprocess.check_output(command, stdin=open(os.devnull))
    except subprocess.CalledProcessError as e:
        print(f"Error running ffmpeg: {e}")
        raise e
    return temp.name, rate

def find_speech_regions(filename, frame_width=4096, min_region_size=0.5, max_region_size=6):
    reader = wave.open(filename)
    sample_width = reader.getsampwidth()
    rate = reader.getframerate()
    n_channels = reader.getnchannels()

    total_duration = reader.getnframes() / rate
    chunk_duration = float(frame_width) / rate

    n_chunks = int(total_duration / chunk_duration)
    energies = []

    for i in range(n_chunks):
        chunk = reader.readframes(frame_width)
        energies.append(audioop.rms(chunk, sample_width * n_channels))

    threshold = percentile(energies, 0.2)

    elapsed_time = 0

    regions = []
    region_start = None

    for energy in energies:
        is_silence = energy <= threshold
        max_exceeded = region_start and elapsed_time - region_start >= max_region_size

        if (max_exceeded or is_silence) and region_start:
            if elapsed_time - region_start >= min_region_size:
                regions.append((region_start, elapsed_time))
                region_start = None

        elif (not region_start) and (not is_silence):
            region_start = elapsed_time
        elapsed_time += chunk_duration
    return regions

def main(source_path, source_lang, dst_lang, status_bar_update_func, completion_notification_func):
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--concurrency', help="Number of concurrent API requests to make", type=int, default=10)
    parser.add_argument('-F', '--format', help="Destination subtitle format", default="srt")
    parser.add_argument('-K', '--api-key',
                        help="The Google Translate API key to be used. (Required for subtitle translation)")
    parser.add_argument('--list-formats', help="List all available subtitle formats", action='store_true')
    parser.add_argument('--list-languages', help="List all available source/destination languages", action='store_true')

    args = parser.parse_args()

    if args.list_formats:
        print("List of formats:")
        for subtitle_format in FORMATTERS.keys():
            print("{format}".format(format=subtitle_format))
        return 0

    if args.list_languages:
        print("List of all languages:")
        for code, language in sorted(LANGUAGE_CODES.items()):
            print("{code}\t{language}".format(code=code, language=language))
        return 0

    if args.format not in FORMATTERS.keys():
        print("Subtitle format not supported. Run with --list-formats to see all supported formats.")
        status_bar_update_func("Subtitle format not supported.")
        return 1

    if source_lang not in LANGUAGE_CODES.keys():
        print("Source language not supported. Run with --list-languages to see all supported languages.")
        status_bar_update_func("Source language not supported.")
        return 1

    if dst_lang not in LANGUAGE_CODES.keys():
        print(
            "Destination language not supported. Run with --list-languages to see all supported languages.")
        status_bar_update_func("Destination language not supported.")
        return 1

    status_bar_update_func("Processing, please wait...")  # Update the status bar first
    audio_filename, audio_rate = extract_audio(source_path)

    regions = find_speech_regions(audio_filename)

    pool = multiprocessing.Pool(args.concurrency)
    converter = FLACConverter(source_path=audio_filename)
    recognizer = SpeechRecognizer(language=source_lang, rate=audio_rate, api_key=GOOGLE_SPEECH_API_KEY)

    transcripts = []
    if regions:
        try:
            status_bar_update_func("Converting speech regions to FLAC files...")
            widgets = ["Converting speech regions to FLAC files: ", Percentage(), ' ', Bar(), ' ', ETA()]
            pbar = ProgressBar(widgets=widgets, maxval=len(regions) if regions else 1)  # Set maxval to 1 if regions is empty
            pbar.start()

            extracted_regions = []
            for i, extracted_region in enumerate(pool.imap(converter, regions)):
                extracted_regions.append(extracted_region)
                pbar.update(i + 1)
            pbar.finish()

            status_bar_update_func("Performing speech recognition...")
            widgets = ["Performing speech recognition: ", Percentage(), ' ', Bar(), ' ', ETA()]
            pbar = ProgressBar(widgets=widgets, maxval=len(regions) if regions else 1)  # Set maxval to 1 if regions is empty
            pbar.start()

            for i, transcript in enumerate(pool.imap(recognizer, extracted_regions)):
                if transcript:
                    transcripts.append(transcript)
                pbar.update(i + 1)
            pbar.finish()

            if not is_same_language(source_lang, dst_lang):
                if args.api_key:
                    google_translate_api_key = args.api_key
                    translator = Translator(dst_lang, google_translate_api_key, dst=dst_lang,
                                            src=source_lang)
                    prompt = "Translating from {0} to {1}: ".format(LANGUAGE_CODES[source_lang], LANGUAGE_CODES[dst_lang])
                    widgets = [prompt, Percentage(), ' ', Bar(), ' ', ETA()]
                    pbar = ProgressBar(widgets=widgets, maxval=len(regions)).start()
                    translated_transcripts = []
                    for i, transcript in enumerate(pool.imap(translator, transcripts)):
                        translated_transcripts.append(transcript)
                        pbar.update(i)
                    pbar.finish()
                    transcripts = translated_transcripts
                else:
                    status_bar_update_func("Google Translate API key is required for translation.")
                    return 1

        except KeyboardInterrupt:
            pbar.finish()
            pool.terminate()
            pool.join()
            
        finally:
            if os.path.exists(audio_filename):
                os.remove(audio_filename)

        timed_subtitles = [(r, t) for r, t in zip(regions, transcripts) if t]
        formatter = FORMATTERS.get(args.format)
        formatted_subtitles = formatter(timed_subtitles)

        base, ext = os.path.splitext(source_path)
        dest = "{base}.{format}".format(base=base, format=args.format)


        with open(dest, 'wb') as f:
            f.write(formatted_subtitles.encode("utf-8"))

        flac_dest = "{base}.flac".format(base=base)
        if os.path.exists(flac_dest):
            os.remove(flac_dest)

        status_bar_update_func("Subtitle đã được tạo thành công!.")
        completion_notification_func()
        return 0

    if __name__ == "__main__":
        if getattr(sys, 'frozen', False):
            # If the application is running as a PyInstaller bundle
            script_dir = os.path.dirname(sys.executable)
        else:
            # If the application is running from the source code
            script_dir = os.path.dirname(os.path.abspath(__file__))

        # Add the ffmpeg directory to the system PATH
        os.environ['PATH'] += os.pathsep + os.path.join(script_dir, "ffmpeg")

        root = tk.Tk()
        app = AutoSubGUI(root, status_bar_update_func=lambda msg: print(msg))
        root.mainloop()