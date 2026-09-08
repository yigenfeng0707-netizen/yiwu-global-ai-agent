"""三段式演示视频录制（Playwright + 线上 demo，iframe 模式）

用法: python scripts/record_demo_videos.py
产出: docs/videos/segment1_market_insight.webm 等 3 段
说明: ms.show 对浏览器请求会重定向到魔搭落地页（应用以 iframe 嵌入），
      因此所有交互需定位到 ms.show 应用 frame 内执行。
"""

import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://gsym236998-yiwu-global-ai-agent.ms.show"
OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "videos"
VIEWPORT = {"width": 1440, "height": 900}


def open_app(page, path: str, ready_selector: str, timeout_s: int = 90):
    """打开应用路径并定位到 ms.show 应用 frame（等待 SPA 挂载完成）"""
    page.goto(f"{BASE}{path}", wait_until="domcontentloaded", timeout=60000)
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        for f in page.frames:
            if "ms.show" in f.url and "modelscope.cn" not in f.url and "alicdn" not in f.url:
                if f.locator(ready_selector).count() > 0:
                    return f
        page.wait_for_timeout(1000)
    raise RuntimeError(f"应用 frame 未就绪: {path} ({ready_selector})")


def scroll(frame, dy: int = 600, pause_ms: int = 1200):
    frame.evaluate(f"window.scrollBy(0, {dy})")
    frame.wait_for_timeout(pause_ms)


def wait_text(frame, text: str, timeout_s: int = 60, absent: str = None):
    """等待 frame 内出现指定文案（可选：同时断言另一文案不出现）"""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        ok = frame.locator(f"text={text}").count() > 0
        bad = absent and frame.locator(f"text={absent}").count() > 0
        if ok and not bad:
            return True
        frame.wait_for_timeout(1000)
    return False


def seg1_market_insight(page):
    f = open_app(page, "/market-insight", "select")
    # 初始品类已自动查询；顶栏徽章 + AI 商业洞察卡片
    wait_text(f, "AI 商业洞察", timeout_s=60)
    frame_top = page
    frame_top.wait_for_timeout(800)
    scroll(f, 700)
    scroll(f, 700, 1800)
    # 切换品类再触发一次真实查询（展示交互）
    try:
        f.locator("select").first.select_option("玩具")
        f.wait_for_timeout(1500)
        wait_text(f, "AI 商业洞察", timeout_s=60)
        scroll(f, 400, 1500)
    except Exception as e:
        print(f"  [warn] 品类切换失败: {e}")


def seg2_customer_service(page):
    f = open_app(page, "/customer-service", "input[placeholder='输入您的问题...']")
    f.fill("input[placeholder='输入您的问题...']", "我想把圣诞饰品出口到俄罗斯，需要什么认证和关税？")
    f.press("input[placeholder='输入您的问题...']", "Enter")
    # 等待真实 AI 回复（推理模型 15-40s；兜底话术特征词缺席才算成功）
    ok = wait_text(f, "关税", timeout_s=60, absent="暂时无法")
    if not ok:
        print("  [warn] 客服回复未在 60s 内出现关键词")
    f.wait_for_timeout(1000)
    scroll(f, 400, 2500)


def seg3_pipeline(page):
    f = open_app(page, "/pipeline", "button:has-text('运行全链路')")
    f.click("button:has-text('运行全链路')")
    # 等待流水线完成（7步全链路 + LLM，60-150s）
    done = wait_text(f, "已完成", timeout_s=150) or wait_text(f, "重新", timeout_s=10)
    if not done:
        print("  [warn] 流水线 150s 内未完成（视频保留进度）")
    f.wait_for_timeout(1000)
    scroll(f, 700)
    scroll(f, 700, 1800)


SEGMENTS = [
    ("segment1_market_insight", seg1_market_insight),
    ("segment2_customer_service", seg2_customer_service),
    ("segment3_pipeline", seg3_pipeline),
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
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
                print(f"[warn] {name} 交互异常（视频仍保留已录部分）: {e}")
            video = page.video
            context.close()
            if video:
                path = video.path()
                target = OUT_DIR / f"{name}.webm"
                Path(path).replace(target)
                size_kb = target.stat().st_size // 1024
                print(f"[done] {name}: {size_kb} KB, {time.time()-t0:.0f}s")
        browser.close()
    print(f"全部完成 -> {OUT_DIR}")


if __name__ == "__main__":
    main()
