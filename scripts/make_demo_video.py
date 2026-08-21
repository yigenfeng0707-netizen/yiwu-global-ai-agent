"""
Render demo_api_transcript.md into a real MP4 "demo video" using PIL + ffmpeg.

Each transcript section is kept intact (the real fetched data: product titles,
prices, ratings, citations) and paginated across slides so the video actually
shows concrete content rather than just headings.

Run:  python scripts/make_demo_video.py
"""
import os
import re
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSCRIPT = os.path.join(ROOT, 'demo_api_transcript.md')
SLIDES_DIR = os.path.join(ROOT, 'demo_slides')
FFMPEG = r'C:\Program Files\EVCapture\ffmpeg.exe'
OUT = os.path.join(ROOT, 'demo_video.mp4')

W, H = 1280, 720
BG = (17, 19, 28)
FG = (224, 228, 240)
ACCENT = (86, 156, 255)
FONT_PATH = r'C:\Windows\Fonts\msyh.ttc'
SEC_PER_SLIDE = 6
LINES_PER_SLIDE = 22


def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


def wrap(text, font, max_w):
    out = []
    for raw in text.split('\n'):
        if raw == '':
            out.append('')
            continue
        cur = ''
        for ch in raw:
            if font.getlength(cur + ch) > max_w:
                out.append(cur)
                cur = ch
            else:
                cur = cur + ch
        out.append(cur)
    return out


def make_slide(lines, title=None):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    y = 40
    pad = 60
    if title:
        d.text((pad, y), title, font=load_font(30), fill=ACCENT)
        y += 50
    f = load_font(22)
    for ln in lines:
        if y > H - 50:
            break
        color = ACCENT if (ln.startswith('## ') or ln.startswith('### ')) else FG
        d.text((pad, y), ln, font=f, fill=color)
        y += 30
    return img


def parse_blocks():
    md = open(TRANSCRIPT, encoding='utf-8').read()
    parts = re.split(r'(?m)^(#{1,2} \d+\) .+)$', md)
    blocks = []
    i = 1
    while i < len(parts):
        h = parts[i].strip()
        b = parts[i + 1] if i + 1 < len(parts) else ''
        i += 2
        paras = [p.strip() for p in b.split('\n\n') if p.strip()]
        cut = next((idx for idx, p in enumerate(paras) if p.startswith('## 来源')), len(paras))
        blocks.append((h, paras[:cut]))
    return blocks


def main():
    os.makedirs(SLIDES_DIR, exist_ok=True)
    blocks = parse_blocks()

    intro = ('义乌小商品出海智能体-OPC', [
        '金漪湖·论剑 2026 智能体 OPC 创新创业大赛 · OPC 智能体赛道',
        '官方工具：remio 睿妙（知识库 + aApp）',
        'aApp：义乌小商品出海助手  (yiwu-opc-assistant v3)',
        '演示方式：remio API 真实调用实录（rag + 无头浏览器竞品实采）',
    ])
    outro = ('作品信息与落地承诺', [
        'aApp 市场包：remio_aapp_market_prod/yiwu-opc-assistant/yiwu-opc-assistant-v3.zip',
        '源码/GitHub：github.com/yigenfeng0707-netizen/yiwu-global-ai-agent',
        '核心能力：智能体工具调用与自主性（真实网页自主抓取）',
        '落地承诺：获奖后注册落地金义新区、入驻 OPC 社区、39 城复制',
    ])
    sections = [intro] + blocks + [outro]

    paths = []
    idx = 0
    for heading, paras in sections:
        lines = []
        for p in paras:
            lines += wrap(p, load_font(22), W - 120)
        pages = [lines[i:i + LINES_PER_SLIDE] for i in range(0, max(len(lines), 1), LINES_PER_SLIDE)]
        for pi, page in enumerate(pages):
            title = heading if pi == 0 else f'{heading} ({pi + 1}/{len(pages)})'
            img = make_slide(page, title=title)
            p = os.path.join(SLIDES_DIR, f'slide_{idx:03d}.png')
            img.save(p)
            paths.append(p)
            idx += 1
    print('slides:', len(paths))

    pattern = os.path.join(SLIDES_DIR, 'slide_%03d.png').replace('\\', '/')
    cmd = [
        FFMPEG, '-y', '-framerate', f'1/{SEC_PER_SLIDE}',
        '-i', pattern, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', OUT
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300)
    print('ffmpeg rc', r.returncode, (r.stderr or '')[-200:])
    if os.path.exists(OUT):
        print('WROTE', OUT, os.path.getsize(OUT), 'bytes')
    for p in paths:
        try:
            os.remove(p)
        except Exception:
            pass
    try:
        os.rmdir(SLIDES_DIR)
    except Exception:
        pass


if __name__ == '__main__':
    main()
