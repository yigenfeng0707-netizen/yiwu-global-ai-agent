"""
Render demo_api_transcript.md into a real MP4 "demo video" using PIL + ffmpeg.

Each transcript section/slide is drawn as an image (CJK-capable font), then ffmpeg
concatenates them into demo_video.mp4. This turns the API-driven demo transcript
into a shareable video deliverable without any screen recording.

Run:  python scripts/make_demo_video.py
"""
import os
import subprocess
import re
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
SEC_PER_SLIDE = 7


def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


def wrap(text, font, max_w):
    lines = []
    for raw in text.split('\n'):
        if raw == '':
            lines.append('')
            continue
        cur = ''
        for ch in raw:
            test = cur + ch
            if font.getlength(test) > max_w:
                lines.append(cur)
                cur = ch
            else:
                cur = test
        lines.append(cur)
        if len(lines) > 200:
            break
    return lines


def make_slide(lines, title=None):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    y = 40
    pad = 60
    if title:
        d.text((pad, y), title, font=load_font(30), fill=ACCENT)
        y += 50
    body_font = load_font(22)
    max_w = W - 2 * pad
    for ln in lines:
        if y > H - 50:
            break
        color = FG
        if ln.startswith('## ') or ln.startswith('# '):
            color = ACCENT
        d.text((pad, y), ln, font=body_font, fill=color)
        y += 30
    return img


def split_chunks(paragraphs):
    chunks = []
    cur = []
    n = 0
    for p in paragraphs:
        wrapped = wrap(p, load_font(22), W - 120)
        if n + len(wrapped) > 26:
            chunks.append(cur)
            cur = []
            n = 0
        cur.extend(wrapped)
        n += len(wrapped)
    if cur:
        chunks.append(cur)
    return chunks


def make_card(lines, title=None, accent=True):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    y = 80 if not title else 50
    pad = 80
    if title:
        d.text((pad, y), title, font=load_font(34), fill=ACCENT)
        y += 60
    f = load_font(24)
    for ln in lines:
        d.text((pad, y), ln, font=f, fill=FG)
        y += 38
    return img


def main():
    os.makedirs(SLIDES_DIR, exist_ok=True)
    md = open(TRANSCRIPT, encoding='utf-8').read()
    # split by headings; each heading + its paragraphs = one logical block
    parts = re.split(r'(?m)^(#{1,3} .+)$', md)
    blocks = []
    i = 1
    while i < len(parts):
        heading = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ''
        i += 2
        paras = [p.strip() for p in body.split('\n\n') if p.strip()]
        blocks.append((heading, paras))

    intro = ('义乌小商品出海智能体-OPC', [
        '金漪湖·论剑 2026 智能体 OPC 创新创业大赛 · OPC 智能体赛道',
        '官方工具：remio 睿妙（知识库 + aApp）',
        'aApp：义乌小商品出海助手  (yiwu-opc-assistant v3)',
        '演示方式：remio API 真实调用实录（rag + 无头浏览器竞品实采）',
        '生成时间：' + md.split('\n')[1].replace('_', '').strip(),
    ])
    outro = ('作品信息与落地承诺', [
        'aApp 市场包：remio_aapp_market_prod/yiwu-opc-assistant/yiwu-opc-assistant-v3.zip',
        '源码/GitHub：github.com/yigenfeng0707-netizen/yiwu-global-ai-agent',
        '核心能力：智能体工具调用与自主性（真实网页自主抓取）',
        '落地承诺：获奖后注册落地金义新区、入驻 OPC 社区、39 城复制',
    ])
    blocks = [intro] + blocks + [outro]

    paths = []
    idx = 0
    for heading, paras in blocks:
        chunks = split_chunks(paras)
        for ci, ch in enumerate(chunks):
            title = heading if ci == 0 else f'{heading} ({ci + 1})'
            img = make_slide(ch, title=title)
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
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=300)
    print('ffmpeg rc', r.returncode, r.stderr[-300:])
    if os.path.exists(OUT):
        print('WROTE', OUT, os.path.getsize(OUT), 'bytes')
    # cleanup temp slides
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
