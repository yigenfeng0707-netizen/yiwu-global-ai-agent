"""义乌小商品出海智能体 - 供应链匹配Agent（确定性匹配 + LLM采购建议）"""

import re
from typing import Any, Dict, List, Tuple

from .base import BaseAgent
from ..data.market_data import (
    MARKET_DATA, CATEGORY_LIST, YIWU_TRADE_CITY, YIXINOU_DATA,
    MARKET_PURCHASE_TRADE_1039,
)
from ..data.sources import DataSourceManager
from ..services.llm import llm_service


def _clamp(v: float, lo: int = 40, hi: int = 95) -> int:
    return int(max(lo, min(hi, round(v))))


def _parse_price_range(s: Any, default: Tuple[float, float] = (1.0, 10.0)) -> Tuple[float, float]:
    """从 '$0.5-15' / '$1.5-8' 之类字符串解析价格区间 (low, high)。"""
    nums = re.findall(r"[\d.]+", str(s))
    try:
        if len(nums) >= 2:
            return float(nums[0]), float(nums[1])
        if len(nums) == 1:
            v = float(nums[0])
            return v, round(v * 2, 2)
    except ValueError:
        pass
    return default


class SupplyChainAgent(BaseAgent):
    """供应链匹配Agent - 匹配义乌7.5万商户、210万+SKU（确定性匹配 + LLM增强）"""

    name = "supply_chain"
    description = "供应链匹配Agent - 义乌小商品城供应商匹配、采购价格/MOQ/交期、义新欧班列物流、1039市场采购贸易"

    # 确定性阶梯（按产品序号取模，避免 random 导致同输入结果漂移）
    _MOQ_LADDER = [100, 200, 300, 500, 150, 300]
    _DELIVERY_LADDER = [7, 5, 10, 3, 15, 7]

    def __init__(self):
        super().__init__()
        self.data_manager = DataSourceManager()

    async def execute(self, **kwargs) -> Dict[str, Any]:
        category = kwargs.get("category", CATEGORY_LIST[0])
        region = kwargs.get("region", "")
        budget = kwargs.get("budget", "中")

        suppliers = self._match_suppliers(category, region, budget)
        purchase_info = self._get_purchase_info(category)
        logistics = self._get_logistics(region)
        trade_1039 = self._get_1039_info(category)
        score = self._calculate_supply_score(category, region)

        result = self._wrap_response({
            "category": category,
            "region": region,
            "budget": budget,
            "suppliers": suppliers,
            "purchase_info": purchase_info,
            "logistics": logistics,
            "trade_1039": trade_1039,
            "supply_score": score,
            "yiwu_trade_city": {
                "total_shops": YIWU_TRADE_CITY["total_shops"],
                "total_skus": YIWU_TRADE_CITY["total_skus"],
                "district": self._get_district(category),
            },
        })

        # LLM 增强：生成采购与物流策略建议（无 API Key 时降级）
        advice = await self._llm_supply_advice(category, region, budget, suppliers, score)
        if advice:
            result["ai_recommendation"] = advice.strip()
            result["ai_used"] = True
        else:
            result["ai_used"] = False

        self.record_query({"category": category, "region": region, "budget": budget},
                          f"供应链评分{score['total']}/{score['level']}")
        return result

    def _match_suppliers(self, category: str, region: str, budget: str) -> List[Dict[str, Any]]:
        """匹配供应商（确定性：价格由品类价格区间推导，MOQ/交期/评分按序号阶梯）"""
        market_data = MARKET_DATA.get(category, {})
        hot_products = market_data.get("hot_products", [])
        low, high = _parse_price_range(market_data.get("avg_price_range", "$1-10"))

        supplier_names = [
            "义乌市鑫达贸易有限公司", "义乌市恒丰进出口有限公司",
            "义乌市华美工贸有限公司", "义乌市盛达商贸有限公司",
            "义乌市远东国际贸易有限公司", "义乌市金桥进出口有限公司",
            "义乌市新纪元商贸有限公司", "义乌市环球小商品有限公司",
        ]

        suppliers = []
        products = hot_products[:6] or [category]
        span = max(high - low, 0.1)
        for i, product in enumerate(products):
            frac = (i % 5) / 5                       # 0,0.2,0.4,0.6,0.8 确定性分布
            price_base = round(low + span * frac * 0.6, 2)
            moq = self._MOQ_LADDER[i % len(self._MOQ_LADDER)]
            if budget == "低":
                moq = max(50, moq // 2)
            elif budget == "高":
                moq = moq * 2
            rating = round(max(4.0, min(4.9, 4.9 - i * 0.12)), 1)

            suppliers.append({
                "supplier": supplier_names[i % len(supplier_names)],
                "product": product,
                "district": self._get_district(category),
                "moq": moq,
                "unit_price": f"${price_base}-{round(price_base * 1.5, 2)}",
                "delivery_days": self._DELIVERY_LADDER[i % len(self._DELIVERY_LADDER)],
                "rating": rating,
                "certifications": self._get_certifications(category, region),
                "recommended": i < 3,
            })

        return suppliers

    def _get_purchase_info(self, category: str) -> Dict[str, Any]:
        """获取采购信息（价格趋势由义乌指数确定性推导）"""
        market_data = MARKET_DATA.get(category, {})
        yiwu = market_data.get("yiwu_index_score", 100)
        price_trend = "上涨" if yiwu >= 104 else "微涨" if yiwu >= 101 else "稳定"
        return {
            "avg_price_range": market_data.get("avg_price_range", "$1-20"),
            "yiwu_advantage": market_data.get("yiwu_advantage", ""),
            "yiwu_index_score": yiwu,
            "price_trend": price_trend,
            "sample_available": True,
            "sample_lead_time": "3-5天",
            "bulk_lead_time": "7-15天",
            "payment_terms": ["T/T", "L/C", "西联汇款", "PayPal"],
        }

    def _get_logistics(self, region: str) -> Dict[str, Any]:
        """获取义新欧班列物流信息"""
        logistics_data = self.data_manager.fetch_by_source("义新欧班列", "", region)
        if logistics_data:
            return logistics_data

        return {
            "source": "义新欧班列",
            "total_routes": 19,
            "countries_covered": 50,
            "cities_connected": 160,
            "routes": YIXINOU_DATA["main_routes"],
            "advantages": [
                "比海运快2-3倍",
                "比空运便宜60-80%",
                "通关便利化，优先查验",
            ],
        }

    def _get_1039_info(self, category: str) -> Dict[str, Any]:
        """获取1039市场采购贸易信息"""
        return {
            "applicable": True,
            "name": MARKET_PURCHASE_TRADE_1039["name"],
            "description": MARKET_PURCHASE_TRADE_1039["description"],
            "advantages": MARKET_PURCHASE_TRADE_1039["advantages"],
            "conditions": MARKET_PURCHASE_TRADE_1039["conditions"],
            "max_value_per_shipment": "$150,000",
            "simplified_declaration": True,
            "vat_exemption": True,
        }

    def _calculate_supply_score(self, category: str, region: str) -> Dict[str, Any]:
        """计算供应链评分（确定性：义乌指数 + 义新欧直达区域物流加成）"""
        market_data = MARKET_DATA.get(category, {})
        yiwu = market_data.get("yiwu_index_score", 100)
        # 义新欧班列直达区域（欧洲/中亚）物流便捷度加成
        logistics_bonus = 6 if region and ("欧洲" in region or "中亚" in region) else 0

        total_score = _clamp(yiwu - 3 + logistics_bonus, 60, 95)
        level = "优秀" if total_score >= 80 else "良好" if total_score >= 70 else "一般" if total_score >= 60 else "较差"

        return {
            "total": total_score,
            "level": level,
            "dimensions": {
                "供应商丰富度": _clamp(yiwu, 60, 95),
                "价格竞争力": _clamp(yiwu + 2, 60, 95),
                "物流便捷度": _clamp(84 + logistics_bonus, 60, 95),
                "认证支持": _clamp(78, 60, 95),
                "1039便利度": _clamp(92, 60, 95),
            },
        }

    def _get_district(self, category: str) -> str:
        """获取品类所在商贸城区"""
        district_map = {
            "玩具": "一区", "工艺品": "一区",
            "五金工具": "二区", "电子电器": "二区",
            "文具办公用品": "三区", "日用百货": "三区",
            "服装服饰": "四区", "针织品": "四区",
            "饰品配件": "五区", "家居装饰": "五区",
        }
        return district_map.get(category, "综合区")

    def _get_certifications(self, category: str, region: str) -> List[str]:
        """获取品类所需认证"""
        cert_map = {
            "日用百货": ["CE", "FDA(食品接触)"],
            "饰品配件": ["CE", "REACH", "EN1811"],
            "玩具": ["CE", "EN71", "ASTM F963"],
            "文具办公用品": ["CE", "EN71"],
            "针织品": ["CE", "Oeko-Tex"],
            "工艺品": ["CE", "阻燃测试"],
            "电子电器": ["CE", "RoHS", "EMC", "LVD"],
            "五金工具": ["CE", "EN标准"],
            "服装服饰": ["CE", "EN14682(童装)"],
            "家居装饰": ["CE", "UL/ETL(灯饰)"],
        }
        certs = cert_map.get(category, ["CE"])
        if "欧洲" in region or "中亚" in region:
            if "EAC" not in certs:
                certs.append("EAC(中亚)")
        if "中东" in region:
            if "SABER" not in certs:
                certs.append("SABER(沙特)")
        return certs

    async def _llm_supply_advice(self, category: str, region: str, budget: str,
                                 suppliers: List[Dict[str, Any]], score: Dict[str, Any]) -> Any:
        """调用 LLM 生成采购与物流策略建议；未配置 API Key 时返回 None（降级）。"""
        if not llm_service.api_key:
            return None
        top = "、".join(s["supplier"] for s in suppliers[:2]) or "义乌国际商贸城供应商"
        district = self._get_district(category)
        prompt = (
            f"请针对以下义乌小商品供应链采购场景，给出3条可执行的采购与物流建议（每条不超过60字，聚焦实操）：\n"
            f"品类：{category}（商贸城{district}）\n目标区域：{region or '全球'}\n预算等级：{budget}\n"
            f"供应链综合评分：{score['total']}（{score['level']}）\n推荐供应商：{top}\n"
            f"请结合 1039 市场采购贸易模式与义新欧班列物流，给出选商、议价与备货发运的专业建议。"
        )
        return await self.llm_generate(
            prompt,
            system_prompt="你是义乌小商品城资深供应链与跨境物流专家，精通 1039 市场采购贸易与义新欧班列，回答专业、简洁、可执行。",
            temperature=0.5, max_tokens=420,
        )
