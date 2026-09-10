"""P1-1 真实数据源 ETL 测试

覆盖：
  - FetchResult 时间戳/新鲜度/序列化
  - ExchangeRateSource 解析与校验（mock payload，不依赖 live 网络）
  - YiwuIndexSource NUXT 解码 + 官方发布值解析 + 品类清洗（fixture HTML）
  - YixinouSource HTML 解析 + 线路/站点提取 + 校验（fixture HTML）
  - RealDataRegistry 三态回退、按品类取指数、义新欧线路查询、持久化落库/读回
"""

import time

import pytest

from app.data.etl.base import FetchResult, RealDataSource
from app.data.etl.exchange_rate import ExchangeRateSource
from app.data.etl.yiwu_index import YiwuIndexSource, _decode_nuxt_html, _clean_category
from app.data.etl.yixinou import (
    YixinouSource,
    _strip_html,
    _split_by_regions,
    _extract_routes,
    _extract_stations,
)
from app.data.etl.registry import RealDataRegistry, DataSourceStatus


# ==================== FetchResult ====================


class TestFetchResult:
    def test_age_and_freshness(self):
        now = time.time()
        r = FetchResult(
            source="x",
            is_real=True,
            data={"a": 1},
            fetched_at=now - 100,
            source_url="http://x",
            freshness_seconds=3600,
        )
        assert 99 <= r.age_seconds(now) <= 101
        assert r.is_fresh(now) is True
        stale = FetchResult(
            source="x", is_real=True, fetched_at=now - 7200, freshness_seconds=3600
        )
        assert stale.is_fresh(now) is False

    def test_zero_fetched_at_never_fresh(self):
        r = FetchResult(source="x", is_real=False, fetched_at=0, freshness_seconds=3600)
        assert r.age_seconds() == float("inf")
        assert r.is_fresh() is False

    def test_to_dict_serializable(self):
        r = FetchResult(
            source="x",
            is_real=True,
            data={"a": 1},
            fetched_at=time.time(),
            source_url="http://x",
            freshness_seconds=60,
        )
        d = r.to_dict()
        assert d["source"] == "x" and d["is_real"] is True
        assert "fetched_at_iso" in d and "age_seconds" in d


# ==================== 源A 汇率 ====================


class TestExchangeRateSource:
    def _payload(self, cny=6.72):
        return {
            "result": "success",
            "base_code": "USD",
            "time_last_update_utc": "Tue, 08 Sep 2026 00:02:31 +0000",
            "time_last_update_unix": 1788854551,
            "time_next_update_utc": "Wed, 09 Sep 2026 00:00:00 +0000",
            "rates": {"CNY": cny, "EUR": 0.86, "GBP": 0.74, "JPY": 154.4, "USD": 1},
        }

    def test_parse(self):
        src = ExchangeRateSource()
        parsed = src.parse(self._payload())
        assert parsed["base"] == "USD"
        assert parsed["cny_rate"] == 6.72
        assert parsed["focus_rates"]["EUR"] == 0.86
        assert parsed["as_of"].startswith("Tue, 08 Sep 2026")

    def test_validate_ok(self):
        src = ExchangeRateSource()
        assert src.validate(src.parse(self._payload())) is True

    def test_validate_rejects_out_of_range_cny(self):
        src = ExchangeRateSource()
        # CNY=99 超出合理区间 5~9，应判为坏数据
        assert src.validate(src.parse(self._payload(cny=99.0))) is False

    def test_validate_rejects_missing_cny(self):
        src = ExchangeRateSource()
        bad = self._payload()
        del bad["rates"]["CNY"]
        assert src.validate(src.parse(bad)) is False

    def test_fetch_raw_non_success_raises(self, monkeypatch):
        src = ExchangeRateSource()
        monkeypatch.setattr(
            src,
            "_get",
            lambda url, **k: type(
                "R",
                (),
                {"json": lambda self: {"result": "error", "error-type": "unsupported"}},
            )(),
        )
        with pytest.raises(ValueError):
            src.fetch_raw()

    def test_fetch_captures_error_as_not_real(self, monkeypatch):
        src = ExchangeRateSource()

        def boom(url, **k):
            raise RuntimeError("network down")

        monkeypatch.setattr(src, "_get", boom)
        result = src.fetch()
        assert result.is_real is False
        assert "network down" in result.error


