# -*- coding: utf-8 -*-
"""把 docs/videos 下 3 段 1080p 演示片段合并为单片，并加标题卡/结尾卡。

产出: docs/videos/OPC产品演示_合并版.mp4 (1920x1080, H.264 + AAC, 含原片段硬字幕与BGM)
依赖: PIL(渲染卡片) + ffmpeg(拼接)。卡片用 PIL 渲染避开 ffmpeg drawtext 的 CJK 字体转义坑。
"""
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
VID = ROOT / "docs" / "videos"
FONT_BD = r"C:\Windows\Fonts\msyhbd.ttc"   # 微软雅黑 Bold
FONT_RG = r"C:\Windows\Fonts\msyh.ttc"     # 微软雅黑 Regular
W, H = 1920, 1080
YIWU_RED = (178, 16, 32)
DARK_RED = (120, 10, 22)
GOLD = (212, 175, 55)
WHITE = (255, 255, 255)

SEGMENTS = [
    "segment1_market_insight_1080p.mp4",
    "segment2_customer_service_1080p.mp4",
    "segment3_pipeline_1080p.mp4",
]
DEMO_URL = "gsym236998-yiwu-global-ai-agent.ms.show"


def _font(path, size):
    return ImageFont.truetype(path, size)


def _center(draw, text, font, y, fill, w=W):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, y), text, font=font, fill=fill)


def render_title():
    img = Image.new("RGB", (W, H), YIWU_RED)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=YIWU_RED)
    d.rectangle([int(W * 0.62), 0, W, H], fill=DARK_RED)          # 右侧深色块
    d.rectangle([160, 600, 560, 612], fill=GOLD)                   # 装饰线
    _center(d, "义乌小商品出海智能体", _font(FONT_BD, 96), 300, WHITE)
    _center(d, "OPC · 产品演示", _font(FONT_BD, 64), 430, GOLD)
    _center(d, "一个人 + 7 个 AI 数字员工 = 一家完整外贸公司", _font(FONT_RG, 40), 660, (255, 220, 220))
    _center(d, "2026「直通乌镇」全球互联网大赛 · OPC 特色赛", _font(FONT_RG, 32), 880, (255, 190, 190))
    p = VID / "_card_title.png"
    img.save(p)
    return p


def render_ending():
    img = Image.new("RGB", (W, H), DARK_RED)
    d = ImageDraw.Draw(img)
    _center(d, "义乌小商品，照亮全球", _font(FONT_BD, 88), 300, WHITE)
    _center(d, "OPC，让每一盏灯都亮起来", _font(FONT_RG, 44), 430, GOLD)
    d.rectangle([560, 560, 1360, 572], fill=GOLD)
    _center(d, "在线体验（已上线魔搭）", _font(FONT_RG, 36), 620, (255, 210, 210))
    _center(d, DEMO_URL, _font(FONT_BD, 48), 680, WHITE)
    _center(d, "7 大 Agent 均为 LLM 增强型 · 真实数据源可现场自证 · CI 四门禁全绿", _font(FONT_RG, 30), 820, (255, 190, 190))
    p = VID / "_card_ending.png"
    img.save(p)
    return p


def png_to_card(png, out_mp4, seconds):
    """PNG -> 带静音音轨的卡片视频，参数对齐片段(h264/1080p30/aac48k stereo)。"""
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-framerate", "30", "-t", str(seconds), "-i", str(png),
        "-f", "lavfi", "-t", str(seconds), "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", "-s", f"{W}x{H}",
        "-c:a", "aac", "-ar", "48000", "-ac", "2", "-shortest", str(out_mp4),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def main():
    for s in SEGMENTS:
        if not (VID / s).exists():
            sys.exit(f"缺片段: {VID / s}")

    title_png = render_title()
    ending_png = render_ending()
    title_mp4 = VID / "_card_title.mp4"
    ending_mp4 = VID / "_card_ending.mp4"
    png_to_card(title_png, title_mp4, 4)
    png_to_card(ending_png, ending_mp4, 5)

    # 统一转码片段为相同参数，确保 concat 兼容（避免时基/编码差异导致花屏）
    norm_dir = VID / "_norm"
    norm_dir.mkdir(exist_ok=True)
    norm_list = []
    for i, s in enumerate([title_mp4] + [VID / x for x in SEGMENTS] + [ending_mp4]):
        out = norm_dir / f"part{i}.mp4"
        cmd = [
            "ffmpeg", "-y", "-i", str(s),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", "-s", f"{W}x{H}",
            "-c:a", "aac", "-ar", "48000", "-ac", "2",
            "-vf", "setsar=1", str(out),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        norm_list.append(out)

    list_file = norm_dir / "concat.txt"
    list_file.write_text("\n".join(f"file '{p.as_posix()}'" for p in norm_list), encoding="utf-8")

    final = VID / "OPC产品演示_合并版.mp4"
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-ac", "2",
           "-movflags", "+faststart", str(final)]
    subprocess.run(cmd, check=True, capture_output=True)

    # 探测时长
    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(final)],
        capture_output=True, text=True).stdout.strip()
    size_kb = final.stat().st_size // 1024
    print(f"✅ 合并完成: {final}")
    print(f"   时长 {float(dur):.1f}s | {size_kb} KB | 1920x1080 H.264+AAC")
    print(f"   结构: 标题卡4s + 市场洞察 + 智能客服 + 全链路Pipeline + 结尾卡5s")


if __name__ == "__main__":
    main()
