import yt_dlp
import json

def get_tiktok_video_info(url):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'dump_single_json': True,
        'extract_flat': False
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            print(f"Title: {info.get('title')}")
            print(f"View count: {info.get('view_count')}")
            print(f"Uploader: {info.get('uploader')}")
            print(f"URL: {info.get('url')[:100]}...") # truncate for display
            return info
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_url = "https://www.tiktok.com/@gooltem_reviewer/video/7280731003661126914" 
    # Just a guess based on author @꿀템리뷰어, maybe id works even without correct author?
    # Let's use a known generic tiktok format: https://www.tiktok.com/@tiktok/video/7280731003661126914
    # Wait, tiktok video URLs might work with ANY handle if the video ID is correct, e.g. https://www.tiktok.com/@a/video/7280731003661126914
    test_url = "https://www.tiktok.com/@a/video/7297395015110823170" # From our mock
    get_tiktok_video_info(test_url)