# ==================== 源B 义乌指数 ====================

# 模拟官网 Nuxt SSR 转义 HTML（标签写作 \u003C，中文/数字为明文）
FIXTURE_HTML = (
    'window.__NUXT__={"a":1};'
    "\\u003Cp\\u003E义乌指数数据显示，过去一年伞具行业指数整体呈现上行态势。"
    "其中，2026年7月伞具类指数为1576.52点，较2025年8月增长约6.4%。\\u003C/p\\u003E"
    "\\u003Cp\\u003E据义乌指数数据监测，五金工具类指数自年初的1463.99点上涨至2026年6月的1557.03点。\\u003C/p\\u003E"
    "\\u003Cp\\u003E整体来看，体育娱乐用品类指数2025年11月达到峰值1767.76点，环比增长12.19%。\\u003C/p\\u003E"
    "\\u003Cp\\u003E2026年4月：义乌指数攀升至1550.67点，环比涨1.85%，创历史新高。\\u003C/p\\u003E"
)


class TestYiwuIndexDecode:
    def test_decode_preserves_chinese_prose(self):
        text = _decode_nuxt_html(FIXTURE_HTML)
        # 关键修正回归：正文必须保留（上一版 bug 会把 script 内正文删光）
        assert "伞具类指数为1576.52点" in text
        assert "义乌指数攀升至1550.67点" in text
        # 转义标签应被清除
        assert "\\u003C" not in text

    def test_clean_category_strips_date_unit(self):
        assert _clean_category("月伞具") == "伞具"
        assert _clean_category("月球") == "球"

    def test_clean_category_keeps_wujin(self):
        # 回归：不能把"五金工具"的"五"当中文数字剥掉
        assert _clean_category("五金工具") == "五金工具"

    def test_clean_category_strips_tag_noise(self):
        assert (
            _clean_category("p据义乌") == "据义乌" or _clean_category("p据义乌") == ""
        )


class TestYiwuIndexParse:
    def test_parse_records(self):
        src = YiwuIndexSource()
        parsed = src.parse(FIXTURE_HTML)
        assert parsed["record_count"] >= 3
        cats = {r["category"] for r in parsed["records"]}
        assert "伞具" in cats
        assert "五金工具" in cats
        assert "体育娱乐用品" in cats
        # 综合指数句应被归类
        assert "义乌指数（综合）" in cats

    def test_parse_values_and_dates(self):
        src = YiwuIndexSource()
        parsed = src.parse(FIXTURE_HTML)
        by_cat = {r["category"]: r for r in parsed["records"]}
        assert by_cat["伞具"]["index_value"] == 1576.52
        assert by_cat["伞具"]["as_of"] == "2026年7月"
        assert by_cat["伞具"]["change_pct"] == 6.4
        # 五金工具句含两值（年初1463.99→2026年6月1557.03），末值为当前、首值为基期
        assert by_cat["五金工具"]["index_value"] == 1557.03
        assert by_cat["五金工具"]["base_value"] == 1463.99

    def test_validate_ok(self):
        src = YiwuIndexSource()
        assert src.validate(src.parse(FIXTURE_HTML)) is True

    def test_validate_rejects_empty(self):
        src = YiwuIndexSource()
        assert src.validate(src.parse("没有指数的纯文本")) is False

    def test_parse_non_str_raises(self):
        src = YiwuIndexSource()
        with pytest.raises(TypeError):
            src.parse({"not": "str"})


# ==================== 源C 义新欧班列 ====================

