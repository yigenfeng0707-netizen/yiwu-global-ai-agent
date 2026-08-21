"""
Build a narrated promo video (demo_video_narrated.mp4) from the API demo transcript.

- Keeps each endpoint section's REAL content (product titles, prices, ratings,
  citations) and paginates it, so the video shows concrete data, not just titles.
- Adds offline Chinese voiceover via Windows Speech.Synthesizer (zh-CN, no internet).
- Each section's first page carries the narration; subsequent pages scroll in silence.

Run:  python scripts/make_narrated_video.py
"""
import os
import re
import json
import wave
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSCRIPT = os.path.join(ROOT, 'demo_api_transcript.md')
FFMPEG = r'C:\Program Files\EVCapture\ffmpeg.exe'
OUT = os.path.join(ROOT, 'demo_video_narrated.mp4')
TMP = os.path.join(tempfile.gettempdir(), 'demo_narr_tmp')
os.makedirs(TMP, exist_ok=True)

W, H = 1280, 720
BG = (17, 19, 28)
FG = (224, 228, 240)
ACCENT = (86, 156, 255)
FONT_PATH = r'C:\Windows\Fonts\msyh.ttc'
LINES_PER_SLIDE = 20
EXTRA_PAGE_SEC = 4.5


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


def silence_wav(path, dur):
    subprocess.run([FFMPEG, '-y', '-f', 'lavfi', '-i', 'anullsrc=r=22050:cl=mono',
                    '-t', f'{dur:.2f}', '-c:a', 'pcm_s16le', path],
                   capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)


def wave_dur(path):
    try:
        with wave.open(path, 'rb') as wf:
            return wf.getnframes() / float(wf.getframerate())
    except Exception:
        return 2.0


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


NARR = {
    '## 1) /ask': '下面演示知识库问答。智能体基于 remio 官方知识库，回答 1039 市场采购贸易方式如何免征增值税，并附带来源引用。',
    '## 2) /competitor-research': '核心能力演示：竞品实采。智能体自主调用无头浏览器，真实抓取沃尔玛、亚马逊等电商页面，提取无线耳机的真实价格、评分与卖点。',
    '## 3) /select-product': '智能选品推荐。基于知识库，给出适合义乌供应链、可走 1039、具备跨境溢价空间的品类建议。',
    '## 4) /compliance-check': '跨境合规检查。列出认证、申报、税务与平台规则的检查清单，并标出高风险项。',
    '## 5) /policy-replicate': '政策复制与金义新区落地。说明如何把成熟市场的跨境电商政策，复制到新市场或复制到金义新区。',
}
INTRO = ('义乌小商品出海智能体-OPC',
         '欢迎观看本作品演示。它参加金漪湖论剑 2026 智能体 OPC 创新创业大赛，基于官方工具 remio 睿妙构建知识库与智能体应用，作品名称为义乌小商品出海助手。')
OUTRO = ('作品信息与落地承诺',
         '本作品已发布到 remio 应用市场，源码开源。核心能力是智能体的工具调用与自主性。若获奖，我们将注册落地金义新区、入驻 OPC 社区，并向全国三十九个试点城市复制推广。')


def main():
    blocks = parse_blocks()
    sections = []  # (title, content_lines, narration)
    sections.append((INTRO[0], [INTRO[1]], INTRO[1]))
    for h, paras in blocks:
        key = next((k for k in NARR if k in h), None)
        if key:
            lines = []
            for p in paras:
                lines += wrap(p, load_font(22), W - 120)
            sections.append((h, lines, NARR[key]))
    sections.append((OUTRO[0], [OUTRO[1]], OUTRO[1]))

    # TTS: one wav per section that has narration
    narr_map = {}
    for si, (title, lines, narr) in enumerate(sections):
        if narr:
            narr_map[si] = narr
    tj = os.path.join(TMP, 'texts.json')
    json.dump([narr_map[k] for k in sorted(narr_map)], open(tj, 'w', encoding='utf-8'), ensure_ascii=False)
    ps1 = os.path.join(TMP, 'tts.ps1')
    with open(ps1, 'w', encoding='utf-8') as f:
        f.write(
            "Add-Type -AssemblyName System.speech\n"
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer\n"
            "$s.SelectVoice('Microsoft Huihui Desktop')\n"
            "$texts = Get-Content -LiteralPath '%s' -Encoding UTF8 | ConvertFrom-Json\n"
            "for ($i=0; $i -lt $texts.Count; $i++) {\n"
            "  $s.SetOutputToWaveFile('%s\\n' + $i + '.wav')\n"
            "  $s.Speak($texts[$i])\n"
            "}\n"
            "$s.Dispose()\n" % (tj, TMP)
        )
    subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ps1],
                   capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300)

    clips = []
    narr_keys = sorted(narr_map)
    for si, (title, lines, narr) in enumerate(sections):
        pages = [lines[i:i + LINES_PER_SLIDE] for i in range(0, max(len(lines), 1), LINES_PER_SLIDE)]
        for pi, page in enumerate(pages):
            ttl = title if pi == 0 else f'{title} ({pi + 1}/{len(pages)})'
            img = make_slide(page, title=ttl)
            ip = os.path.join(TMP, f's{si}_{pi}.png')
            cp = os.path.join(TMP, f'c{si}_{pi}.mp4')
            img.save(ip)
            if pi == 0 and si in narr_map:
                ki = narr_keys.index(si)
                wp = os.path.join(TMP, f'n{ki}.wav')
                dur = wave_dur(wp) + 0.6
                audio = wp
            else:
                wp = os.path.join(TMP, f'sil_{si}_{pi}.wav')
                dur = EXTRA_PAGE_SEC
                silence_wav(wp, dur)
                audio = wp
            subprocess.run([
                FFMPEG, '-y', '-loop', '1', '-i', ip, '-i', audio,
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k',
                '-r', '25', '-t', f'{dur:.2f}', '-shortest', cp
            ], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
            clips.append(cp)

    list_file = os.path.join(TMP, 'list.txt')
    with open(list_file, 'w', encoding='utf-8') as f:
        for c in clips:
            f.write("file '%s'\n" % c.replace('\\', '/'))
    subprocess.run([
        FFMPEG, '-y', '-f', 'concat', '-safe', '0', '-i', list_file, '-c', 'copy', OUT
    ], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)

    for c in clips:
        try:
            os.remove(c)
        except Exception:
            pass
    print('WROTE', OUT, os.path.getsize(OUT), 'bytes; sections=', len(sections))


if __name__ == '__main__':
    main()
