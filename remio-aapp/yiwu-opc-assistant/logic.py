import os
import urllib.parse

from remio_sdk import create_aapp_logger, router, syscall, syscall_stream

AAPP_DIR = os.environ.get('REMIO_AAPP_DIR', '')
LOG_DIR = os.environ.get('REMIO_AAPP_LOG_DIR', os.path.join(os.path.dirname(AAPP_DIR), 'log'))
LOGGER = create_aapp_logger('yiwu-opc-assistant', LOG_DIR, 'main')

KB_NAME = '义乌跨境 OPC 知识库'

AGENT_PROFILE = (
    '你是「义乌小商品出海智能体-OPC」的核心分析引擎，服务于义乌小商品跨境卖家与 OPC 一人外贸公司。'
    '回答用中文，结构清晰、可落地，必要时给出可执行步骤与风险提醒。'
)

INTENTS = {
    'select': (
        '基于 remio 知识库「义乌跨境 OPC 知识库」中的智能选品方法论与产业带信息，'
        '为用户做选品推荐：给出 3-5 个适合义乌供应链、可走 1039 市场采购、具备跨境溢价空间的品类，'
        '并说明选品逻辑、目标市场与起步建议。'
    ),
    'compliance': (
        '基于 remio 知识库中的跨境合规与认证、RCEP 关税优惠、1039 市场采购贸易方式等资料，'
        '做一份合规检查清单：覆盖资质/认证、申报/税务、平台规则与关税优惠利用，'
        '并标出高风险项与应对建议。'
    ),
    'policy': (
        '基于 remio 知识库中的金义新区产业带与落地政策、OPC 政策复制方法，'
        '说明如何把一个成熟市场的跨境电商政策/扶持做法复制到新市场或复制到金义新区落地，'
        '给出可复制的政策清单与落地步骤。'
    ),
}


def _extract(res, key):
    if not isinstance(res, dict):
        return None
    if res.get(key) not in (None, '', []):
        return res.get(key)
    data = res.get('data') or {}
    return data.get(key) if isinstance(data, dict) else None


def _stream_rag(question, system_prompt=None):
    def on_stream_event(event):
        event_type = event.get('type', '')
        if event_type == 'progress':
            syscall('show_progress', {
                'text': event.get('text', ''),
                'toolName': event.get('toolName', ''),
                'toolId': event.get('toolId', ''),
            })
        elif event_type == 'progress_done':
            syscall('show_progress', {'text': '', 'toolId': event.get('toolId', ''), 'status': 'done'})
        elif event_type == 'text_delta':
            syscall('send_chat_message', {'content': event.get('delta', ''), 'stream': True})
        elif event_type == 'citation':
            syscall('send_chat_message', {
                'citation': {
                    'noteId': event.get('noteId', ''),
                    'content': event.get('content', ''),
                    'index': event.get('index', 0),
                },
                'stream': True,
            })

    payload = {
        'question': question,
        'include_citations': True,
        'enable_direct_answer': True,
    }
    if system_prompt:
        payload['system_prompt'] = system_prompt
    syscall_stream('rag_stream', payload, on_event=on_stream_event)
    syscall('send_chat_message', {'content': '', 'stream': True, 'stream_end': True})


def _build_search_urls(query):
    q = urllib.parse.quote(query)
    return [
        f'https://www.amazon.com/s?k={q}',
        f'https://www.aliexpress.com/wholesale?SearchText={q}',
        f'https://s.1688.com/offer/offer_search.htm?keywords={q}',
    ]


def _summarize_with_llm(prompt):
    try:
        res = syscall('run_prompt', {'prompt': prompt, 'capabilities': 'none', 'system_prompt': AGENT_PROFILE})
        return _extract(res, 'text') or _extract(res, 'answer') or ''
    except Exception as exc:  # noqa: BLE001
        LOGGER.warn('yiwu.llm.fail', str(exc))
        return ''


@router.route('GET', '/welcome')
def handle_welcome(_params):
    return ('我是义乌小商品出海助手（v2），基于 remio 知识库「义乌跨境 OPC 知识库」+ 真实网页自主抓取。'
            '能力：①知识库问答 / 选品推荐 / 合规检查 / 政策复制；'
            '②竞品实采——我会自主用无头浏览器抓取 Amazon、AliExpress、1688 的真实竞品页面并提炼洞察。')


