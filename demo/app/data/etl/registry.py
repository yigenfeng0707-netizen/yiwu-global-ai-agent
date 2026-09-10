"""真实数据源注册表（P1-1）

职责：
  1. 统一管理真实源（exchange_rate / yiwu_index）的刷新与持久缓存；
  2. 提供"三态回退"：本次抓取成功 → 用新值；失败 → 回退上次成功值（内存→DB）；
     从未成功 → is_real=False，由调用方决定用演示基准值并明确标注；
  3. 对外产出数据源状态清单（real / demo / planned），供 /data-sources 与前端徽章
     如实显示，杜绝"HTTP 200 就显示 AI 已接入/实时数据"的说谎问题；
  4. 启动预热（best-effort，后台线程，不阻塞应用启动）。

诚实口径：legacy 的 5 个 demo 源（义乌小商品城/义新欧/Amazon/Alibaba/行业报告）
在此显式声明为 demo 或 planned，与新增的 2 个 real 源并列展示，让评委一眼看清
"哪些是真的、哪些是演示、哪些在规划"。
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Dict, List, Optional

from .base import FetchResult, RealDataSource
from .exchange_rate import ExchangeRateSource
from .yiwu_index import YiwuIndexSource
from .yixinou import YixinouSource

logger = logging.getLogger(__name__)


class DataSourceStatus:
    """数据源三态。"""

    REAL = "real"  # 真实接入的外部数据管道（带时间戳，可现场自证）
    DEMO = "demo"  # 演示数据（静态内置，明确标注）
    PLANNED = "planned"  # 规划中（尚未接入，对外不冒充真实）


# 默认注册的真实源
DEFAULT_REAL_SOURCES: List[RealDataSource] = [
    ExchangeRateSource(),
    YiwuIndexSource(),
    YixinouSource(),
]

# legacy demo 源的三态声明（与 sources.py 的 5 个源对应，诚实标注）
LEGACY_SOURCE_STATUS: List[Dict[str, str]] = [
    {
        "name": "义乌小商品城",
        "status": DataSourceStatus.DEMO,
        "note": "内置品类/商户静态演示数据，非实时抓取",
    },
    {
        "name": "义新欧班列",
        "status": DataSourceStatus.DEMO,
        "note": "运营线路已由真实源 yixinou 提供（yixinou.com/lines）；时效/运费仍为静态演示数据",
    },
    {
        "name": "Amazon",
        "status": DataSourceStatus.PLANNED,
        "note": "平台销售数据接入规划中，当前为演示占位",
    },
    {
        "name": "Alibaba.com",
        "status": DataSourceStatus.PLANNED,
        "note": "国际站 B2B 数据接入规划中，当前为演示占位",
    },
    {
        "name": "行业报告",
        "status": DataSourceStatus.DEMO,
        "note": "内置行业规模/增速静态演示数据；义乌指数已改由真实源 yiwu_index 提供",
    },
]

# legacy demo 源的三态声明（与 sources.py 的 5 个源对应，诚实标注）
LEGACY_SOURCE_STATUS: List[Dict[str, str]] = [
    {
        "name": "义乌小商品城",
        "status": DataSourceStatus.DEMO,
        "note": "内置品类/商户静态演示数据，非实时抓取",
    },
    {
        "name": "义新欧班列",
        "status": DataSourceStatus.DEMO,
        "note": "内置线路/时效/运费静态演示数据",
    },
    {
        "name": "Amazon",
        "status": DataSourceStatus.PLANNED,
        "note": "平台销售数据接入规划中，当前为演示占位",
    },
    {
        "name": "Alibaba.com",
        "status": DataSourceStatus.PLANNED,
        "note": "国际站 B2B 数据接入规划中，当前为演示占位",
    },
    {
        "name": "行业报告",
        "status": DataSourceStatus.DEMO,
        "note": "内置行业规模/增速静态演示数据；义乌指数已改由真实源 yiwu_index 提供",
    },
]


class RealDataRegistry:
    """真实数据源注册表。"""

    def __init__(
        self, sources: Optional[List[RealDataSource]] = None, db: Optional[Any] = None
    ):
        self._sources: Dict[str, RealDataSource] = {}
        self._last_good: Dict[str, FetchResult] = {}  # 内存最近成功值
        self._db = db  # 持久层（可注入，便于测试）
        self._lock = threading.Lock()
        for s in sources if sources is not None else DEFAULT_REAL_SOURCES:
            self.register(s)

    # ---------- 注册 / 取源 ----------

    def register(self, source: RealDataSource):
        self._sources[source.name] = source

    def get_source(self, name: str) -> Optional[RealDataSource]:
        return self._sources.get(name)

    @property
    def source_names(self) -> List[str]:
        return list(self._sources.keys())

    # ---------- 持久层（懒获取，避免循环依赖） ----------

    def _get_db(self):
        if self._db is not None:
            return self._db
        try:
            from ...db.database import get_db

            self._db = get_db()
        except Exception as e:  # noqa: BLE001
            logger.warning("真实数据源持久层不可用，仅用内存缓存: %s", e)
            self._db = False  # 标记不可用，避免反复尝试
        return self._db or None

    # ---------- 刷新 ----------

    def refresh(
        self, name: Optional[str] = None, force: bool = False
    ) -> Dict[str, FetchResult]:
        """刷新指定源（name=None 则全部）。

        成功：更新内存最近成功值 + 落库；
        失败：保留上次成功值（不清空），返回的 FetchResult.is_real=False 并带 error。
        force=False 时，若内存值仍新鲜则跳过抓取（省外部请求）。
        """
        targets = (
            [self._sources[name]]
            if name and name in self._sources
            else list(self._sources.values())
        )
        results: Dict[str, FetchResult] = {}
        for src in targets:
            if not force:
                cached = self._last_good.get(src.name)
                if cached and cached.is_fresh():
                    results[src.name] = cached
                    continue
            result = src.fetch()
            with self._lock:
                if result.is_real:
                    self._last_good[src.name] = result
                    self._persist(result)
                else:
                    logger.warning("真实数据源 %s 抓取失败：%s", src.name, result.error)
            results[src.name] = result
        return results

    def _persist(self, result: FetchResult):
        db = self._get_db()
        if not db:
            return
        try:
            db.save_real_data(result.to_dict())
        except Exception as e:  # noqa: BLE001
            logger.warning("真实数据源 %s 落库失败：%s", result.source, e)

    # ---------- 取值（三态回退） ----------

    def get(self, name: str) -> Optional[FetchResult]:
        """取最近成功值：内存 → DB。从未成功返回 None。"""
        with self._lock:
            cached = self._last_good.get(name)
        if cached:
            return cached
        db = self._get_db()
        if db:
            try:
                record = db.get_real_data(name)
                if record and record.get("payload"):
                    payload = record["payload"]
                    result = FetchResult(
                        source=name,
                        is_real=bool(payload.get("is_real")),
                        data=payload.get("data", {}) or {},
                        fetched_at=payload.get("fetched_at", 0) or 0,
                        source_url=payload.get("source_url", ""),
                        freshness_seconds=payload.get("freshness_seconds", 0) or 0,
                        error=payload.get("error", ""),
                    )
                    if result.is_real:
                        with self._lock:
                            self._last_good[name] = result
                        return result
            except Exception as e:  # noqa: BLE001
                logger.warning("读取真实数据源 %s 缓存失败：%s", name, e)
        return None

    def get_data(
        self, name: str, default: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """取真实数据 data 字段；无成功值则返回 default（或空 dict）。"""
        result = self.get(name)
        if result and result.is_real and result.data:
            return result.data
        return default if default is not None else {}

    def get_meta(self, name: str) -> Dict[str, Any]:
        """取真实数据的溯源元信息（fetched_at/source_url/is_real/age），供前端徽章与答辩自证。"""
        result = self.get(name)
        if not result:
            return {
                "is_real": False,
                "source": name,
                "fetched_at": 0,
                "source_url": "",
                "age_seconds": None,
                "note": "尚无成功抓取记录",
            }
        d = result.to_dict()
        return {
            "is_real": d["is_real"],
            "source": name,
            "fetched_at": d["fetched_at"],
            "fetched_at_iso": d["fetched_at_iso"],
            "source_url": d["source_url"],
            "age_seconds": d["age_seconds"],
            "is_fresh": d["is_fresh"],
            "error": d["error"],
        }

    def get_index_for_category(self, category: str) -> Dict[str, Any]:
        """取某品类的义乌指数官方发布值（千点基准），带完整溯源 meta。

        匹配优先级：品类精确匹配 → 综合指数 → 最新一条。
        无真实成功值时 is_real=False、index_value=None，由调用方决定演示回退。
        """
        data = self.get_data("yiwu_index")
        meta = self.get_meta("yiwu_index")
        records = (data or {}).get("records", []) or []
        base = {
            "is_real": False,
            "index_value": None,
            "scale": "",
            "as_of": "",
            "category_matched": "",
            "change_pct": None,
            "source_url": meta.get("source_url", ""),
            "fetched_at_iso": meta.get("fetched_at_iso", ""),
            "excerpt": "",
            "note": "",
        }
        if not meta.get("is_real") or not records:
            base["note"] = "义乌指数真实源暂无成功抓取记录（回退演示基准值）"
            return base
        match = None
        for r in records:  # ① 品类精确匹配
            if r.get("category") == category:
                match = r
                break
        if match is None:  # ② 综合指数
            for r in records:
                if r.get("category") == "义乌指数（综合）":
                    match = r
                    break
        if match is None:  # ③ 最新一条
            match = records[0]
        base.update(
            {
                "is_real": True,
                "index_value": float(match.get("index_value")),
                "scale": match.get("index_scale", "官方千点基准"),
                "as_of": match.get("as_of", ""),
                "category_matched": match.get("category", ""),
                "change_pct": match.get("change_pct"),
                "excerpt": match.get("excerpt", ""),
                "note": "义乌指数官网官方发布值（定期更新，非实时面板）",
            }
        )
        return base

    def get_exchange_rate(self, currency: str = "CNY") -> Dict[str, Any]:
        """取某货币对 USD 的每日参考汇率，带溯源 meta。无真实值时 is_real=False。"""
        data = self.get_data("exchange_rate")
        meta = self.get_meta("exchange_rate")
        if not meta.get("is_real") or not data:
            return {
                "is_real": False,
                "currency": currency,
                "rate": None,
                "as_of": "",
                "source_url": meta.get("source_url", ""),
                "note": "汇率真实源暂无成功抓取记录",
            }
        focus = data.get("focus_rates", {}) or {}
        rate = focus.get(currency, (data.get("all_rates", {}) or {}).get(currency))
        return {
            "is_real": rate is not None,
            "currency": currency,
            "base": data.get("base", "USD"),
            "rate": rate,
            "as_of": data.get("as_of", ""),
            "focus_rates": focus,
            "source_url": meta.get("source_url", ""),
            "fetched_at_iso": meta.get("fetched_at_iso", ""),
            "provider": data.get("provider", ""),
            "note": "open.er-api.com 每日参考汇率（非银行实时牌价）",
        }

    def get_yixinou_routes(self, region: str = "") -> Dict[str, Any]:
        """取义新欧班列运营线路数据，带溯源 meta。

        region 可选过滤：传入"欧洲"/"中亚"/"俄罗斯"等关键词时，
        返回对应区域线路；不传或无匹配时返回全部线路。
        无真实成功值时 is_real=False，由调用方决定演示回退。
        """
        data = self.get_data("yixinou")
        meta = self.get_meta("yixinou")
        base = {
            "is_real": False,
            "source": "义新欧班列",
            "total_routes": 0,
            "routes_by_region": {},
            "routes": [],
            "source_url": meta.get("source_url", ""),
            "fetched_at_iso": meta.get("fetched_at_iso", ""),
            "note": "义新欧真实源暂无成功抓取记录（回退演示基准值）",
        }
        if not meta.get("is_real") or not data:
            return base
        routes_by_region = data.get("routes_by_region", {}) or {}
        all_routes = data.get("all_routes", []) or []
        official = data.get("official_stats", {}) or {}
        # 区域关键词映射
        region_map = {
            "欧洲": "中欧",
            "中欧": "中欧",
            "中亚": "中亚",
            "俄罗斯": "中俄",
            "中俄": "中俄",
            "俄": "中俄",
        }
        target_region = region_map.get(region, "") if region else ""
        if target_region and target_region in routes_by_region:
            filtered = routes_by_region[target_region]
        elif region:
            # 模糊匹配：region 关键词在线路名中出现
            filtered = [r for r in all_routes if region in r]
        else:
            filtered = all_routes
        base.update(
            {
                "is_real": True,
                "total_routes": len(all_routes),
                "routes_by_region": routes_by_region,
                "routes": filtered,
                "total_routes_reported": official.get("total_routes_reported", 0),
                "countries_covered": official.get("countries_covered", 0),
                "cities_connected": official.get("cities_connected", 0),
                "contacts": data.get("contacts", []),
                "provider": data.get("provider", ""),
                "note": "义新欧班列官网 yixinou.com/lines 运营线路（定期更新，非实时运踪/运价）",
            }
        )
        return base

    # ---------- 状态汇总 ----------

    def status(self) -> List[Dict[str, Any]]:
        """全部数据源三态状态清单（real 源带新鲜度，legacy 源带声明）。"""
        out: List[Dict[str, Any]] = []
        for name, src in self._sources.items():
            meta = self.get_meta(name)
            out.append(
                {
                    "name": src.display_name,
                    "key": name,
                    "status": DataSourceStatus.REAL
                    if meta.get("is_real")
                    else DataSourceStatus.PLANNED,
                    "description": src.description,
                    "source_url": src.source_url,
                    "refresh_interval": src.refresh_interval,
                    "is_real": bool(meta.get("is_real")),
                    "fetched_at": meta.get("fetched_at"),
                    "fetched_at_iso": meta.get("fetched_at_iso"),
                    "age_seconds": meta.get("age_seconds"),
                    "is_fresh": meta.get("is_fresh"),
                    "error": meta.get("error", ""),
                }
            )
        for legacy in LEGACY_SOURCE_STATUS:
            out.append(
                {
                    "name": legacy["name"],
                    "key": legacy["name"],
                    "status": legacy["status"],
                    "description": legacy["note"],
                    "source_url": "",
                    "refresh_interval": 0,
                    "is_real": False,
                    "fetched_at": 0,
                    "fetched_at_iso": "",
                    "age_seconds": None,
                    "is_fresh": False,
                    "error": "",
                }
            )
        return out

    def real_count(self) -> int:
        """当前真实接入（有成功值）的源数量。"""
        return sum(
            1
            for name in self._sources
            if (self.get(name) or FetchResult(source=name, is_real=False)).is_real
        )

    # ---------- 启动预热 ----------

    def warm(self, block: bool = False):
        """启动预热：刷新全部真实源。

        默认后台线程执行（block=False），避免慢源拖垮应用启动；
        抓取失败不影响启动（get 会回退 DB 上次成功值或 None）。
        """
        if block:
            self.refresh(force=True)
            return
        t = threading.Thread(target=self._warm_worker, name="etl-warm", daemon=True)
        t.start()

    def _warm_worker(self):
        try:
            self.refresh(force=True)
            logger.info(
                "[ETL预热] 真实数据源刷新完成：real=%d/%d",
                self.real_count(),
                len(self._sources),
            )
        except Exception as e:  # noqa: BLE001
            logger.warning("[ETL预热] 失败（不影响启动）：%s", e)


# ---------- 全局单例 ----------

_registry: Optional[RealDataRegistry] = None
_registry_lock = threading.Lock()


def get_registry() -> RealDataRegistry:
    """获取全局真实数据源注册表（懒加载单例）。"""
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = RealDataRegistry()
    return _registry
