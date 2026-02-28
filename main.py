from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import urllib.request
import urllib.parse
import json
import ssl
import time

app = FastAPI()

# 프론트엔드(Vite)와의 통신을 위해 CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def format_count(count):
    if not count:
        return "0"
    if count >= 1000000:
        return f"{count/1000000:.1f}M"
    elif count >= 1000:
        return f"{count/1000:.0f}K"
    return str(count)

@app.get("/api/search")
def search_tiktok(
    q: str = Query(..., description="Search keyword"),
    views_filter: str = Query("all", description="Views filter (e.g. 100k-300k, 300k-500k, 500k-1m, 1m+)"),
    period_filter: str = Query("all", description="Period filter (1d, 1w, 1m, 3m)")
):
    encoded_kw = urllib.parse.quote(q)
    url = f"https://www.tikwm.com/api/feed/search?keywords={encoded_kw}&count=30&cursor=0"
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    )
    
    results = []
    
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('code') == 0:
                videos = data.get('data', {}).get('videos', [])
                for item in videos:
                    play_count = item.get('play_count', 0)
                    
                    # 조회수 필터링 로직
                    if views_filter == '100k-300k':
                        if not (100000 <= play_count < 300000):
                            continue
                    elif views_filter == '300k-500k':
                        if not (300000 <= play_count < 500000):
                            continue
                    elif views_filter == '500k-1m':
                        if not (500000 <= play_count < 1000000):
                            continue
                    elif views_filter == '1m+':
                        if play_count < 1000000:
                            continue

                    # 기간 필터링 로직 (create_time은 보통 Unix Timestamp 초 단위)
                    create_time = item.get('create_time', 0)
                    current_time = int(time.time())
                    
                    if period_filter == '1d': # 24시간 이내
                        if current_time - create_time > 86400:
                            continue
                    elif period_filter == '1w': # 6일 이내
                        if current_time - create_time > 86400 * 6:
                            continue
                    elif period_filter == '1m': # 한달(30일) 이내
                        if current_time - create_time > 86400 * 30:
                            continue
                    elif period_filter == '3m': # 3개월(90일) 이내
                        if current_time - create_time > 86400 * 90:
                            continue

                    # 프론트엔드 데이터 규격에 맞게 매핑
                    results.append({
                        "id": item.get('video_id'),
                        "title": item.get('title'),
                        "views": format_count(play_count),
                        "author": f"@{item.get('author', {}).get('unique_id', 'unknown')}",
                        "video_url": item.get('play') # 순수 MP4 링크
                    })
    except Exception as e:
        print(f"Error fetching from TikWM: {e}")
        
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
