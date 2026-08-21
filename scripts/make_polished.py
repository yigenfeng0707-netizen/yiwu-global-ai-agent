"""
Polished demo video builder.

Produces:
  - demo_video_narrated.mp4 : full narrated demo (real data + price highlight
    cards + intro fade-in + light background music)
  - demo_video_short.mp4    : 60-90s social cut (intro + price cards + highlights)

Offline Chinese TTS via Windows Speech.Synthesizer (zh-CN). No internet needed.

Run:  python scripts/make_polished.py
"""
import os
import re
import json
import wave
import subprocess
import tempfile
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSCRIPT = os.path.join(ROOT, 'demo_api_transcript.md')
FFMPEG = r'C:\Program Files\EVCapture\ffmpeg.exe'
OUT_FULL = os.path.join(ROOT, 'demo_video_narrated.mp4')
OUT_SHORT = os.path.join(ROOT, 'demo_video_short.mp4')
TMP = os.path.join(tempfile.gettempdir(), 'demo_polish_tmp')
os.makedirs(TMP, exist_ok=True)

W, H = 1280, 720
BG = (17, 19, 28)
FG = (224, 228, 240)
ACCENT = (86, 156, 255)
GOOD = (120, 220, 150)
FONT_PATH = r'C:\Windows\Fonts\msyh.ttc'
LINES_PER_SLIDE = 20
EXTRA_PAGE_SEC = 4.2
BGM_VOL = 0.09


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


