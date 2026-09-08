"""义乌小商品出海智能体 - 真实数据源 ETL 基类

P1-1 真数据源样板的核心抽象：
    fetch_raw()  抓取原始响应（HTTP/文件）
    parse()      解析为结构化 dict
    validate()   校验数据可用性（防止把空/坏数据当成真实数据落库）
    fetch()      编排上述三步，统一产出带时间戳、来源、真伪标记的 FetchResult

设计原则（对应《升级改造方案》P1-1 与"诚实优先/可自证"总纲）：
  1. 每个真实源都必须携带 source_url + fetched_at，评委可现场复核请求-响应；
  2. 抓取/解析失败绝不抛异常打断主流程，而是返回 is_real=False 的 FetchResult，
     由上层（registry/store）决定回退到"上次成功值"或"演示基准值"；
  3. is_real 三态语义贯穿到前端徽章，杜绝"HTTP 200 就显示 AI 已接入"的说谎问题。
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

import httpx

# ETL 统一超时（秒）：连接 5s、读取 15s，避免慢源拖垮启动预热
DEFAULT_TIMEOUT = httpx.Timeout(15.0, connect=5.0)
# 模拟浏览器 UA，降低被简单反爬拦截的概率
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


@dataclass
class FetchResult:
    """一次 ETL 抓取的标准化产物。

    is_real=True  表示数据来自真实外部源且通过校验；
    is_real=False 表示抓取/解析/校验失败，data 为空或降级值，error 说明原因。
    """

    source: str                      # 源标识，如 "exchange_rate" / "yiwu_index"
    is_real: bool                    # 是否真实抓取并校验通过
    data: Dict[str, Any] = field(default_factory=dict)   # 解析后的结构化数据
    fetched_at: float = 0.0          # 抓取完成时间戳（time.time()）
    source_url: str = ""             # 数据来源 URL（可自证）
    freshness_seconds: int = 0       # 该源建议刷新间隔（秒）
    error: str = ""                  # 失败原因（is_real=False 时填写）
    raw_excerpt: str = ""            # 原始响应摘录（≤500字符，答辩自证用）

    def age_seconds(self, now: Optional[float] = None) -> float:
        """数据年龄（秒）。fetched_at 为 0 时返回 inf（视为永不可用）。"""
        if not self.fetched_at:
            return float("inf")
        return (now if now is not None else time.time()) - self.fetched_at

    def is_fresh(self, now: Optional[float] = None) -> bool:
        """是否在建议刷新间隔内（新鲜）。"""
        if self.freshness_seconds <= 0:
            return False
        return self.age_seconds(now) <= self.freshness_seconds

    def to_dict(self) -> Dict[str, Any]:
        """序列化为可 JSON 化的 dict（供 API 对外暴露 / 落库）。"""
        return {
            "source": self.source,
            "is_real": self.is_real,
            "data": self.data,
            "fetched_at": self.fetched_at,
            "fetched_at_iso": (
                time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(self.fetched_at))
                if self.fetched_at else ""
            ),
            "source_url": self.source_url,
            "freshness_seconds": self.freshness_seconds,
            "age_seconds": round(self.age_seconds(), 1) if self.fetched_at else None,
            "is_fresh": self.is_fresh(),
            "error": self.error,
        }


class RealDataSource(ABC):
    """真实数据源抽象基类。子类实现 fetch_raw / parse，可选覆写 validate。"""

    #: 源唯一标识（英文，用于 registry/store 键）
    name: str = "base"
    #: 对外展示名（中文）
    display_name: str = "基础数据源"
    #: 数据来源 URL（可自证）
    source_url: str = ""
    #: 建议刷新间隔（秒）
    refresh_interval: int = 3600
    #: 一句话描述（含更新频率，诚实标注"实时/定期"）
    description: str = ""

    def __init__(self, timeout: httpx.Timeout = DEFAULT_TIMEOUT,
                 headers: Optional[Dict[str, str]] = None):
        self.timeout = timeout
        self.headers = headers or DEFAULT_HEADERS

    # ---------- 子类必须实现 ----------

    @abstractmethod
    def fetch_raw(self) -> Union[str, Dict[str, Any]]:
        """抓取原始数据（HTTP 响应文本或已解析的 JSON dict）。失败应抛异常。"""

    @abstractmethod
    def parse(self, raw: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """把原始数据解析为结构化 dict。失败应抛异常。"""

    # ---------- 可选覆写 ----------

    def validate(self, parsed: Dict[str, Any]) -> bool:
        """校验解析结果是否可用。默认要求非空 dict。子类可加字段/范围校验。"""
        return bool(parsed) and isinstance(parsed, dict)

    # ---------- 统一编排 ----------

    def fetch(self) -> FetchResult:
        """完整 ETL 流程：fetch_raw → parse → validate。

        任何环节异常都被捕获并转为 is_real=False 的 FetchResult，绝不向上抛，
        保证主流程（启动预热 / 接口响应）不被单个慢源或坏源拖垮。
        """
        started = time.time()
        try:
            raw = self.fetch_raw()
            excerpt = self._make_excerpt(raw)
            parsed = self.parse(raw)
            if not self.validate(parsed):
                return FetchResult(
                    source=self.name, is_real=False, data={},
                    fetched_at=time.time(), source_url=self.source_url,
                    freshness_seconds=self.refresh_interval,
                    error="校验未通过：解析结果为空或不符合预期结构",
                    raw_excerpt=excerpt,
                )
            return FetchResult(
                source=self.name, is_real=True, data=parsed,
                fetched_at=time.time(), source_url=self.source_url,
                freshness_seconds=self.refresh_interval,
                raw_excerpt=excerpt,
            )
        except Exception as e:  # noqa: BLE001 - ETL 必须吞掉一切异常做降级
            return FetchResult(
                source=self.name, is_real=False, data={},
                fetched_at=started, source_url=self.source_url,
                freshness_seconds=self.refresh_interval,
                error=f"{type(e).__name__}: {e}",
            )

    # ---------- 工具 ----------

    def _get(self, url: str, **kwargs) -> httpx.Response:
        """带统一超时/UA 的 GET，response.raise_for_status()。"""
        with httpx.Client(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
            resp = client.get(url, **kwargs)
            resp.raise_for_status()
            return resp

    @staticmethod
    def _make_excerpt(raw: Union[str, Dict[str, Any]], limit: int = 500) -> str:
        """生成原始响应摘录（答辩自证：证明数据确实来自外部请求）。"""
        try:
            text = raw if isinstance(raw, str) else str(raw)
        except Exception:  # noqa: BLE001
            return ""
        text = text.strip()
        return text[:limit] + ("…" if len(text) > limit else "")
