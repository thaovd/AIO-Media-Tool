import yt_dlp
from datetime import timedelta


def get_video_info(url):
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        # Chuyển đổi độ dài sang định dạng hh:mm:ss
        length_seconds = info.get('duration', 0)
        length_str = str(timedelta(seconds=length_seconds))
        
        # Nhận độ phân giải có sẵn
        resolutions = set()
        for format_info in info.get('formats', []):
            width = format_info.get('width')
            height = format_info.get('height')
            if width is not None and height is not None and width > 0 and height > 0:
                resolutions.add(f"{width}x{height}")
        
        # Sắp xếp độ phân giải từ nhỏ đến lớn
        sorted_resolutions = sorted(resolutions, key=lambda x: [int(y) for y in x.split('x')])
        resolutions_str = ", ".join(sorted_resolutions)
        
        # Lấy URL hình thumb có kích thước nhỏ nhất
        thumbnails = info.get('thumbnails', [])
        if thumbnails:
            smallest_thumbnail = min(thumbnails, key=lambda t: t.get('width', float('inf')) * t.get('height', float('inf')))
            thumbnail_url = smallest_thumbnail.get('url', '')
        else:
            thumbnail_url = ''
        
        video_info = {
            'thumbnail': thumbnail_url,
            'title': info.get('title', ''),
            'length': length_str,
            'resolutions': resolutions_str
        }
        
        return video_info

if __name__ == "__main__":
    user_url = input("Enter the video URL: ")
    video_info = get_video_info(user_url)

    # Hiển thị tổng hợp thông tin
    print("Video Information:")
    print(f"Thumbnail: {video_info['thumbnail']}")
    print(f"Title: {video_info['title']}")
    print(f"Length: {video_info['length']}")
    print(f"Resolutions: {video_info['resolutions']}")

