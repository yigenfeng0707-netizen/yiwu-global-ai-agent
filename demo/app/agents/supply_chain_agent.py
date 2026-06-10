"""义乌小商品出海智能体 - 供应链匹配Agent"""

import random
from typing import Any, Dict, List

from .base import BaseAgent
from ..data.market_data import (
    MARKET_DATA, CATEGORY_LIST, YIWU_TRADE_CITY, YIXINOU_DATA,
    MARKET_PURCHASE_TRADE_1039,
)
from ..data.sources import DataSourceManager


class SupplyChainAgent(BaseAgent):
    """供应链匹配Agent - 匹配义乌7.5万商户、210万+SKU"""

    name = "supply_chain"
    description = "供应链匹配Agent - 义乌小商品城供应商匹配、采购价格/MOQ/交期、义新欧班列物流、1039市场采购贸易"

    def __init__(self):
        self.data_manager = DataSourceManager()

    async def execute(self, **kwargs) -> Dict[str, Any]:
        category = kwargs.get("category", CATEGORY_LIST[0])
        region = kwargs.get("region", "")
        budget = kwargs.get("budget", "中")

        # 供应商匹配
        suppliers = self._match_suppliers(category, region, budget)

        # 采购信息
        purchase_info = self._get_purchase_info(category)

        # 义新欧班列物流
        logistics = self._get_logistics(region)

        # 1039模式信息
        trade_1039 = self._get_1039_info(category)

        # 供应链评分
        score = self._calculate_supply_score(category, region)

        return self._wrap_response({
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

    def _match_suppliers(self, category: str, region: str, budget: str) -> List[Dict[str, Any]]:
        """匹配供应商"""
        market_data = MARKET_DATA.get(category, {})
        hot_products = market_data.get("hot_products", [])

        suppliers = []
        supplier_names = [
            "义乌市鑫达贸易有限公司", "义乌市恒丰进出口有限公司",
            "义乌市华美工贸有限公司", "义乌市盛达商贸有限公司",
            "义乌市远东国际贸易有限公司", "义乌市金桥进出口有限公司",
            "义乌市新纪元商贸有限公司", "义乌市环球小商品有限公司",
        ]

        for i, product in enumerate(hot_products[:6]):
            price_base = random.uniform(0.5, 15)
            moq = random.choice([50, 100, 200, 300, 500])
            if budget == "低":
                moq = max(50, moq // 2)
            elif budget == "高":
                moq = moq * 2

            suppliers.append({
                "supplier": supplier_names[i % len(supplier_names)],
                "product": product,
                "district": self._get_district(category),
                "moq": moq,
                "unit_price": f"${round(price_base, 2)}-{round(price_base * 1.5, 2)}",
                "delivery_days": random.choice([3, 5, 7, 10, 15]),
                "rating": round(random.uniform(4.0, 5.0), 1),
                "certifications": self._get_certifications(category, region),
                "recommended": i < 3,
            })

        return suppliers

    def _get_purchase_info(self, category: str) -> Dict[str, Any]:
        """获取采购信息"""
        market_data = MARKET_DATA.get(category, {})
        return {
            "avg_price_range": market_data.get("avg_price_range", "$1-20"),
            "yiwu_advantage": market_data.get("yiwu_advantage", ""),
            "yiwu_index_score": market_data.get("yiwu_index_score", 100),
            "price_trend": random.choice(["上涨", "稳定", "微涨"]),
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
        """计算供应链评分"""
        market_data = MARKET_DATA.get(category, {})
        yiwu_score = market_data.get("yiwu_index_score", 100)

        total_score = min(95, max(60, yiwu_score - 5 + random.randint(-3, 5)))
        level = "优秀" if total_score >= 80 else "良好" if total_score >= 70 else "一般" if total_score >= 60 else "较差"

        return {
            "total": total_score,
            "level": level,
            "dimensions": {
                "供应商丰富度": min(95, yiwu_score + random.randint(-5, 5)),
                "价格竞争力": min(95, yiwu_score + random.randint(-3, 8)),
                "物流便捷度": min(95, 85 + random.randint(-5, 10)),
                "认证支持": min(95, 75 + random.randint(-5, 10)),
                "1039便利度": min(95, 90 + random.randint(-3, 5)),
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
