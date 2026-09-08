"""源A：实时汇率数据源（open.er-api.com）

为什么选它做 P1-1 的"保证可现场自证"样板：
  - 免费、无需 API Key、无验证码/反爬，演示现场可稳定复现请求-响应；
  - 每日更新且响应自带 time_last_update_utc 时间戳，天然满足"数据带时间戳"验收；
  - 与义乌商户出海强相关：USD/CNY 结汇价、目标市场货币（EUR/GBP/JPY 等）
    直接服务"定价/利润测算"场景，替换原先拍脑袋的静态汇率。

数据口径（诚实标注）：
  - 来源为 open.er-api.com 聚合的每日参考汇率，非银行实时牌价；
  - 更新频率为"每日"，故 freshness 设为 24h，对外表述为"每日更新"而非"实时"。
"""

from __future__ import annotations

from typing import Any, Dict, Union

from .base import RealDataSource

API_URL = "https://open.er-api.com/v6/latest/USD"

# 义乌出海重点目标市场货币（与项目 SUPPORTED_REGIONS / 39城叙事呼应）
FOCUS_CURRENCIES = ["CNY", "EUR", "GBP", "JPY", "USD", "RUB", "KRW", "AUD", "CAD", "SGD"]


class ExchangeRateSource(RealDataSource):
    """每日参考汇率源（USD 基准）。"""

    name = "exchange_rate"
    display_name = "实时汇率"
    source_url = API_URL
    refresh_interval = 24 * 3600  # 每日更新
    description = "open.er-api.com 每日参考汇率（USD 基准），含 CNY/EUR/GBP 等出海目标市场货币，每日更新"

    def fetch_raw(self) -> Dict[str, Any]:
        """抓取汇率 JSON。result != success 视为失败抛异常。"""
        resp = self._get(API_URL)
        payload = resp.json()
        if payload.get("result") != "success":
            raise ValueError(f"汇率 API 返回非 success：{payload.get('result')} / {payload.get('error-type')}")
        return payload

    def parse(self, raw: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """解析为 {base, as_of, rates(全量), focus(重点货币), cny_rate}。"""
        if isinstance(raw, str):
            raise TypeError("汇率源期望 dict 原始数据，收到 str")
        rates: Dict[str, float] = raw.get("rates", {}) or {}
        focus = {c: rates[c] for c in FOCUS_CURRENCIES if c in rates}
        return {
            "base": raw.get("base_code", "USD"),
            # API 自带的官方更新时间戳（可自证数据新鲜度）
            "as_of": raw.get("time_last_update_utc", ""),
            "as_of_unix": raw.get("time_last_update_unix", 0),
            "next_update": raw.get("time_next_update_utc", ""),
            "focus_rates": focus,
            "cny_rate": rates.get("CNY"),
            "all_rates": rates,
            "provider": "open.er-api.com",
        }

    def validate(self, parsed: Dict[str, Any]) -> bool:
        """校验：必须有 CNY 汇率且落在合理区间（防 API 返坏值被当真）。"""
        if not parsed or not isinstance(parsed, dict):
            return False
        cny = parsed.get("cny_rate")
        if not isinstance(cny, (int, float)):
            return False
        # USD/CNY 合理区间 5~9（超出说明数据异常）
        if not (5.0 <= float(cny) <= 9.0):
            return False
        return bool(parsed.get("focus_rates"))
