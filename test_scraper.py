import asyncio
from playwright.async_api import async_playwright

async def test_search():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to TikTok search...")
        await page.goto("https://www.tiktok.com/search?q=coupang")
        try:
            await page.wait_for_selector('[data-e2e="search-card-video"]', timeout=5000)
            elements = await page.query_selector_all('[data-e2e="search-card-video"]')
            print(f"Found {len(elements)} videos!")
            for el in elements[:3]:
                link = await el.query_selector('a')
                if link:
                    href = await link.get_attribute('href')
                    print("Video link:", href)
        except Exception as e:
            print("Failed to find elements:", e)
            html = await page.content()
            print("Page title:", await page.title())
        await browser.close()

asyncio.run(test_search())