# 模拟官网 /lines 页面 HTML（服务器渲染，含中欧/中亚/中俄三类线路+站点+联系方式）
YIXINOU_FIXTURE_HTML = """
<!DOCTYPE html>
<html><head><title>运营线路 - 义新欧班列</title></head><body>
<div class="header"><h1>运营线路</h1></div>
<div class="content">
<h2>中欧线路</h2>
<div class="section">
<p>线路</p>
<ul>
<li>义乌-霍尔果斯-跨两海</li>
<li>义乌-霍尔果斯-格鲁吉亚</li>
<li>义乌-阿拉山口-马德里</li>
<li>金华-阿拉山口-杜伊斯堡</li>
<li>义乌-霍尔果斯-布拉格</li>
<li>义乌-阿拉山口-伦敦</li>
<li>义乌-霍尔果斯-巴黎</li>
</ul>
<p>站点</p>
<ul>
<li>马德里</li>
<li>杜伊斯堡</li>
<li>布拉格</li>
<li>伦敦</li>
<li>巴黎</li>
<li>汉堡</li>
<li>米兰</li>
</ul>
<p>联系方式：yeqiuran@yixinou.com</p>
</div>
<h2>中亚线路</h2>
<div class="section">
<p>线路</p>
<ul>
<li>义乌-霍尔果斯-阿拉木图</li>
<li>义乌-阿拉山口-塔什干</li>
<li>金华-霍尔果斯-阿拉木图</li>
<li>金华-阿拉山口-塔什干</li>
<li>义乌-霍尔果斯-杜尚别</li>
<li>义乌-阿拉山口-阿什哈巴德</li>
</ul>
<p>站点</p>
<ul>
<li>阿拉木图</li>
<li>丘库尔赛</li>
<li>阿拉梅金</li>
<li>塔什干</li>
<li>谢尔盖利</li>
<li>杜尚别</li>
<li>苦盏</li>
<li>阿什哈巴德</li>
<li>梅杰乌</li>
<li>浩罕</li>
<li>瑟尔达里因</li>
</ul>
</div>
<h2>中俄线路</h2>
<div class="section">
<p>线路</p>
<ul>
<li>义乌-满洲里-明斯克</li>
<li>金华-满洲里-明斯克</li>
<li>义乌-霍尔果斯-俄罗斯</li>
<li>义乌-阿拉山口-明斯克</li>
<li>义乌-霍尔果斯-莫斯科</li>
<li>义乌-满洲里-莫斯科</li>
</ul>
<p>站点</p>
<ul>
<li>莫斯科</li>
<li>明斯克</li>
<li>圣彼得堡</li>
<li>沃罗西洛夫</li>
<li>沃尔西诺</li>
<li>别雷拉斯特</li>
</ul>
</div>
</div>
</body></html>
"""


class TestYixinouStripHtml:
    def test_strip_html_removes_tags(self):
        text = _strip_html("<p>Hello</p><div>World</div>")
        assert "Hello" in text and "World" in text
        assert "<p>" not in text

    def test_strip_html_unescapes_entities(self):
        text = _strip_html("<p>&nbsp;test&nbsp;</p>")
        assert "test" in text


class TestYixinouSplitRegions:
    def test_split_finds_all_regions(self):
        text = _strip_html(YIXINOU_FIXTURE_HTML)
        chunks = _split_by_regions(text)
        assert "中欧线路" in chunks
        assert "中亚线路" in chunks
        assert "中俄线路" in chunks

    def test_split_chunks_disjoint(self):
        text = _strip_html(YIXINOU_FIXTURE_HTML)
        chunks = _split_by_regions(text)
        # 中欧 chunk 不应包含中亚线路
        assert "中亚线路" not in chunks.get("中欧线路", "")
        # 中亚 chunk 不应包含中俄线路
        assert "中俄线路" not in chunks.get("中亚线路", "")


class TestYixinouExtractRoutes:
    def test_extract_routes_from_chunk(self):
        text = _strip_html(YIXINOU_FIXTURE_HTML)
        chunks = _split_by_regions(text)
        routes = _extract_routes(chunks["中欧线路"])
        assert len(routes) >= 5
        assert "义乌-霍尔果斯-跨两海" in routes
        assert "义乌-阿拉山口-马德里" in routes

    def test_extract_routes_no_duplicates(self):
        text = _strip_html(YIXINOU_FIXTURE_HTML)
        chunks = _split_by_regions(text)
        routes = _extract_routes(chunks["中亚线路"])
        assert len(routes) == len(set(routes))


