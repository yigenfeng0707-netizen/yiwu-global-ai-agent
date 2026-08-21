"""
Headless demo capture for 义乌小商品出海智能体-OPC (yiwu-opc-assistant aApp).

Replays the aApp's exact behavior via remio CLI syscalls (rag / headless_fetch_content
/ run_prompt) and writes a timestamped, real-output transcript to demo_api_transcript.md.
This is an API-driven "demo recording": no screen capture or manual UI driving required.

Run:  python scripts/demo_capture.py
Prereq: remio desktop (remiocn) running; aApp knowledge base present.
"""
import subprocess
import json
import os
import time
import urllib.parse
from datetime import datetime

REMIO = r'C:\Users\18969\AppData\Local\Programs\remio-cli\remio.exe'
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'demo_api_transcript.md')

AGENT_PROFILE = ('你是「义乌小商品出海智能体-OPC」的核心分析引擎，服务于义乌小商品跨境卖家与 OPC 一人外贸公司。'
                 '回答用中文，结构清晰、可落地。')
INTENTS = {
    'select': '基于知识库做 3-5 个适合义乌供应链、可走 1039、具备跨境溢价空间的品类推荐，说明选品逻辑与目标市场。',
    'compliance': '做跨境合规与认证、RCEP 关税、1039 通关的检查清单，标出高风险项与应对建议。',
    'policy': '说明如何把成熟市场跨境电商政策复制到新市场或复制到金义新区落地，给出政策清单与落地步骤。',
}


def remio(args, timeout=150):
    p = subprocess.run([REMIO, '--cn'] + args, capture_output=True, text=True, encoding='utf-8', timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def call_syscall(action, payload, timeout=150):
    return remio(['syscall', action, json.dumps(payload, ensure_ascii=False)], timeout=timeout)


def _extract(obj, *keys, default=''):
    cur = obj
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
    return cur if cur not in (None, '') else default


def rag(question, intent_key=None, timeout=150):
    prompt = question
    if intent_key:
        prompt = question + '\n\n' + AGENT_PROFILE + '\n' + INTENTS[intent_key]
    rc, out, err = remio(['rag', prompt], timeout=timeout)
    if rc != 0:
        return f'[rag failed rc={rc}] {err[:300]}'
    try:
        return _extract(json.loads(out), 'data', 'content') or out
    except Exception:
        return out


def headless_fetch(url, timeout=70):
    rc, out, err = call_syscall('headless_fetch_content', {'url': url}, timeout=timeout)
    if rc != 0:
        return None, f'[fetch failed rc={rc}] {err[:200]}'
    try:
        d = json.loads(out).get('data', {})
        return d.get('title', ''), d.get('text', '') or ''
    except Exception:
        return None, out[:300]


def synthesize(prompt, timeout=90):
    rc, out, err = call_syscall('run_prompt', {'prompt': prompt, 'capabilities': 'none', 'system_prompt': AGENT_PROFILE}, timeout=timeout)
    if rc != 0:
        return f'[llm failed rc={rc}] {err[:200]}'
    try:
        return json.loads(out).get('data', {}).get('output', '') or out[:500]
    except Exception:
        return out[:500]


def build_search_urls(query):
    q = urllib.parse.quote(query)
    return [
        f'https://www.amazon.com/s?k={q}',
        f'https://www.aliexpress.com/wholesale?SearchText={q}',
        f'https://s.1688.com/offer/offer_search.htm?keywords={q}',
    ]


def section(title):
    return f'\n\n## {title}\n_{datetime.now().strftime("%H:%M:%S")}_\n'


def main():
    L = []
    L.append(f'# aApp 演示实录（API 驱动 / remio 官方工具）\n_生成时间 {datetime.now().isoformat(timespec="seconds")}_\n')
    L.append('\n> 本实录通过 `remio --cn` CLI 直接调用 aApp 所用的同一组 syscall（rag / headless_fetch_content / run_prompt）重放，'
            '输出均为 remio 运行时真实返回，可作为演示证据。')

    L.append(section('1) /ask — 1039 市场采购免税（知识库 RAG + 引用）'))
    L.append(rag('1039 市场采购贸易方式如何免征增值税、简化申报？'))

    L.append(section('2) /competitor-research — 竞品实采：无线耳机（真实无头浏览器抓取）'))
    query = '无线耳机'
    snippets = []
    for url in build_search_urls(query):
        L.append(f'\n### 抓取：{url}')
        title, text = headless_fetch(url)
        if text:
            L.append(f'- 标题：{title}\n- 正文摘要（前 600 字）：\n\n{text[:600]}')
            snippets.append(f'## 来源：{title}\n{text[:3500]}')
        else:
            L.append(f'- {text}')
    if snippets:
        L.append('\n### LLM 竞品洞察提炼')
        prompt = (f'以下是针对「{query}」从 Amazon / AliExpress / 1688 真实抓取的竞品页面正文。'
                  '请提炼：1) 价格区间与定位；2) 头部卖家共性卖点；3) 差异化机会；4) 对义乌供应链卖家的选品与定价建议。\n\n'
                  + '\n\n---\n\n'.join(snippets))
        L.append(synthesize(prompt))

    L.append(section('3) /select-product — 智能选品推荐'))
    L.append(rag('为义乌跨境卖家做智能选品推荐', 'select'))

    L.append(section('4) /compliance-check — 跨境合规检查'))
    L.append(rag('做一份义乌小商品出海通用跨境合规检查清单', 'compliance'))

    L.append(section('5) /policy-replicate — 政策复制与金义新区落地'))
    L.append(rag('如何做跨境电商政策复制与金义新区落地', 'policy'))

    L.append('\n\n---\n_实录结束。所有输出来自 remio 官方工具真实调用。_')
    content = '\n'.join(L)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(content)
    print('WROTE', OUT, 'bytes=', len(content.encode('utf-8')))


if __name__ == '__main__':
    t0 = time.time()
    main()
    print('ELAPSED %.1fs' % (time.time() - t0))
