from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import urllib.request
import urllib.parse
import json
import ssl
import time
from deep_translator import GoogleTranslator

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
    platform: str = Query("tiktok", description="Platform (tiktok or douyin)"),
    views_filter: str = Query("all", description="Views filter (e.g. 100k-300k, 300k-500k, 500k-1m, 1m+)"),
    period_filter: str = Query("all", description="Period filter (1d, 1w, 1m, 3m)")
):
    encoded_kw = urllib.parse.quote(q)
    domain_param = "&domain=2" if platform == "douyin" else ""
    # Increase count to 50 to gather more candidates for strict filtering
    url = f"https://www.tikwm.com/api/feed/search?keywords={encoded_kw}&count=100&cursor=0{domain_param}"
    
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
                    title = item.get('title', '')
                    # 엄격한 키워드 필터링: 원본 검색어(q)가 제목(설명)에 최소한 부분문자열로 들어있어야 함
                    if q.lower() not in title.lower():
                        continue

                    play_count = item.get('play_count', 0)
                    
                    # 조회수 필터링 로직
                    if views_filter == '100k+':
                        if play_count < 100000:
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

                    # 업로드 후 며칠 지났는지 계산 (올림 처리)
                    age_seconds = current_time - create_time
                    age_days = max(1, (age_seconds + 86399) // 86400) # 1일 미만도 1일로 표시

                    # 프론트엔드 데이터 규격에 맞게 매핑
                    results.append({
                        "id": item.get('video_id'),
                        "title": item.get('title'),
                        "views": format_count(play_count),
                        "author": f"@{item.get('author', {}).get('unique_id', 'unknown')}",
                        "video_url": item.get('play'), # 순수 MP4 링크
                        "age_days": age_days
                    })
    except Exception as e:
        print(f"Error fetching from TikWM: {e}")
        
    return results

@app.get("/api/translate")
def translate_keyword(
    q: str = Query(..., description="Text to translate"),
    target: str = Query(..., description="Target language code (e.g., 'zh-CN', 'en')")
):
    try:
        translated = GoogleTranslator(source='auto', target=target).translate(q)
        return {"original": q, "translated": translated}
    except Exception as e:
        print(f"Translation Error: {e}")
        return {"original": q, "translated": q}  # Fallback to original

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
