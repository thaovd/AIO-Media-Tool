import subprocess
import os
import datetime
import sys

def get_video_duration(video_file):
    try:
        script_dir = "ffprobe.exe"
        ffmpeg_path = script_dir
        output = subprocess.check_output([ffmpeg_path, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_file])
        duration_seconds = float(output.decode().strip())
        return datetime.timedelta(seconds=duration_seconds)
    except subprocess.CalledProcessError as e:
        print(f"Error getting video duration: Command '{e.cmd}' exit status {e.returncode}.")
        return None
    except (ValueError, OSError, IOError) as e:
        print(f"Error getting video duration: {e}")
        return None

if __name__ == "__main__":
    video_file = input("Enter video file path: ")
    if not os.path.exists(video_file):
        print(f"Error: File '{video_file}' does not exist.")
        exit(1)
    
    duration = get_video_duration(video_file)
    if duration:
        print(f"{duration}")
    else:
        print("Error getting video duration.")
