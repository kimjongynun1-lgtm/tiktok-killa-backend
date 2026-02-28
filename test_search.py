import urllib.request
import urllib.parse
import json
import ssl

def search_tiktok(keyword):
    print(f"Searching for {keyword}")
    encoded_kw = urllib.parse.quote(keyword)
    url = f"https://www.tikwm.com/api/feed/search?keywords={encoded_kw}&count=10&cursor=0"
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    )
    
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('code') == 0:
                videos = data.get('data', {}).get('videos', [])
                print(f"Found {len(videos)} videos")
                for item in videos[:3]:
                    print("-" * 30)
                    print(f"Video ID: {item.get('video_id')}")
                    print(f"Title: {item.get('title')}")
                    print(f"Views: {item.get('play_count')}")
                    print(f"Author: {item.get('author', {}).get('unique_id')}")
                    print(f"MP4 URL: {item.get('play')[:100]}...")
                return videos
            else:
                print("Failed:", data)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    search_tiktok("coupang")
