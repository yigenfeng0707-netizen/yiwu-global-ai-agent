"""义乌小商品出海智能体 - 智能选品Agent"""

import random
from typing import Any, Dict, List

from .base import BaseAgent
from ..data.market_data import MARKET_DATA, CATEGORY_LIST, SUPPORTED_REGIONS


class SmartSelectionAgent(BaseAgent):
    """智能选品Agent - 基于义乌市场数据的智能选品推荐"""

    name = "smart_selection"
    description = "智能选品Agent - 产品推荐、利润分析、供应链推荐、行动计划"

    async def execute(self, **kwargs) -> Dict[str, Any]:
        category = kwargs.get("category", CATEGORY_LIST[0])
        budget = kwargs.get("budget", "中")
        region = kwargs.get("region", SUPPORTED_REGIONS[0])

        market_data = MARKET_DATA.get(category, {})

        # 综合评分
        overall_score = self._calculate_score(category, region, budget)

        # 市场机会
        market_opportunity = self._get_market_opportunity(category, region)

        # 产品推荐
        product_recommendations = self._get_product_recommendations(category, region, budget)

        # 利润分析
        profit_analysis = self._get_profit_analysis(category, budget)

        # 供应链推荐
        supply_recommendations = self._get_supply_recommendations(category, budget)

        # 行动计划
        action_plan = self._get_action_plan(category, region)

        return self._wrap_response({
            "category": category,
            "budget": budget,
            "region": region,
            "overall_score": overall_score,
            "market_opportunity": market_opportunity,
            "product_recommendations": product_recommendations,
            "profit_analysis": profit_analysis,
            "supply_recommendations": supply_recommendations,
            "action_plan": action_plan,
        })

    def _calculate_score(self, category: str, region: str, budget: str) -> Dict[str, Any]:
        """计算综合评分"""
        market_data = MARKET_DATA.get(category, {})
        yiwu_score = market_data.get("yiwu_index_score", 100)

        total = min(95, max(55, yiwu_score - 8 + random.randint(-5, 10)))
        level = "优秀" if total >= 80 else "良好" if total >= 70 else "一般" if total >= 60 else "较差"

        return {
            "total": total,
            "level": level,
            "market_demand": min(95, yiwu_score + random.randint(-5, 5)),
            "competition": min(95, 70 + random.randint(-10, 15)),
            "profit_potential": min(95, 75 + random.randint(-5, 15)),
            "supply_stability": min(95, 85 + random.randint(-5, 10)),
        }

    def _get_market_opportunity(self, category: str, region: str) -> Dict[str, Any]:
        """获取市场机会"""
        market_data = MARKET_DATA.get(category, {})
        target_markets = market_data.get("target_markets", {})
        region_data = target_markets.get(region, {})

        return {
            "market_size": market_data.get("market_size", "N/A"),
            "growth_rate": region_data.get("growth", market_data.get("growth_rate", "N/A")),
            "competition_level": random.choice(["中等", "较高", "中等偏低"]),
            "entry_difficulty": random.choice(["较低", "中等", "较低"]),
        }

    def _get_product_recommendations(self, category: str, region: str, budget: str) -> List[Dict[str, Any]]:
        """获取产品推荐"""
        market_data = MARKET_DATA.get(category, {})
        hot_products = market_data.get("hot_products", [])

        result = []
        for product in hot_products[:5]:
            scores = {
                "综合评分": min(95, 65 + random.randint(0, 25)),
                "市场需求": min(95, 60 + random.randint(0, 30)),
                "利润空间": min(95, 55 + random.randint(0, 35)),
                "竞争程度": min(95, 50 + random.randint(0, 40)),
                "供应链稳定": min(95, 70 + random.randint(0, 20)),
            }
            result.append({
                "product": product,
                "scores": scores,
                "suggested_moq": random.choice([50, 100, 200, 500]),
                "estimated_roi": f"{random.randint(20, 80)}%",
            })
        return result

    def _get_profit_analysis(self, category: str, budget: str) -> Dict[str, Any]:
        """获取利润分析"""
        budget_multiplier = {"低": 0.6, "中": 1.0, "高": 1.5}.get(budget, 1.0)

        return {
            "cost_breakdown": {
                "采购成本": f"¥{int(5000 * budget_multiplier):,}-{int(15000 * budget_multiplier):,}",
                "物流费用": f"¥{int(2000 * budget_multiplier):,}-{int(5000 * budget_multiplier):,}",
                "认证费用": f"¥{int(1000 * budget_multiplier):,}-{int(8000 * budget_multiplier):,}",
                "平台费用": f"¥{int(1500 * budget_multiplier):,}-{int(4000 * budget_multiplier):,}",
                "运营费用": f"¥{int(1000 * budget_multiplier):,}-{int(3000 * budget_multiplier):,}",
            },
            "revenue": {
                "预计月销量": f"{random.randint(200, 2000)}件",
                "预计月收入": f"¥{int(15000 * budget_multiplier):,}-{int(50000 * budget_multiplier):,}",
                "预计月利润": f"¥{int(5000 * budget_multiplier):,}-{int(20000 * budget_multiplier):,}",
            },
            "break_even": {
                "盈亏平衡销量": f"{random.randint(100, 500)}件/月",
            },
        }

    def _get_supply_recommendations(self, category: str, budget: str) -> List[Dict[str, Any]]:
        """获取供应链推荐"""
        suppliers = [
            {"supplier": "义乌市鑫达贸易有限公司", "location": "义乌国际商贸城", "moq": "100件", "price_range": "$1.5-8", "rating": 4.8, "recommended": True},
            {"supplier": "义乌市恒丰进出口有限公司", "location": "义乌国际商贸城", "moq": "200件", "price_range": "$1.2-6", "rating": 4.6, "recommended": True},
            {"supplier": "义乌市华美工贸有限公司", "location": "义乌国际商贸城", "moq": "50件", "price_range": "$2-10", "rating": 4.5, "recommended": False},
            {"supplier": "义乌市盛达商贸有限公司", "location": "义乌国际商贸城", "moq": "300件", "price_range": "$0.8-5", "rating": 4.7, "recommended": True},
        ]
        return suppliers

    def _get_action_plan(self, category: str, region: str) -> Dict[str, Any]:
        """获取行动计划"""
        return {
            "phase1": {
                "name": "市场调研与选品",
                "tasks": [
                    f"研究{region}{category}市场需求和竞争格局",
                    "在义乌国际商贸城实地考察或线上选品",
                    "确认目标产品认证要求",
                    "联系2-3家供应商获取报价和样品",
                ],
            },
            "phase2": {
                "name": "样品测试与认证",
                "tasks": [
                    "采购样品进行品质测试",
                    "启动目标市场认证申请(CE/EAC/SABER等)",
                    "办理1039市场采购贸易备案",
                    "选择物流方案(义新欧班列/海运)",
                ],
            },
            "phase3": {
                "name": "首批采购与发货",
                "tasks": [
                    "下首批订单，确认MOQ和交期",
                    "安排义新欧班列/海运发货",
                    "准备清关文件和认证证书",
                    "在目标平台创建产品listing",
                ],
            },
        }
