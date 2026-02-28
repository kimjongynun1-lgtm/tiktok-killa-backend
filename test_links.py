import asyncio
from playwright.async_api import async_playwright

async def get_test_links():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.tiktok.com/@bts_official_bighit")
        try:
            await page.wait_for_selector('a[href*="/video/"]', timeout=3000)
            elements = await page.query_selector_all('a[href*="/video/"]')
            links = []
            for el in elements:
                href = await el.get_attribute('href')
                if href and "/video/" in href:
                    links.append(href)
            print("Found links:", list(set(links))[:6])
        except Exception as e:
            print("Failed:", e)
        await browser.close()

asyncio.run(get_test_links())