@router.route('POST', '/ask')
def handle_ask(params):
    question = str(params.get('input', '')).strip()
    if not question:
        return {'error': 'input is required'}
    LOGGER.info('yiwu.ask.start', 'rag stream', {'len': len(question)})
    _stream_rag(question)
    LOGGER.info('yiwu.ask.done', 'ok')
    return {}


@router.route('POST', '/competitor-research')
def handle_competitor_research(params):
    query = str(params.get('input', '')).strip()
    if not query:
        return {'error': 'input is required (product / category to research)'}

    LOGGER.info('yiwu.competitor.start', query)
    syscall('send_chat_message', {'content': f'🔍 竞品实采启动：针对「{query}」自主抓取真实电商页面…', 'stream': True})

    urls = _build_search_urls(query)
    snippets = []
    for url in urls:
        syscall('show_progress', {'text': f'无头浏览器抓取：{url}', 'toolName': 'headless_fetch_content'})
        try:
            res = syscall('headless_fetch_content', {'url': url, 'timeout_ms': 20000})
            text = _extract(res, 'text') or ''
            title = _extract(res, 'title') or url
            if text:
                snippets.append(f'## 来源：{title}\n{text[:3500]}')
                syscall('send_chat_message', {
                    'content': f'\n\n✅ 已抓取：{title}（{len(text)} 字符）\n', 'stream': True})
            else:
                syscall('send_chat_message', {'content': f'\n\n⚠️ 页面无正文：{url}\n', 'stream': True})
        except Exception as exc:  # noqa: BLE001
            LOGGER.warn('yiwu.fetch.fail', str(exc))
            syscall('send_chat_message', {'content': f'\n\n⚠️ 抓取失败：{url}\n', 'stream': True})
        syscall('show_progress', {'text': '', 'toolName': 'headless_fetch_content', 'status': 'done'})

    if snippets:
        prompt = (
            f'以下是针对「{query}」从 Amazon / AliExpress / 1688 真实抓取的竞品页面正文。'
            '请提炼结构化竞品洞察（用中文，分点）：\n'
            '1) 价格区间与定位；2) 头部卖家的共性卖点；3) 差异化机会与空白点；'
            '4) 对义乌供应链卖家的选品与定价建议。\n\n'
            + '\n\n---\n\n'.join(snippets)
        )
        analysis = _summarize_with_llm(prompt)
        if analysis:
            syscall('send_chat_message', {'content': '\n\n### 🧠 竞品洞察分析\n' + analysis, 'stream': True})
        else:
            syscall('send_chat_message', {'content': '\n\n（实时 LLM 分析暂不可用，已为你保留原始抓取内容）', 'stream': True})
    else:
        syscall('send_chat_message', {
            'content': '\n\n实时网页抓取本次无结果，已回退到知识库给出选品与合规建议：\n', 'stream': True})
        _stream_rag(f'{query} 的跨境选品与竞品策略', system_prompt=AGENT_PROFILE)

    syscall('send_chat_message', {'content': '', 'stream': True, 'stream_end': True})
    LOGGER.info('yiwu.competitor.done', 'ok', {'snippets': len(snippets)})
    return {}


@router.route('POST', '/select-product')
def handle_select_product(params):
    query = str(params.get('input', '')).strip()
    question = (f'为「{query}」做智能选品推荐' if query else '做一份通用义乌小商品跨境选品推荐')
    LOGGER.info('yiwu.select.start', question)
    _stream_rag(question, system_prompt=AGENT_PROFILE + '\n' + INTENTS['select'])
    LOGGER.info('yiwu.select.done', 'ok')
    return {}


@router.route('POST', '/compliance-check')
def handle_compliance_check(params):
    query = str(params.get('input', '')).strip()
    question = (f'针对「{query}」做跨境合规检查' if query else '做一份义乌小商品出海通用合规检查清单')
    LOGGER.info('yiwu.compliance.start', question)
    _stream_rag(question, system_prompt=AGENT_PROFILE + '\n' + INTENTS['compliance'])
    LOGGER.info('yiwu.compliance.done', 'ok')
    return {}


@router.route('POST', '/policy-replicate')
def handle_policy_replicate(params):
    query = str(params.get('input', '')).strip()
    question = (f'如何把政策复制到「{query}」' if query else '如何做跨境电商政策复制与金义新区落地')
    LOGGER.info('yiwu.policy.start', question)
    _stream_rag(question, system_prompt=AGENT_PROFILE + '\n' + INTENTS['policy'])
    LOGGER.info('yiwu.policy.done', 'ok')
    return {}


handle = router.handle
