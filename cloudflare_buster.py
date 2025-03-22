from playwright.async_api import async_playwright
import asyncio
import os

async def download_image_with_browser(url, output_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(url, timeout=60000)
            # Wait until image is rendered or response is ready
            await page.wait_for_load_state('networkidle')

            # Save image content (simulate right-click > save image as)
            content = await page.evaluate("""() => {
                return fetch(window.location.href)
                    .then(res => res.blob())
                    .then(blob => blob.arrayBuffer())
                    .then(buf => Array.from(new Uint8Array(buf)));
            }""")
            if content:
                with open(output_path, 'wb') as f:
                    f.write(bytes(content))
                return True
            else:
                return False
        except Exception as e:
            print(f"Playwright failed: {e}")
            return False
        finally:
            await browser.close()
