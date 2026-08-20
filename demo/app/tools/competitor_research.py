"""义乌小商品出海智能体 - 竞品实采工具（智能体自主性 / 工具调用）

本工具是金漪湖论剑 OPC 智能体赛道"工具调用与自主性"评分项的核心实现：
让智能体像人一样**自主打开真实电商网站**（Amazon / 1688 等），
完成 搜索 -> 滚动 -> 抽取商品标题/价格/评分/评论 的端到端操作，
为市场洞察、竞品分析提供真实一手数据，而非仅依赖内置样例数据。

实现策略：
1. 优先复用本地已有的 WebRetriever Agent（D:/Apps/competition/webretriever-agent）
   进行 VLM 驱动的浏览器自主操作；
2. 若不可用，则使用 Playwright 轻量自驱抓取；
3. 若浏览器环境不可用，则安全回退为带明确标识的模拟数据，保证服务可运行。
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from typing import Any, Dict, List, Optional

# WebRetriever Agent 可选依赖（用户本地已有，提供最强自主性能力）
try:  # pragma: no cover - 依赖可选
    from webretriever_agent import run_single_task  # type: ignore
    _HAS_WEBRETRIEVER = True
except Exception:  # noqa: BLE001
    _HAS_WEBRETRIEVER = False

# Playwright 可选依赖
try:  # pragma: no cover - 依赖可选
    from playwright.async_api import async_playwright  # type: ignore
    _HAS_PLAYWRIGHT = True
except Exception:  # noqa: BLE001
    _HAS_PLAYWRIGHT = False


SEARCH_URLS = {
    "amazon": "https://www.amazon.com/s?k={query}",
    "1688": "https://www.1688.com/cha?keywords={query}",
}


class CompetitorResearchTool:
    """竞品自主调研工具：在真实网站上自主搜索并抽取竞品情报。

    用法：
        tool = CompetitorResearchTool()
        result = await tool.research("义乌 饰品", platform="amazon", country="US")
    """

    def __init__(self, enabled: Optional[bool] = None, headless: bool = True):
        self.enabled = (
            enabled if enabled is not None
            else os.getenv("COMPETITOR_RESEARCH_ENABLED", "true").lower() != "false"
        )
        self.headless = headless
        self.mode = self._detect_mode()

    def _detect_mode(self) -> str:
        if not self.enabled:
            return "disabled"
        if _HAS_WEBRETRIEVER:
            return "webretriever"
        if _HAS_PLAYWRIGHT:
            return "playwright"
        return "mock"

    async def research(
        self,
        query: str,
        platform: str = "amazon",
        country: str = "US",
        max_items: int = 8,
    ) -> Dict[str, Any]:
        """对指定商品在真实平台执行自主竞品调研。

        返回结构：
        {
            "query": ...,
            "platform": ...,
            "country": ...,
            "mode": "webretriever" | "playwright" | "mock",
            "items": [ {title, price, rating, reviews, url} ... ],
            "summary": "基于真实页面抽取的竞品洞察（由 LLM 合成时再加工）",
            "real_data": true/false
        }
        """
        if self.mode == "disabled":
            return self._mock(query, platform, country, "工具已禁用（COMPETITOR_RESEARCH_ENABLED=false）")

        if self.mode == "webretriever":
            try:
                return await self._run_webretriever(query, platform, country, max_items)
            except Exception as e:  # noqa: BLE001
                return self._mock(query, platform, country, "WebRetriever 调用失败，回退模拟：{}".format(e))

        if self.mode == "playwright":
            try:
                return await self._run_playwright(query, platform, country, max_items)
            except Exception as e:  # noqa: BLE001
                return self._mock(query, platform, country, "浏览器不可用，回退模拟：{}".format(e))

        return self._mock(query, platform, country, "未检测到浏览器自动化依赖，使用模拟数据")

    # ------------------------------------------------------------------
    # 模式 1：复用本地 WebRetriever Agent（最强自主性）
    # ------------------------------------------------------------------
    async def _run_webretriever(self, query, platform, country, max_items) -> Dict[str, Any]:
        task = {
            "task_id": "competitor_research",
            "task_idx": 0,
            "website": SEARCH_URLS.get(platform, SEARCH_URLS["amazon"]).format(query=query),
            "task": (
                "在{}上搜索\"{}\"，自主浏览前{}个商品，"
                "提取每个商品的标题、价格、评分、评论数，并以 JSON 列表返回。"
            ).format(platform, query, max_items),
        }
        # WebRetriever 为同步阻塞型，放到线程执行避免阻塞事件循环
        loop = asyncio.get_event_loop()
        outcome = await loop.run_in_executor(None, run_single_task, task)
        items = self._normalize_webretriever(outcome)
        return {
            "query": query,
            "platform": platform,
            "country": country,
            "mode": "webretriever",
            "items": items[:max_items],
            "real_data": True,
            "note": "由本地 WebRetriever Agent 在真实网站自主操作抽取",
        }

    @staticmethod
    def _normalize_webretriever(outcome: Any) -> List[Dict[str, Any]]:
        # WebRetriever 返回结构不定，尽量从 answer/轨迹中解析商品
        try:
            text = ""
            if isinstance(outcome, dict):
                text = str(outcome.get("answer") or outcome.get("final_answer") or outcome)
            else:
                text = str(outcome)
            # 尝试解析 JSON 列表
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                return [
                    {
                        "title": str(d.get("title") or d.get("name") or ""),
                        "price": str(d.get("price") or ""),
                        "rating": str(d.get("rating") or ""),
                        "reviews": str(d.get("reviews") or d.get("review_count") or ""),
                        "url": str(d.get("url") or ""),
                    }
                    for d in data
                    if isinstance(d, dict)
                ]
        except Exception:  # noqa: BLE001
            pass
        return []

    # ------------------------------------------------------------------
    # 模式 2：Playwright 轻量自驱抓取
    # ------------------------------------------------------------------
    async def _run_playwright(self, query, platform, country, max_items) -> Dict[str, Any]:
        url = SEARCH_URLS.get(platform, SEARCH_URLS["amazon"]).format(query=query)
        items: List[Dict[str, Any]] = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            # 等待商品加载
            await page.wait_for_timeout(2500)
            # 滚动以触发懒加载
            for _ in range(3):
                await page.mouse.wheel(0, 1200)
                await page.wait_for_timeout(800)

            if platform.startswith("amazon"):
                cards = await page.query_selector_all("div[data-component-type='s-search-result']")
                for card in cards[:max_items]:
                    title = await self._safe_text(card, "h2 span")
                    price = await self._safe_text(card, ".a-price .a-offscreen")
                    rating = await self._safe_text(card, "i.a-icon-star-small span")
                    reviews = await self._safe_text(card, "span.a-size-base.s-underline-text")
                    href = await self._safe_attr(card, "h2 a", "href")
                    items.append({
                        "title": title,
                        "price": price,
                        "rating": rating,
                        "reviews": reviews,
                        "url": href or "",
                    })
            else:
                # 1688 等通用兜底：抽取标题文本
                texts = await page.eval_on_selector_all(
                    "a", "els => els.slice(0, {n}).map(e => e.innerText)".format(n=max_items * 3),
                )
                items = [{"title": t.strip(), "price": "", "rating": "", "reviews": "", "url": ""}
                         for t in texts if t and t.strip()][:max_items]
            await browser.close()

        return {
            "query": query,
            "platform": platform,
            "country": country,
            "mode": "playwright",
            "items": items,
            "real_data": True,
            "note": "由 Playwright 在真实网站自主搜索与抽取",
        }

    @staticmethod
    async def _safe_text(card, sel: str) -> str:
        try:
            el = await card.query_selector(sel)
            return (await el.inner_text()).strip() if el else ""
        except Exception:  # noqa: BLE001
            return ""

    @staticmethod
    async def _safe_attr(card, sel: str, attr: str) -> str:
        try:
            el = await card.query_selector(sel)
            return (await el.get_attribute(attr)) or "" if el else ""
        except Exception:  # noqa: BLE001
            return ""

    # ------------------------------------------------------------------
    # 回退：明确标识的模拟数据（保证服务始终可运行）
    # ------------------------------------------------------------------
    def _mock(self, query, platform, country, reason: str) -> Dict[str, Any]:
        return {
            "query": query,
            "platform": platform,
            "country": country,
            "mode": "mock",
            "real_data": False,
            "note": reason,
            "items": [
                {
                    "title": "[模拟] {} 竞品A（浏览器未启用，真实数据需启用 Playwright 或 WebRetriever）".format(query),
                    "price": "—",
                    "rating": "—",
                    "reviews": "—",
                    "url": "",
                },
                {
                    "title": "[模拟] {} 竞品B".format(query),
                    "price": "—",
                    "rating": "—",
                    "reviews": "—",
                    "url": "",
                },
            ],
        }
