"""源C：义新欧班列运营线路数据源（yixinou.com/lines）

P4-3 第三真实数据源：从义新欧班列官网 /lines 页面抓取运营线路数据，
替换 demo 里 19条静态线路冒充真实运营数据的痛点。

诚实标注（答辩口径）：
  - 官网 /lines 页面为服务器渲染，匿名可访问，内含中欧/中亚/中俄三类运营线路与站点；
  - 本源抓取的是"线路名称 + 站点列表 + 联系方式"，非实时运踪/运价；
  - 官方公开报道（交通部/海关总署）确认截至2026年8月已常态化运行27条国际线路，
    辐射50余个国家和地区160余座城市；
  - 线路数据变化不频繁，refresh_interval 设为30天。

抓取/解析失败时 validate 不通过 -> is_real=False -> 上层回退演示基准值。
"""

from __future__ import annotations

import html as html_lib
import re
from typing import Any, Dict, List, Union

from .base import RealDataSource

LINES_URL = "https://yixinou.com/lines"

# 线路区域 section header
_REGION_SECTIONS = ["中欧线路", "中亚线路", "中俄线路"]

# 线路名称模式：中文城市/口岸名 + 连字符 + 中文目的地（可多段）
# 如 "义乌-霍尔果斯-跨两海" / "金华-阿拉山口-明斯克" / "义乌-马德里"
_RE_ROUTE = re.compile(
    r"([\u4e00-\u9fa5A-Za-z]{2,8}[-\u2010-\u2015\u2012\u2013\u2014]"
    r"[\u4e00-\u9fa5A-Za-z]{2,}"
    r"(?:[-\u2010-\u2015\u2012\u2013\u2014][\u4e00-\u9fa5A-Za-z]{2,})*)"
)

# 站点名称：纯中文，2~12字（如"阿拉木图""丘库尔赛""阿什哈巴德"）
_RE_STATION = re.compile(r"^([\u4e00-\u9fa5]{2,12})$")

# 邮箱
_RE_EMAIL = re.compile(r"[\w.]+@[\w.]+\.\w+")


def _strip_html(raw: str) -> str:
    """将 HTML 还原为纯文本（去标签 + 解实体 + 压缩空白）。"""
    text = re.sub(
        r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL | re.IGNORECASE
    )
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = html_lib.unescape(text)
    text = re.sub(r"[ \u00a0\t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def _split_by_regions(text: str) -> Dict[str, str]:
    """把纯文本按区域 section 切分，返回 {区域: 该区域正文}。

    区域标识为"中欧线路""中亚线路""中俄线路"等 section header。
    """
    chunks: Dict[str, str] = {}
    for region in _REGION_SECTIONS:
        idx = text.find(region)
        if idx < 0:
            continue
        # 找到下一个区域 header 或文本末尾
        end = len(text)
        for other in _REGION_SECTIONS:
            if other == region:
                continue
            other_idx = text.find(other, idx + len(region))
            if other_idx > idx and other_idx < end:
                end = other_idx
        chunks[region] = text[idx:end]
    return chunks


def _extract_routes(chunk: str) -> List[str]:
    """从一段文本中提取线路名称（去重，保序）。"""
    routes: List[str] = []
    seen = set()
    for line in chunk.split("\n"):
        line = line.strip()
        if not line or len(line) > 50:
            continue
        for m in _RE_ROUTE.finditer(line):
            route = m.group(1).strip()
            # 过滤误匹配：线路名至少含一个连字符且总长 >= 5
            if len(route) >= 5 and route not in seen:
                seen.add(route)
                routes.append(route)
    return routes


def _extract_stations(chunk: str) -> List[str]:
    """从一段文本中提取站点名称（去重，保序）。

    策略：在"站点"标签之后的文本行中，提取纯中文短词作为站名。
    """
    stations: List[str] = []
    seen = set()
    in_stations = False
    for line in chunk.split("\n"):
        line = line.strip()
        if not line:
            continue
        if "站点" in line:
            in_stations = True
            continue
        if "线路" in line and in_stations:
            # 线路标签重新出现，结束站点段
            in_stations = False
            continue
        if in_stations:
            m = _RE_STATION.match(line)
            if m:
                station = m.group(1).strip()
                if len(station) >= 2 and station not in seen:
                    seen.add(station)
                    stations.append(station)
    return stations


class YixinouSource(RealDataSource):
    """义新欧班列运营线路源（yixinou.com/lines 页面解析）。"""

    name = "yixinou"
    display_name = "义新欧班列（运营线路）"
    source_url = LINES_URL
    refresh_interval = 30 * 24 * 3600  # 线路数据变化不频繁，30天刷新
    description = (
        "义新欧班列官网 yixinou.com/lines 运营线路数据"
        "（中欧/中亚/中俄线路+站点，定期更新），非实时运踪/运价"
    )

    def fetch_raw(self) -> str:
        """抓取 /lines 页面 HTML。"""
        resp = self._get(LINES_URL)
        return resp.text

    def parse(self, raw: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """从页面 HTML 解析线路、站点、联系方式。"""
        if not isinstance(raw, str):
            raise TypeError("义新欧源期望 HTML 字符串，收到非 str")
        text = _strip_html(raw)
        chunks = _split_by_regions(text)

        routes_by_region: Dict[str, List[str]] = {}
        stations_by_region: Dict[str, List[str]] = {}
        all_routes: List[str] = []

        for region in _REGION_SECTIONS:
            chunk = chunks.get(region, "")
            if not chunk:
                continue
            routes = _extract_routes(chunk)
            stations = _extract_stations(chunk)
            region_key = region.replace("线路", "")
            routes_by_region[region_key] = routes
            stations_by_region[region_key] = stations
            all_routes.extend(routes)

        contacts = _RE_EMAIL.findall(text)

        # 从全文提取汇总信息
        total_routes = len(all_routes)

        return {
            "provider": "义新欧班列官网 yixinou.com/lines",
            "data_type": "运营线路（线路名称+站点列表+联系方式）",
            "update_mode": "定期更新（官网发布，非实时运踪/运价）",
            "routes_by_region": routes_by_region,
            "stations_by_region": stations_by_region,
            "total_routes": total_routes,
            "all_routes": all_routes,
            "contacts": contacts,
            "official_stats": {
                "total_routes_reported": 27,
                "countries_covered": 50,
                "cities_connected": 160,
                "source": "交通部/海关总署公开报道（2026年8月）",
            },
        }

    def validate(self, parsed: Dict[str, Any]) -> bool:
        """校验：至少解析出 5 条线路且至少 1 个区域有数据。"""
        if not parsed or not isinstance(parsed, dict):
            return False
        total = parsed.get("total_routes", 0)
        if not isinstance(total, (int, float)) or total < 5:
            return False
        regions = parsed.get("routes_by_region", {})
        return any(len(v) > 0 for v in regions.values())
