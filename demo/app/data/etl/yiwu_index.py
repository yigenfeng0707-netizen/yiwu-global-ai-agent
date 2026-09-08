"""源B：义乌指数官方发布值数据源（ywindex.com/report）

P1-1 叙事皇冠：用义乌指数官网《报告》栏目服务器渲染的文章正文里
**官方公开发布**的品类指数值，替换 demo 里 `random.uniform(98,110)` 伪造的
"义乌指数"和 `YIWU_INDEX.current=102.8` 常量冒充实时的痛点。

诚实标注（重要，答辩口径）：
  - 官网首页/数据面板为 Nuxt SPA + 腾讯验证码，实时面板需登录订阅，无法稳定抓取；
  - 但 /report 栏目文章正文为服务器渲染，内含官方公布的品类指数值与日期，
    例如「2026年7月伞具类指数为1576.52点」「五金工具类指数自年初的1463.99点
    上涨至2026年6月的1557.03点」「体育娱乐用品类指数2025年11月达到峰值1767.76点」；
  - 因此本源定位为"**官方发布值·定期更新**"，而非"实时"；
  - 官方义乌指数为千点基准（景气类），与 demo 旧 98~110 标度不同，不可混用，
    故 parse 结果显式携带 index_scale="官方千点基准" 与每条的 as_of 日期。

解析失败（0 条）时 validate 不通过 → is_real=False → 上层回退上次成功值/演示基准。
"""

from __future__ import annotations

import html as html_lib
import re
from typing import Any, Dict, List, Union

from .base import RealDataSource

REPORT_URL = "https://www.ywindex.com/report"

# 句子切分：中文句号/问号/叹号/分号/换行
_SENT_SPLIT = re.compile(r"[。！？；\n]")
# 品类：强制带「类」字——义乌指数具体品类一律表述为「XX类指数」（如"五金工具类指数"）
# 不带"类"的泛指"义乌指数"由 _RE_COMPOSITE 兜底，避免把"据义乌/从义乌"误当品类
_RE_CATEGORY = re.compile(r"([\u4e00-\u9fa5]{1,12}?)类指数")
# 综合指数句：直接提"义乌指数"而未指明具体品类（如"义乌指数攀升至1550.67点"）
_RE_COMPOSITE = re.compile(r"义乌指数")
# 指数值：「1576.52点」（千点基准，3~4 位整数 + 1~2 位小数）
_RE_VALUE = re.compile(r"(\d{3,4}\.\d{1,2})\s*点")
# 日期：「2026年7月」/「2025年11月」/「2026年」/「年初」/「年末」
_RE_DATE = re.compile(r"(\d{4}年\d{1,2}月|\d{4}年|年初|年末)")
# 环比/涨幅：动词长词优先（涨幅高达|增幅达 在 涨 之前），"约/高达/高"均为可选修饰
# 覆盖「环比增长12.19%」「增长约6.4%」「环比涨1.85%」「环比上涨4.32%」「涨幅高达49.8%」
_RE_CHANGE = re.compile(
    r"(?:环比|同比|较[^，。]{0,12})?(?:增长|上涨|上升|攀升|涨幅高达|增幅达|涨)约?(?:高达|高)?(\d{1,2}\.\d{1,2})%"
)


def _clean_category(raw_cat: str) -> str:
    """清洗品类名：剥离泄入的日期字/数字/标点，返回规范品类（可能为空）。

    例：「月伞具」→「伞具」；「月球」→「球」；「p据义乌」→「」。
    """
    if not raw_cat:
        return ""
    cat = raw_cat.strip()
    # 去首部日期单位/序数/标点与残留标签字符（不剥中文数字，避免"五金工具"→"金工具"）
    cat = re.sub(r"^[0-9]+", "", cat)
    cat = re.sub(r"^[月年日份号第]+", "", cat)
    cat = re.sub(r"^[，。、；：\s>\\/p]+", "", cat)
    # 去尾部可能误接的非品类字
    cat = cat.strip("，。、；： ")
    return cat