class TestYixinouExtractStations:
    def test_extract_stations_from_chunk(self):
        text = _strip_html(YIXINOU_FIXTURE_HTML)
        chunks = _split_by_regions(text)
        stations = _extract_stations(chunks["中亚线路"])
        assert "阿拉木图" in stations
        assert "塔什干" in stations
        assert "杜尚别" in stations
        assert len(stations) >= 5


class TestYixinouParse:
    def test_parse_full(self):
        src = YixinouSource()
        parsed = src.parse(YIXINOU_FIXTURE_HTML)
        assert parsed["total_routes"] >= 15
        assert "中欧" in parsed["routes_by_region"]
        assert "中亚" in parsed["routes_by_region"]
        assert "中俄" in parsed["routes_by_region"]
        assert len(parsed["routes_by_region"]["中欧"]) >= 5
        assert len(parsed["routes_by_region"]["中亚"]) >= 5
        assert len(parsed["routes_by_region"]["中俄"]) >= 5

    def test_parse_contacts(self):
        src = YixinouSource()
        parsed = src.parse(YIXINOU_FIXTURE_HTML)
        assert "yeqiuran@yixinou.com" in parsed["contacts"]

    def test_parse_official_stats(self):
        src = YixinouSource()
        parsed = src.parse(YIXINOU_FIXTURE_HTML)
        assert parsed["official_stats"]["total_routes_reported"] == 27
        assert parsed["official_stats"]["countries_covered"] == 50

    def test_validate_ok(self):
        src = YixinouSource()
        assert src.validate(src.parse(YIXINOU_FIXTURE_HTML)) is True

    def test_validate_rejects_empty(self):
        src = YixinouSource()
        assert src.validate(src.parse("<html><body>没有线路</body></html>")) is False

    def test_validate_rejects_too_few_routes(self):
        src = YixinouSource()
        # 只有2条线路，不满足 >= 5 的校验
        html = "<html><body><h2>中欧线路</h2><p>线路</p><ul><li>义乌-马德里</li><li>义乌-伦敦</li></ul></body></html>"
        parsed = src.parse(html)
        assert src.validate(parsed) is False

    def test_parse_non_str_raises(self):
        src = YixinouSource()
        with pytest.raises(TypeError):
            src.parse({"not": "str"})

    def test_fetch_fallbacks_to_snapshot_on_network_error(self, monkeypatch):
        """网络不可达时自动降级到快照数据，仍返回 is_real=True。"""
        src = YixinouSource()

        def boom(url, **k):
            raise RuntimeError("network down")

        monkeypatch.setattr(src, "_get", boom)
        result = src.fetch()
        # 快照 fallback：is_real=True，数据来自本地快照
        assert result.is_real is True
        assert result.data.get("total_routes", 0) >= 20
        assert result.data.get("snapshot_date") == "2026-09-10"
        assert "快照" in result.raw_excerpt or "snapshot" in result.raw_excerpt.lower()


# ==================== Registry 三态回退 ====================


class _StubSource(RealDataSource):
    """可编程桩源：按 scripted 结果依次返回，模拟成功/失败。"""

    name = "stub"
    display_name = "桩源"
    source_url = "http://stub"
    refresh_interval = 60
    description = "test stub"

    def __init__(self, results):
        super().__init__()
        self._results = list(results)
        self.calls = 0

    def fetch_raw(self):
        self.calls += 1
        item = self._results.pop(0) if self._results else None
        if isinstance(item, Exception):
            raise item
        return item

    def parse(self, raw):
        return {"value": raw}


