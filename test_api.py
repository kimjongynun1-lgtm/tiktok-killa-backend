import urllib.request
import json
import ssl

def get_tiktok_video_info(video_id_or_url):
    print(f"Fetching config for {video_id_or_url}")
    # Using TikWM API to get video information
    url = f"https://www.tikwm.com/api/?url={video_id_or_url}"
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('code') == 0:
                item = data.get('data', {})
                print(f"Title: {item.get('title')}")
                print(f"Views: {item.get('play_count')}")
                print(f"Author: {item.get('author', {}).get('unique_id')}")
                print(f"MP4 URL: {item.get('play')[:100]}...")
            else:
                print("Failed:", data)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_url = "https://www.tiktok.com/@a/video/7297395015110823170" 
    get_tiktok_video_info(test_url)