def _decode_nuxt_html(raw: str) -> str:
    """把 Nuxt SSR 页面里转义的 HTML 还原为纯中文正文。

    官网正文嵌在 ``<script>window.__NUXT__={...}</script>`` 的转义 JSON 中
    （标签写作 ``\\u003Cp\\u003E``，中文与数字为明文）。

    关键修正（上一版 bug）：**不能**先把 ``\\u003C`` 还原成真实 ``<`` 再删
    ``<script>`` 块——那样会把嵌在 script 里的正文一并删掉（实测 decoded 只剩
    1057 字符、解析 0 条）。正确做法：把转义的标签边界 ``\\u003C``/``\\u003E``
    直接替换为换行（充当句子/段落边界），全程不制造真实 ``<>``，从而保住正文；
    外层真实 HTML 标签最后再统一删除。
    """
    text = raw
    # 1) 转义标签边界 → 换行（不还原成真实 <>，避免误删 NUXT 正文）
    text = text.replace("\\u003C", "\n").replace("\\u003E", "\n")
    # 2) 其余常见转义还原
    text = (text.replace("\\u0026", "&").replace("\\u0022", '"')
                .replace("\\u0027", "'").replace("\\/", "/"))
    text = text.replace("\\n", "\n").replace("\\r", "").replace("\\t", " ")
    # 3) 删除外层真实 HTML 标签（此时 NUXT 数据已无真实 <>，安全）
    text = re.sub(r"<[^>]+>", "\n", text)
    # 4) 解 HTML 实体（&nbsp; 等）
    text = html_lib.unescape(text)
    # 5) 压缩空白
    text = re.sub(r"[ \u00a0]+", " ", text)
    return text


class YiwuIndexSource(RealDataSource):
    """义乌指数官方发布值源（/report 栏目文章正文解析）。"""

    name = "yiwu_index"
    display_name = "义乌指数（官方发布值）"
    source_url = REPORT_URL
    refresh_interval = 7 * 24 * 3600  # 官方发布值，每周刷新足够
    description = "义乌指数官网 /report 栏目官方公开发布的品类指数值（千点基准·定期更新），非实时面板"

    def fetch_raw(self) -> str:
        """抓取 /report 页面 HTML（服务器渲染，含官方发布指数正文）。"""
        resp = self._get(REPORT_URL)
        return resp.text

    def parse(self, raw: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """从文章正文解析 (品类, 指数值, 日期, 环比) 官方发布记录。"""
        if not isinstance(raw, str):
            raise TypeError("义乌指数源期望 HTML 字符串，收到非 str")
        text = _decode_nuxt_html(raw)
        records: List[Dict[str, Any]] = []
        seen = set()
        for sent in _SENT_SPLIT.split(text):
            if "指数" not in sent:
                continue
            values = _RE_VALUE.findall(sent)
            if not values:
                continue
            cat_m = _RE_CATEGORY.search(sent)
            category = _clean_category(cat_m.group(1)) if cat_m else ""
            # 品类为空或误把"义乌"当品类，但句子确含"义乌指数" → 归为综合指数
            if (not category or category in ("义乌", "义乌指数")) and _RE_COMPOSITE.search(sent):
                category = "义乌指数（综合）"
            date_m = _RE_DATE.search(sent)
            as_of = date_m.group(1) if date_m else ""
            change_m = _RE_CHANGE.search(sent)
            change_pct = float(change_m.group(1)) if change_m else None
            # 一句话可能含「自年初的1463.99点上涨至2026年6月的1557.03点」两值，
            # 取最后一个为当前发布值，首个为基期值
            current = float(values[-1])
            base = float(values[0]) if len(values) > 1 else None
            key = (category, current, as_of)
            if key in seen:
                continue
            seen.add(key)
            # excerpt 去首部残留标签噪声（p> / \n / > / / 等）
            excerpt = re.sub(r"^[>\s\\/a-zA-Z]+", "", sent.strip())[:120]
            records.append({
                "category": category,
                "index_value": current,
                "base_value": base,
                "as_of": as_of,
                "change_pct": change_pct,
                "index_scale": "官方千点基准",
                "excerpt": excerpt,
            })
        return {
            "provider": "义乌指数官网 ywindex.com/report",
            "index_type": "义乌中国小商品指数（官方发布值）",
            "index_scale": "官方千点基准（与 demo 旧 98~110 标度不同，不可混用）",
            "update_mode": "定期更新（官方发布，非实时面板）",
            "records": records,
            "record_count": len(records),
        }

    def validate(self, parsed: Dict[str, Any]) -> bool:
        """校验：至少解析出 1 条带品类与合理指数值（800~3000 千点区间）的记录。"""
        if not parsed or not isinstance(parsed, dict):
            return False
        records = parsed.get("records") or []
        if not records:
            return False
        valid = [
            r for r in records
            if r.get("category") and isinstance(r.get("index_value"), (int, float))
            and 800.0 <= float(r["index_value"]) <= 3000.0
        ]
        return len(valid) >= 1
