"""1080p 演示视频录制脚本（Playwright + 本地 dev server）

产出: docs/videos/segment1_1080p.webm 等 3 段，1920x1080
后续: ffmpeg 转 MP4 H.264 + 硬字幕 + BGM
"""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5173"
OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "videos"
VIEWPORT = {"width": 1920, "height": 1080}


def scroll(page, dy=600, pause_ms=1200):
    page.evaluate(f"window.scrollBy(0, {dy})")
    page.wait_for_timeout(pause_ms)


def wait_text(page, text, timeout_s=60):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if page.locator(f"text={text}").count() > 0:
            return True
        page.wait_for_timeout(1000)
    return False


def seg1_market_insight(page):
    page.goto(f"{BASE}/market-insight", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)
    wait_text(page, "AI", timeout_s=30)
    page.wait_for_timeout(1000)
    scroll(page, 700)
    scroll(page, 700, 1800)
    try:
        page.locator("select").first.select_option("玩具")
        page.wait_for_timeout(2000)
        scroll(page, 400, 2000)
    except Exception as e:
        print(f"  [warn] category switch: {e}")


def seg2_customer_service(page):
    page.goto(f"{BASE}/customer-service", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)
    try:
        inp = page.locator("input[placeholder*='输入']")
        if inp.count() > 0:
            inp.fill("我想把圣诞饰品出口到俄罗斯，需要什么认证和关税？")
            page.wait_for_timeout(500)
            inp.press("Enter")
            page.wait_for_timeout(3000)
            scroll(page, 400, 3000)
    except Exception as e:
        print(f"  [warn] customer service: {e}")


def seg3_pipeline(page):
    page.goto(f"{BASE}/pipeline", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)
    try:
        btn = page.locator("button:has-text('运行')")
        if btn.count() > 0:
            btn.click()
            page.wait_for_timeout(5000)
        scroll(page, 700)
        scroll(page, 700, 2000)
    except Exception as e:
        print(f"  [warn] pipeline: {e}")


SEGMENTS = [
    ("segment1_market_insight_1080p", seg1_market_insight),
    ("segment2_customer_service_1080p", seg2_customer_service),
    ("segment3_pipeline_1080p", seg3_pipeline),
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Users\52637\AppData\Local\ms-playwright\chromium-1243\chrome-win64\chrome.exe",
        )
        for name, actions in SEGMENTS:
            print(f"[rec] {name} ...")
            t0 = time.time()
            context = browser.new_context(
                viewport=VIEWPORT,
                record_video_dir=str(OUT_DIR),
                record_video_size=VIEWPORT,
            )
            page = context.new_page()
            try:
                actions(page)
            except Exception as e:
                print(f"[warn] {name}: {e}")
            video = page.video
            context.close()
            if video:
                src = video.path()
                dst = OUT_DIR / f"{name}.webm"
                Path(src).replace(dst)
                kb = dst.stat().st_size // 1024
                print(f"[done] {name}: {kb} KB, {time.time() - t0:.0f}s")
        browser.close()
    print(f"Done -> {OUT_DIR}")


if __name__ == "__main__":
    main()
