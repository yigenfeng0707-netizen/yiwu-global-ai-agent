"""
Build a 30-ish second pitch HOOK video (demo_video_hook.mp4).

Reuses the polished video engine: a punchy spoken hook (judge-facing), two real
price cards (the "real data" punch), and a closing card. Piano BGM underneath.

Run:  python scripts/make_hook_video.py
"""
import os
import re
import json
import subprocess
import tempfile

import make_polished as mp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'demo_video_hook.mp4')
AUTOTMP = os.path.join(tempfile.gettempdir(), 'demo_hook_tmp')
os.makedirs(AUTOTMP, exist_ok=True)
FFMPEG = mp.FFMPEG

HOOK = ('各位评委好。我们做的是义乌小商品出海智能体——一个真正会自己干活的 AI。'
        '你只给它一个目标，比如跑通无线耳机跨境出海，它就会自己决定：先查 1039 免税政策，'
        '再上网实采沃尔玛的真实价格，然后自己选品、查合规、规划金义新区落地。全程真实数据、零合成。'
        '它基于赛事官方工具 remio 原生构建，获奖后立刻落地金义新区。一人加 AI，就是一家外贸公司。请看演示。')

prices = mp.extract_prices()[:2]
pp = []
for price, cap, rating in prices:
    p = price.lstrip('$')
    s = '售价 %s 美元' % p
    if rating:
        s += '，评分 %s 星' % rating
    pp.append(s)
price_narration = '来看真实抓取：' + '；'.join(pp) + '。这就是义乌供应链的底气。'

CLOSE = 'demo_video_autonomous.mp4 即该智能体实时跑通的完整实录；aApp 与源码均已开源。'


def main():
    narr = [HOOK, price_narration, CLOSE]
    tj = os.path.join(AUTOTMP, 'texts.json')
    json.dump(narr, open(tj, 'w', encoding='utf-8'), ensure_ascii=False)
    ps1 = os.path.join(AUTOTMP, 'tts.ps1')
    with open(ps1, 'w', encoding='utf-8') as f:
        f.write(
            "Add-Type -AssemblyName System.speech\n"
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer\n"
            "$s.SelectVoice('Microsoft Huihui Desktop')\n"
            "$t = Get-Content -LiteralPath '%s' -Encoding UTF8 | ConvertFrom-Json\n"
            "for ($i=0; $i -lt $t.Count; $i++) { $s.SetOutputToWaveFile('%s\\n' + $i + '.wav'); $s.Speak($t[$i]) }\n"
            "$s.Dispose()\n" % (tj, AUTOTMP)
        )
    subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ps1],
                   capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=200)

    bgm = os.path.join(AUTOTMP, 'bgm.wav')
    mp.compose_music(bgm, 120)

    def tw(i):
        return os.path.join(AUTOTMP, f'n{i}.wav')

    frames = []
    # hook
    hip = os.path.join(AUTOTMP, 'hook.png')
    mp.make_slide(mp.wrap(HOOK, mp.load_font(26), mp.W - 160), title='路演开场 · 30 秒 Hook').save(hip)
    frames.append((hip, tw(0), min(mp.wave_dur(tw(0)) + 0.6, 32), True))
    # price cards
    for ci, (price, cap, rating) in enumerate(prices):
        pip = os.path.join(AUTOTMP, f'pc_{ci}.png')
        mp.make_price_card(price, cap, rating).save(pip)
        if ci == 0:
            dur = mp.wave_dur(tw(1)) + 0.4
            audio = tw(1)
        else:
            wp = os.path.join(AUTOTMP, f'sil_{ci}.wav')
            mp.silence_wav(wp, 5.0)
            dur = 5.0
            audio = wp
        frames.append((pip, audio, dur, False))
    # close
    cip = os.path.join(AUTOTMP, 'close.png')
    mp.make_slide(mp.wrap(CLOSE, mp.load_font(26), mp.W - 160), title='demo_video_autonomous.mp4').save(cip)
    frames.append((cip, tw(2), min(mp.wave_dur(tw(2)) + 0.6, 8), False))

    clips = []
    for k, (ip, audio, dur, fade) in enumerate(frames):
        cp = os.path.join(AUTOTMP, f'c{k}.mp4')
        mp.build_clip(ip, audio, dur, cp, fade_in=fade, bgm=bgm)
        clips.append(cp)
    lf = os.path.join(AUTOTMP, 'list.txt')
    with open(lf, 'w', encoding='utf-8') as f:
        for c in clips:
            f.write("file '%s'\n" % c.replace('\\', '/'))
    subprocess.run([FFMPEG, '-y', '-f', 'concat', '-safe', '0', '-i', lf, '-c', 'copy', OUT],
                   capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
    print('HOOK WROTE', OUT, os.path.getsize(OUT), 'bytes')


if __name__ == '__main__':
    main()