class TestRegistry:
    def test_refresh_success_sets_last_good(self):
        stub = _StubSource([100])
        reg = RealDataRegistry(sources=[stub], db=False)
        res = reg.refresh(force=True)
        assert res["stub"].is_real is True
        assert reg.get_data("stub") == {"value": 100}
        assert reg.real_count() == 1

    def test_failure_falls_back_to_last_good(self):
        stub = _StubSource([100, RuntimeError("down")])
        reg = RealDataRegistry(sources=[stub], db=False)
        reg.refresh(force=True)  # 第一次成功
        res2 = reg.refresh(force=True)  # 第二次失败
        assert res2["stub"].is_real is False
        # 关键：失败后仍能取到上次成功值（三态回退）
        assert reg.get_data("stub") == {"value": 100}
        assert reg.real_count() == 1

    def test_never_succeeded_returns_none(self):
        stub = _StubSource([RuntimeError("down")])
        reg = RealDataRegistry(sources=[stub], db=False)
        reg.refresh(force=True)
        assert reg.get("stub") is None
        assert reg.get_data("stub", default={"fallback": True}) == {"fallback": True}
        assert reg.real_count() == 0

    def test_fresh_cache_skips_refetch(self):
        stub = _StubSource([100, 200])
        reg = RealDataRegistry(sources=[stub], db=False)
        reg.refresh(force=True)  # 用掉 100
        reg.refresh(force=False)  # 仍新鲜，应跳过抓取
        assert stub.calls == 1
        assert reg.get_data("stub") == {"value": 100}

    def test_status_includes_legacy_three_states(self):
        stub = _StubSource([100])
        reg = RealDataRegistry(sources=[stub], db=False)
        reg.refresh(force=True)
        statuses = {s["name"]: s["status"] for s in reg.status()}
        assert statuses["桩源"] == DataSourceStatus.REAL
        assert statuses["Amazon"] == DataSourceStatus.PLANNED
        assert statuses["义乌小商品城"] == DataSourceStatus.DEMO


# ==================== Registry 持久化 ====================


class TestRegistryPersistence:
    def test_save_and_reload_from_db(self, tmp_path):
        from app.db.database import Database

        db = Database(db_path=str(tmp_path / "test.db"))
        # 第一个 registry 抓取成功并落库
        stub1 = _StubSource([100])
        reg1 = RealDataRegistry(sources=[stub1], db=db)
        reg1.refresh(force=True)
        # 模拟进程重启：新 registry（内存空），应从 DB 回退到上次成功值
        stub2 = _StubSource([RuntimeError("down")])
        stub2.name = "stub"
        reg2 = RealDataRegistry(sources=[stub2], db=db)
        assert reg2.get_data("stub") == {"value": 100}
        assert reg2.real_count() == 1


# ==================== 按品类取指数 / 汇率 ====================


class TestRegistryLookups:
    def _reg_with_index(self):
        """构造一个已成功抓取 yiwu_index 的 registry（注入桩数据，不走网络）。"""
        reg = RealDataRegistry(sources=[], db=False)
        payload = {
            "records": [
                {
                    "category": "伞具",
                    "index_value": 1576.52,
                    "as_of": "2026年7月",
                    "change_pct": 6.4,
                    "index_scale": "官方千点基准",
                    "excerpt": "x",
                },
                {
                    "category": "义乌指数（综合）",
                    "index_value": 1550.67,
                    "as_of": "2026年4月",
                    "change_pct": 1.85,
                    "index_scale": "官方千点基准",
                    "excerpt": "y",
                },
            ],
            "record_count": 2,
        }
        result = FetchResult(
            source="yiwu_index",
            is_real=True,
            data=payload,
            fetched_at=time.time(),
            source_url="https://www.ywindex.com/report",
            freshness_seconds=7 * 24 * 3600,
        )
        reg._last_good["yiwu_index"] = result
        return reg

    def test_exact_category_match(self):
        reg = self._reg_with_index()
        got = reg.get_index_for_category("伞具")
        assert got["is_real"] is True
        assert got["index_value"] == 1576.52
        assert got["category_matched"] == "伞具"

    def test_fallback_to_composite(self):
        reg = self._reg_with_index()
        got = reg.get_index_for_category("不存在的品类")
        assert got["is_real"] is True
        assert got["category_matched"] == "义乌指数（综合）"
        assert got["index_value"] == 1550.67

    def test_no_real_data_returns_not_real(self):
        reg = RealDataRegistry(sources=[], db=False)
        got = reg.get_index_for_category("伞具")
        assert got["is_real"] is False
        assert got["index_value"] is None

    def test_exchange_rate_lookup(self):
        reg = RealDataRegistry(sources=[], db=False)
        payload = {
            "base": "USD",
            "as_of": "Tue, 08 Sep 2026",
            "focus_rates": {"CNY": 6.72, "EUR": 0.86},
            "all_rates": {"CNY": 6.72},
            "provider": "open.er-api.com",
        }
        reg._last_good["exchange_rate"] = FetchResult(
            source="exchange_rate",
            is_real=True,
            data=payload,
            fetched_at=time.time(),
            source_url="https://open.er-api.com/v6/latest/USD",
            freshness_seconds=86400,
        )
        got = reg.get_exchange_rate("CNY")
        assert got["is_real"] is True and got["rate"] == 6.72
        assert reg.get_exchange_rate("EUR")["rate"] == 0.86