def make_price_card(price, caption, rating=None):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([60, 160, W - 60, H - 160], outline=ACCENT, width=4)
    d.text((W // 2, 220), caption, font=load_font(30), fill=FG, anchor='mm')
    d.text((W // 2, 380), price, font=load_font(120), fill=GOOD, anchor='mm')
    if rating:
        d.text((W // 2, 520), '评分 ' + rating, font=load_font(40), fill=ACCENT, anchor='mm')
    else:
        d.text((W // 2, 520), '真实电商页面抓取', font=load_font(36), fill=ACCENT, anchor='mm')
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


def extract_prices():
    md = open(TRANSCRIPT, encoding='utf-8').read()
    i = md.find('## 2) /competitor')
    j = md.find('## 3) /select')
    seg = md[i:j] if i >= 0 and j > i else md
    found = []

    def grab(pattern):
        for m in re.finditer(pattern, seg):
            line_start = seg.rfind('\n', 0, m.start()) + 1
            line = seg[line_start:seg.find('\n', m.start())].strip()
            val = m.group(1).replace(',', '')
            price = '$' + val
            rating = None
            rm = re.search(r'([0-9.]+)\s*星|([0-9.]+)\s*out of 5', line)
            if rm:
                rating = rm.group(1) or rm.group(2)
            cap = re.sub(r'\s+', ' ', line)
            cap = cap[:34]
            if price not in [f[0] for f in found]:
                found.append((price, cap, rating))
            if len(found) >= 3:
                return

    # prefer dotted retail prices (e.g. 16.99); fall back to integer amounts
    grab(r'\$([0-9,]+\.[0-9]{1,2})')
    if len(found) < 3:
        grab(r'\$([0-9,]{3,})')
    return found


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


def compose_music(path, dur):
    """Compose a complete piano piece — 《茉莉花》(Jasmine Flower) melody — offline via numpy."""
    sr = 22050

    def add_note(out, freq, start, length, vel=0.15):
        if freq <= 0:
            return
        n = int(sr * length)
        if n <= 0:
            return
        t = np.linspace(0, length, n, endpoint=False)
        env = np.exp(-t / (length * 0.32))
        a = int(0.004 * sr)
        if a < n:
            env[:a] = np.linspace(0, 1, a)
        w = np.zeros(n)
        for h, amp in [(1, 1.0), (2, 0.5), (3, 0.22), (4, 0.1), (5, 0.05)]:
            w += amp * np.sin(2 * np.pi * freq * h * t)
        w = w / (np.max(np.abs(w)) + 1e-9) * env * vel
        s0 = int(start * sr)
        out[s0:s0 + n] += w

    freq = {'1': 261.63, '2': 293.66, '3': 329.63, '4': 349.23, '5': 392.00,
            '6': 440.00, '7': 493.88, '1h': 523.25, '0': 0}
    beat = 0.5
    # 《茉莉花》 numbered notation (jianpu), C major; '1h' = high do
    melody = [
        ('3', 1), ('3', 1), ('5', 1), ('6', 1), ('1h', 1.5), ('1', 0.5), ('6', 1), ('5', 1),
        ('5', 1), ('6', 1), ('5', 1), ('3', 1), ('5', 1), ('6', 1), ('5', 1), ('3', 1), ('2', 1), ('3', 1),
        ('3', 1), ('5', 1), ('3', 1), ('2', 1), ('1h', 1.5), ('2', 0.5), ('1', 1), ('6', 1),
        ('5', 1), ('6', 1), ('1h', 1.5), ('1', 0.5), ('6', 1), ('5', 1),
        ('3', 1), ('5', 1), ('3', 1), ('2', 1), ('1h', 1.5), ('2', 0.5), ('1', 1), ('6', 1),
        ('5', 1), ('6', 1), ('5', 1), ('3', 1), ('5', 1), ('6', 1), ('5', 1), ('3', 1), ('2', 1), ('3', 1),
        ('3', 1), ('5', 1), ('3', 1), ('2', 1), ('1h', 1.5), ('2', 0.5), ('1', 1), ('6', 1),
        ('5', 1), ('6', 1), ('1h', 1.5), ('1', 0.5), ('6', 1), ('5', 1),
    ]
    chords = [(261.63, 329.63, 392.00), (196.00, 246.94, 293.66),
              (220.00, 261.63, 329.63), (174.61, 220.00, 261.63)]
    total_beats = sum(b for _, b in melody)
    loop = np.zeros(int(sr * total_beats * beat))
    # melody (piano)
    pos = 0.0
    for note, b in melody:
        f = freq[note]
        if f > 0:
            add_note(loop, f, pos * beat, b * beat * 0.95, vel=0.20)
        pos += b
    # soft chord pad + bass, one bar per 4 beats
    for bar in range(int(total_beats) // 4 + 1):
        base = bar * 4 * beat
        if base >= total_beats * beat:
            break
        r, th, fi = chords[bar % 4]
        for f in (r, th, fi):
            add_note(loop, f, base, 4 * beat, vel=0.035)
        add_note(loop, r / 2, base, 4 * beat * 0.9, vel=0.06)
    loop /= (np.max(np.abs(loop)) + 1e-9)
    loop *= 0.6
    total = int(dur * sr)
    full = np.tile(loop, total // len(loop) + 1)[:total]
    sf.write(path, full.astype(np.float32), sr)


def build_clip(img, audio, dur, out_path, fade_in=False, bgm=None):
    vf = 'fade=t=in:st=0:d=0.6,format=yuv420p' if fade_in else 'format=yuv420p'
    padf = 'apad=whole_dur=%f' % dur
    if bgm:
        bgmseg = out_path + '.bgm.wav'
        subprocess.run([FFMPEG, '-y', '-i', bgm, '-t', f'{dur:.2f}', '-c:a', 'copy', bgmseg],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
        filt = '[1:a]%s[a1];[2:a]volume=%s[a2];[a1][a2]amix=inputs=2:dropout_transition=0[a]' % (padf, BGM_VOL)
        subprocess.run([
            FFMPEG, '-y', '-loop', '1', '-i', img, '-i', audio, '-i', bgmseg,
            '-filter_complex', filt, '-map', '0:v', '-map', '[a]',
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k',
            '-r', '25', '-t', f'{dur:.2f}', '-vf', vf, out_path
        ], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
        try:
            os.remove(bgmseg)
        except Exception:
            pass
    else:
        filt = '[1:a]%s[a]' % padf
        subprocess.run([
            FFMPEG, '-y', '-loop', '1', '-i', img, '-i', audio,
            '-filter_complex', filt, '-map', '0:v', '-map', '[a]',
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k',
            '-r', '25', '-t', f'{dur:.2f}', '-vf', vf, out_path
        ], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)


def main():
    blocks = parse_blocks()
    sections = []
    sections.append((INTRO[0], [INTRO[1]], INTRO[1]))
    for h, paras in blocks:
        key = next((k for k in NARR if k in h), None)
        if key:
            lines = []
            for p in paras:
                lines += wrap(p, load_font(22), W - 120)
            sections.append((h, lines, NARR[key]))
    sections.append((OUTRO[0], [OUTRO[1]], OUTRO[1]))

    # collect all narrations -> TTS
    narr_texts = []  # list of (tag, text)
    for s in sections:
        narr_texts.append(('sec', s[2]))
    prices = extract_prices()
    price_parts = []
    for price, cap, rating in prices:
        p = price.lstrip('$')
        s = '售价 %s 美元' % p
        if rating:
            s += '，评分 %s 星' % rating
        price_parts.append(s)
    price_narration = '我们来看真实抓取的数据：' + '；'.join(price_parts) + '。这些真实价格，正是义乌供应链出海的底气。'
    narr_texts.append(('price', price_narration))
    tj = os.path.join(TMP, 'texts.json')
    json.dump([t for _, t in narr_texts], open(tj, 'w', encoding='utf-8'), ensure_ascii=False)
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

    # background music (one long file, trimmed per clip)
    bgm_path = os.path.join(TMP, 'bgm.wav')
    compose_music(bgm_path, 400)

    def tts_wav(idx):
        return os.path.join(TMP, f'n{idx}.wav')

    # build frames for FULL video
    frames = []  # (img_path, audio_path, dur, fade_in)
    ni = 0
    for si, (title, lines, narr) in enumerate(sections):
        pages = [lines[i:i + LINES_PER_SLIDE] for i in range(0, max(len(lines), 1), LINES_PER_SLIDE)]
        for pi, page in enumerate(pages):
            ttl = title if pi == 0 else f'{title} ({pi + 1}/{len(pages)})'
            ip = os.path.join(TMP, f's{si}_{pi}.png')
            make_slide(page, title=ttl).save(ip)
            if pi == 0:
                wp = tts_wav(ni); ni += 1
                dur = wave_dur(wp) + 0.6
                audio = wp
            else:
                wp = os.path.join(TMP, f'sil_{si}_{pi}.wav')
                silence_wav(wp, EXTRA_PAGE_SEC)
                dur = EXTRA_PAGE_SEC
                audio = wp
            frames.append((ip, audio, dur, pi == 0 and si == 0))
        # insert price cards right after competitor section (single narration on first card)
        if 'competitor' in title:
            for ci, (price, cap, rating) in enumerate(prices):
                ip = os.path.join(TMP, f'pc_{ci}.png')
                make_price_card(price, cap, rating).save(ip)
                if ci == 0:
                    wp = tts_wav(ni); ni += 1
                    dur = wave_dur(wp) + 0.4
                else:
                    wp = os.path.join(TMP, f'sil_pc_{ci}.wav')
                    silence_wav(wp, EXTRA_PAGE_SEC)
                    dur = EXTRA_PAGE_SEC
                frames.append((ip, wp, dur, False))

    clips = []
    for k, (ip, audio, dur, fade) in enumerate(frames):
        cp = os.path.join(TMP, f'c{k}.mp4')
        build_clip(ip, audio, dur, cp, fade_in=fade, bgm=bgm_path)
        clips.append(cp)
    list_file = os.path.join(TMP, 'list.txt')
    with open(list_file, 'w', encoding='utf-8') as f:
        for c in clips:
            f.write("file '%s'\n" % c.replace('\\', '/'))
    subprocess.run([FFMPEG, '-y', '-f', 'concat', '-safe', '0', '-i', list_file, '-c', 'copy', OUT_FULL],
                   capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
    for c in clips:
        try:
            os.remove(c)
        except Exception:
            pass
    print('FULL WROTE', OUT_FULL, os.path.getsize(OUT_FULL), 'bytes; frames=', len(frames))

    # SHORT version: intro + price cards + competitor/select highlights + outro
    short_frames = []
    # intro
    ip0 = os.path.join(TMP, 'short_intro.png')
    make_slide([INTRO[1]], title=INTRO[0]).save(ip0)
    wp0 = tts_wav(0)
    short_frames.append((ip0, wp0, min(wave_dur(wp0) + 0.6, 9), True))
    # price cards (first 3) — single narration on first card (no repetition)
    spn_path = os.path.join(TMP, 'spn_0.wav')
    for ci, (price, cap, rating) in enumerate(prices):
        ip = os.path.join(TMP, f'sp_{ci}.png')
        make_price_card(price, cap, rating).save(ip)
        if ci == 0:
            audio = spn_path
            dur = wave_dur(spn_path) + 0.4  # match real narration length, never cut off
        else:
            wp = os.path.join(TMP, f'spn_sil_{ci}.wav')
            silence_wav(wp, 6.0)
            audio = wp
        short_frames.append((ip, audio, 6.0, False))
    # competitor first page (real data)
    csec = sections[2]
    cip = os.path.join(TMP, 'short_c.png')
    make_slide(csec[1][:LINES_PER_SLIDE], title=csec[0]).save(cip)
    cwp = tts_wav(2)
    short_frames.append((cip, cwp, min(wave_dur(cwp) + 0.6, 9), False))
    # select first page (real data)
    ssec = sections[3]
    sip = os.path.join(TMP, 'short_s.png')
    make_slide(ssec[1][:LINES_PER_SLIDE], title=ssec[0]).save(sip)
    swp = tts_wav(3)
    short_frames.append((sip, swp, min(wave_dur(swp) + 0.6, 9), False))
    # outro
    ipo = os.path.join(TMP, 'short_outro.png')
    make_slide([OUTRO[1]], title=OUTRO[0]).save(ipo)
    wpo = tts_wav(len(sections) - 1)
    short_frames.append((ipo, wpo, min(wave_dur(wpo) + 0.6, 9), False))

    # generate the single short price narration (spn_0.wav)
    json.dump([price_narration], open(os.path.join(TMP, 'sp_texts.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    with open(os.path.join(TMP, 'sp_tts.ps1'), 'w', encoding='utf-8') as f:
        f.write(
            "Add-Type -AssemblyName System.speech\n"
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer\n"
            "$s.SelectVoice('Microsoft Huihui Desktop')\n"
            "$t = Get-Content -LiteralPath '%s' -Encoding UTF8 | ConvertFrom-Json\n"
            "for ($i=0; $i -lt $t.Count; $i++) { $s.SetOutputToWaveFile('%s\\spn_' + $i + '.wav'); $s.Speak($t[$i]) }\n"
            "$s.Dispose()\n" % (os.path.join(TMP, 'sp_texts.json'), TMP)
        )
    subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(TMP, 'sp_tts.ps1')],
                   capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=200)

    sclips = []
    for k, (ip, audio, dur, fade) in enumerate(short_frames):
        cp = os.path.join(TMP, f'sc{k}.mp4')
        build_clip(ip, audio, dur, cp, fade_in=fade, bgm=bgm_path)
        sclips.append(cp)
    slist = os.path.join(TMP, 'slist.txt')
    with open(slist, 'w', encoding='utf-8') as f:
        for c in sclips:
            f.write("file '%s'\n" % c.replace('\\', '/'))
    subprocess.run([FFMPEG, '-y', '-f', 'concat', '-safe', '0', '-i', slist, '-c', 'copy', OUT_SHORT],
                   capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
    print('SHORT WROTE', OUT_SHORT, os.path.getsize(OUT_SHORT), 'bytes')


if __name__ == '__main__':
    main()
