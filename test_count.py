import urllib.request
import urllib.parse
import json
import ssl
import time

def test_api_loop(keyword):
    encoded_kw = urllib.parse.quote(keyword)
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    matches = []
    cursor = 0
    
    for i in range(3): # Fetch 3 pages max
        url = f"https://www.tikwm.com/api/feed/search?keywords={encoded_kw}&count=100&cursor={cursor}"
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
        )
        
        try:
            with urllib.request.urlopen(req, context=ctx) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data.get('code') == 0:
                    videos = data.get('data', {}).get('videos', [])
                    print(f"Page {i+1} total fetched: {len(videos)}")
                    
                    for v in videos:
                        title = v.get('title', '')
                        if keyword.lower() in title.lower():
                            if v['video_id'] not in [m['video_id'] for m in matches]:
                                matches.append(v)
                    
                    cursor = data.get('data', {}).get('cursor', 0)
                    if cursor == 0 or not data.get('data', {}).get('hasMore'):
                        break
                else:
                    print("Failed:", data)
                    break
        except Exception as e:
            print("Error:", e)
            break
            
        time.sleep(1) # Be nice to API

    print(f"Total Strict Matches for {keyword}: {len(matches)}")
    return matches

if __name__ == "__main__":
    test_api_loop("꿀템")
    test_api_loop("꿀탬")
