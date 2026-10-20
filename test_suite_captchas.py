import asyncio
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True, encoding="utf-8")

REAL_URLS = [
    ("hCaptcha Easy", "https://lessons.zennolab.com/captchas/hcaptcha/?level=easy"),
    ("hCaptcha Moderate", "https://lessons.zennolab.com/captchas/hcaptcha/?level=moderate"),
    ("hCaptcha Difficult", "https://lessons.zennolab.com/captchas/hcaptcha/?level=difficult"),
    ("reCAPTCHA v2 Low", "https://lessons.zennolab.com/captchas/recaptcha/v2_simple.php?level=low"),
    ("reCAPTCHA v2 Middle", "https://lessons.zennolab.com/captchas/recaptcha/v2_simple.php?level=middle"),
]

async def run_suite():
    p = await async_playwright().start()
    shots_dir = Path("screenshots/suite")
    shots_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        browser = await p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=False,
            args=["--start-maximized", "--no-first-run", "--no-default-browser-check"]
        )
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        from tools.browser_cdp import BrowserController
        bc = BrowserController()
        bc._page = page
        bc._connected = True

        for name, url in REAL_URLS:
            print(f"\n==================================================")
            print(f"Testing Real Captcha: {name} -> {url}")
            print(f"==================================================")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                await asyncio.sleep(2.5)

                slug = name.lower().replace(" ", "_")
                before_path = shots_dir / f"{slug}_before.png"
                await page.screenshot(path=str(before_path))

                # Run solver
                res = await bc.solve_captcha()
                print(f"Result for {name}: {res}")

                await asyncio.sleep(3.5)
                after_path = shots_dir / f"{slug}_after.png"
                await page.screenshot(path=str(after_path))
                print(f"Screenshots saved: {before_path} & {after_path}")
            except Exception as e:
                print(f"Error on {name}: {e}")

        await browser.close()
        print("\n[+] All real captcha tests completed!")
    finally:
        await p.stop()

if __name__ == "__main__":
    asyncio.run(run_suite())
