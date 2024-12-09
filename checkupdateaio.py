import json
import requests
import os
import zipfile
import tkinter as tk
from tkinter import ttk
from threading import Thread
import subprocess

def get_latest_version():
    url = "https://vuthao.id.vn/app_check/AIOMediaTool/version.txt"
    response = requests.get(url)
    response.raise_for_status()
    return response.text.strip()

def get_current_version():
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        return config["version"]

def update_application():
    latest_version = get_latest_version()
    download_url = "https://vuthao.id.vn/app_check/AIOMediaTool/AIOToolMedia.zip"
    zip_file_path = "AIOToolMedia.zip"

    # Download the latest version
    response = requests.get(download_url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024

    # Create the progress bar
    progress_bar = ttk.Progressbar(root, mode='determinate', maximum=total_size, length=300)
    progress_bar.pack(pady=20)

    # Download the file in chunks and update the progress bar
    downloaded = 0
    with open(zip_file_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=block_size):
            if chunk:
                file.write(chunk)
                downloaded += len(chunk)
                progress_bar['value'] = downloaded
                root.update_idletasks()

    # Extract the downloaded zip file
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(".")

    # Delete the downloaded zip file
    os.remove(zip_file_path)

    print(f"Đã cập nhật phiên bản: {latest_version}")

    # Add the button to open the AIOMediaTool.exe application
    open_button = tk.Button(root, text="Khởi động lại", command=open_aio_tool)
    open_button.pack(pady=10)

def open_aio_tool():
    subprocess.Popen(["AIO Tool Media.exe"])
    root.destroy()  # Close the update application window

def check_for_updates():
    latest_version = get_latest_version()
    current_version = get_current_version()

    if latest_version > current_version:
        update_label.config(text=f"Có phiên bản mới khả dụng: {latest_version}")
        update_button.pack(pady=10)
    else:
        update_label.config(text=f"Bạn đang sử dụng phiên bản mới nhất: {current_version}")

def start_update():
    update_button.pack_forget()
    update_thread = Thread(target=update_application)
    update_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("AIO Tool Media Update")

    # Center the application window on the screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 400
    window_height = 200
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    update_label = tk.Label(root, text="Đang kiểm tra cập nhật...")
    update_label.pack(pady=20)

    update_button = tk.Button(root, text="Cập nhật ngay", command=start_update)

    check_for_updates()

    root.mainloop()
