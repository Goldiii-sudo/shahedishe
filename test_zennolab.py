import asyncio
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright
import cv2
import numpy as np

# Ensure stdout is unbuffered utf-8
sys.stdout.reconfigure(line_buffering=True, encoding="utf-8")

async def test_captcha():
    print("Starting Playwright with Chrome...")
    p = await async_playwright().start()
    try:
        browser = await p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=False,
            args=["--start-maximized", "--no-first-run", "--no-default-browser-check"]
        )
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        print("Navigating to https://lessons.zennolab.com/captchas/hcaptcha/?level=easy ...")
        await page.goto("https://lessons.zennolab.com/captchas/hcaptcha/?level=easy", wait_until="domcontentloaded", timeout=15000)
        print("Page DOM loaded. Waiting 3s for hCaptcha to initialize...")
        await asyncio.sleep(3)

        # 1. Take full screenshot
        shots_dir = Path("screenshots")
        shots_dir.mkdir(exist_ok=True)
        before_shot = shots_dir / "zennolab_before.png"
        await page.screenshot(path=str(before_shot))
        print(f"Saved initial screenshot to {before_shot}")

        # 2. Test Computer Vision locator from tools.captcha
        from tools.captcha import find_captcha_checkbox
        cv_img = cv2.imread(str(before_shot))
        loc = find_captcha_checkbox(cv_img)
        print("Computer Vision find_captcha_checkbox returned:", loc)

        # 3. Test Direct Frame DOM solver (autoreger.js technique)
        clicked = False
        for frame in page.frames:
            url = frame.url or ""
            if "hcaptcha" in url and "checkbox" in url:
                print(f"Found hCaptcha iframe: {url}")
                loc_box = frame.locator("#checkbox, input[type='checkbox'], #anchor").first
                if await loc_box.count() > 0:
                    print("Found #checkbox locator in iframe. Clicking now...")
                    await loc_box.click()
                    clicked = True
                    print("Click issued!")
                    break

        if not clicked:
            print("Trying iframe wait...")
            try:
                frame_el = await page.wait_for_selector("iframe[src*='hcaptcha']", timeout=5000)
                frame = await frame_el.content_frame()
                if frame:
                    loc_box = frame.locator("#checkbox")
                    await loc_box.click(timeout=3000)
                    clicked = True
                    print("Clicked #checkbox after wait!")
            except Exception as e:
                print("Frame wait error:", e)

        print("Waiting 4s to capture state after click...")
        await asyncio.sleep(4)

        after_shot = shots_dir / "zennolab_after.png"
        await page.screenshot(path=str(after_shot))
        print(f"Saved post-click screenshot to {after_shot}")

        # Check status in page text
        body_text = await page.evaluate("() => document.body.innerText")
        print("Page body text snippet:\n", body_text[:400])

        await browser.close()
        print("Browser closed. Test finished.")
    finally:
        await p.stop()

if __name__ == "__main__":
    asyncio.run(test_captcha())