# ==================== 义新欧线路查询 ====================


class TestYixinouLookup:
    def _reg_with_yixinou(self):
        """构造一个已成功抓取 yixinou 的 registry（注入桩数据，不走网络）。"""
        reg = RealDataRegistry(sources=[], db=False)
        payload = {
            "provider": "义新欧班列官网 yixinou.com/lines",
            "routes_by_region": {
                "中欧": ["义乌-霍尔果斯-跨两海", "义乌-阿拉山口-马德里"],
                "中亚": ["义乌-霍尔果斯-阿拉木图", "义乌-阿拉山口-塔什干"],
                "中俄": ["义乌-满洲里-明斯克", "义乌-霍尔果斯-莫斯科"],
            },
            "stations_by_region": {
                "中欧": ["马德里", "伦敦"],
                "中亚": ["阿拉木图", "塔什干"],
                "中俄": ["莫斯科", "明斯克"],
            },
            "total_routes": 6,
            "all_routes": [
                "义乌-霍尔果斯-跨两海",
                "义乌-阿拉山口-马德里",
                "义乌-霍尔果斯-阿拉木图",
                "义乌-阿拉山口-塔什干",
                "义乌-满洲里-明斯克",
                "义乌-霍尔果斯-莫斯科",
            ],
            "contacts": ["yeqiuran@yixinou.com"],
            "official_stats": {
                "total_routes_reported": 27,
                "countries_covered": 50,
                "cities_connected": 160,
                "source": "交通部/海关总署公开报道（2026年8月）",
            },
        }
        result = FetchResult(
            source="yixinou",
            is_real=True,
            data=payload,
            fetched_at=time.time(),
            source_url="https://yixinou.com/lines",
            freshness_seconds=30 * 24 * 3600,
        )
        reg._last_good["yixinou"] = result
        return reg

    def test_get_all_routes(self):
        reg = self._reg_with_yixinou()
        got = reg.get_yixinou_routes()
        assert got["is_real"] is True
        assert got["total_routes"] == 6
        assert len(got["routes"]) == 6
        assert got["total_routes_reported"] == 27

    def test_filter_by_region_europe(self):
        reg = self._reg_with_yixinou()
        got = reg.get_yixinou_routes("欧洲")
        assert got["is_real"] is True
        # 过滤后应只含中欧线路
        assert len(got["routes"]) == 2
        assert "义乌-霍尔果斯-跨两海" in got["routes"]

    def test_filter_by_region_central_asia(self):
        reg = self._reg_with_yixinou()
        got = reg.get_yixinou_routes("中亚")
        assert got["is_real"] is True
        assert len(got["routes"]) == 2
        assert "义乌-霍尔果斯-阿拉木图" in got["routes"]

    def test_no_real_data_returns_not_real(self):
        reg = RealDataRegistry(sources=[], db=False)
        got = reg.get_yixinou_routes()
        assert got["is_real"] is False
        assert got["total_routes"] == 0
