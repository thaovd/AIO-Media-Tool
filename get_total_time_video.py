import subprocess
import os
import datetime

def get_video_duration(video_file):
    try:
        output = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_file])
        duration_seconds = float(output.decode().strip())
        return datetime.timedelta(seconds=duration_seconds)
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi lấy thời lượng video: Command '{e.cmd}' exit status {e.returncode}.")
        return None
    except (ValueError, OSError, IOError) as e:
        print(f"Lỗi khi lấy thời lượng video: {e}")
        return None

if __name__ == "__main__":
    video_file = input("Nhập link file video: ")
    if not os.path.exists(video_file):
        print(f"Lỗi: File '{video_file}' không tồn tại.")
        exit(1)
    
    duration = get_video_duration(video_file)
    if duration:
        print(f"{duration}")
    else:
        print("Lỗi khi lấy thời lượng video.")
