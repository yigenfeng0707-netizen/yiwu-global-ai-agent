"""义乌小商品出海智能体 - 智能选品Agent（确定性评分 + LLM策略增强）"""

from typing import Any, Dict, List

from .base import BaseAgent
from ..data.market_data import MARKET_DATA, CATEGORY_LIST, SUPPORTED_REGIONS
from ..services.llm import llm_service


def _parse_pct(value: Any, default: float = 0.0) -> float:
    """把 '12.5%' / '580亿美元' 之类的字符串解析为首个数值，失败返回 default。"""
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value)
    num = ""
    for ch in s:
        if ch.isdigit() or ch == ".":
            num += ch
        elif num:
            break
    try:
        return float(num) if num else default
    except ValueError:
        return default


def _clamp(v: float, lo: int = 40, hi: int = 95) -> int:
    return int(max(lo, min(hi, round(v))))


class SmartSelectionAgent(BaseAgent):
    """智能选品Agent - 基于义乌市场数据的确定性评分 + LLM 选品策略增强"""

    name = "smart_selection"
    description = "智能选品Agent - 产品推荐、利润分析、供应链推荐、行动计划"

    LLM_SYSTEM_PROMPT = "你是义乌小商品城资深跨境选品专家，擅长基于市场数据给出可执行的选品、定价与备货建议，回答专业、简洁、聚焦实操。"

    # 预算等级对利润潜力/销量的调节
    _BUDGET_BONUS = {"低": -6, "中": 0, "高": 6}
    _BUDGET_MULT = {"低": 0.6, "中": 1.0, "高": 1.5}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        category = kwargs.get("category", CATEGORY_LIST[0])
        budget = kwargs.get("budget", "中")
        region = kwargs.get("region", SUPPORTED_REGIONS[0])

        # 综合评分（确定性）
        overall_score = self._calculate_score(category, region, budget)

        # 市场机会（确定性）
        market_opportunity = self._get_market_opportunity(category, region)

        # 产品推荐（确定性）
        product_recommendations = self._get_product_recommendations(category, region, budget, overall_score)

        # 利润分析（确定性）
        profit_analysis = self._get_profit_analysis(category, budget)

        # 供应链推荐
        supply_recommendations = self._get_supply_recommendations(category, budget)

        # 行动计划
        action_plan = self._get_action_plan(category, region)

        result = self._wrap_response({
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

        # LLM 增强：生成选品策略解读（无 API Key 时优雅降级，不影响结构化结果）
        advice = await self._llm_selection_advice(category, region, budget, overall_score, product_recommendations)
        if advice:
            result["ai_recommendation"] = advice.strip()
            result["ai_used"] = True
        else:
            result["ai_used"] = False

        self.record_query({"category": category, "region": region, "budget": budget},
                          f"选品评分{overall_score['total']}/{overall_score['level']}")
        return result

    def _score_dims(self, category: str, region: str, budget: str) -> Dict[str, float]:
        """基于 MARKET_DATA 真实字段确定性推导四维原始分（供评分与产品推荐复用）。"""
        md = MARKET_DATA.get(category, {})
        yiwu = _parse_pct(md.get("yiwu_index_score", 100), 100)
        tm = md.get("target_markets", {}).get(region, {})
        growth = _parse_pct(tm.get("growth") or md.get("growth_rate", "10"), 10)
        share = _parse_pct(tm.get("share", "10"), 10)
        bonus = self._BUDGET_BONUS.get(budget, 0)

        market_demand = 50 + growth * 1.4 + (yiwu - 100) * 0.9
        competition = 88 - share * 0.9            # 份额越高竞争越激烈，竞争友好度越低
        profit_potential = 56 + growth * 1.1 + bonus + (yiwu - 100) * 0.4
        supply_stability = 62 + (yiwu - 100) * 1.6
        return {
            "market_demand": market_demand,
            "competition": competition,
            "profit_potential": profit_potential,
            "supply_stability": supply_stability,
            "growth": growth,
            "share": share,
        }

    def _calculate_score(self, category: str, region: str, budget: str) -> Dict[str, Any]:
        """计算综合评分（确定性，同输入同输出）"""
        d = self._score_dims(category, region, budget)
        market_demand = _clamp(d["market_demand"])
        competition = _clamp(d["competition"])
        profit_potential = _clamp(d["profit_potential"])
        supply_stability = _clamp(d["supply_stability"])

        total = _clamp(
            0.30 * market_demand + 0.25 * profit_potential
            + 0.25 * supply_stability + 0.20 * competition,
            45, 95,
        )
        level = "优秀" if total >= 80 else "良好" if total >= 70 else "一般" if total >= 60 else "较差"
        return {
            "total": total,
            "level": level,
            "market_demand": market_demand,
            "competition": competition,
            "profit_potential": profit_potential,
            "supply_stability": supply_stability,
        }

    def _get_market_opportunity(self, category: str, region: str) -> Dict[str, Any]:
        """获取市场机会（确定性映射）"""
        md = MARKET_DATA.get(category, {})
        tm = md.get("target_markets", {}).get(region, {})
        d = self._score_dims(category, region, "中")
        share, growth = d["share"], d["growth"]

        competition_level = "较高" if share >= 28 else "中等" if share >= 14 else "中等偏低"
        entry_difficulty = "较低" if growth >= 16 else "中等" if growth >= 10 else "较高"
        return {
            "market_size": md.get("market_size", "N/A"),
            "growth_rate": tm.get("growth", md.get("growth_rate", "N/A")),
            "competition_level": competition_level,
            "entry_difficulty": entry_difficulty,
        }

    def _get_product_recommendations(self, category: str, region: str, budget: str,
                                     overall_score: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取产品推荐（确定性：基于品类基准分 + 热门排名）"""
        md = MARKET_DATA.get(category, {})
        hot_products = md.get("hot_products", [])
        d = self._score_dims(category, region, budget)
        moq_ladder = [100, 200, 300, 500, 800]

        result = []
        for i, product in enumerate(hot_products[:5]):
            rank = (len(hot_products[:5]) - i) * 3  # 排名越靠前分越高
            scores = {
                "综合评分": _clamp(overall_score["total"] + rank - 6, 50, 95),
                "市场需求": _clamp(d["market_demand"] + rank - 4, 50, 95),
                "利润空间": _clamp(d["profit_potential"] + rank - 8, 50, 95),
                "竞争程度": _clamp(d["competition"] - rank + 8, 50, 95),
                "供应链稳定": _clamp(d["supply_stability"] + rank - 5, 50, 95),
            }
            result.append({
                "product": product,
                "scores": scores,
                "suggested_moq": moq_ladder[i % len(moq_ladder)],
                "estimated_roi": f"{24 + rank * 2}%",
            })
        return result

    def _get_profit_analysis(self, category: str, budget: str) -> Dict[str, Any]:
        """获取利润分析（确定性：基于预算系数）"""
        m = self._BUDGET_MULT.get(budget, 1.0)
        return {
            "cost_breakdown": {
                "采购成本": f"¥{int(5000 * m):,}-{int(15000 * m):,}",
                "物流费用": f"¥{int(2000 * m):,}-{int(5000 * m):,}",
                "认证费用": f"¥{int(1000 * m):,}-{int(8000 * m):,}",
                "平台费用": f"¥{int(1500 * m):,}-{int(4000 * m):,}",
                "运营费用": f"¥{int(1000 * m):,}-{int(3000 * m):,}",
            },
            "revenue": {
                "预计月销量": f"{int(300 * m):,}-{int(1500 * m):,}件",
                "预计月收入": f"¥{int(15000 * m):,}-{int(50000 * m):,}",
                "预计月利润": f"¥{int(5000 * m):,}-{int(20000 * m):,}",
            },
            "break_even": {
                "盈亏平衡销量": f"{int(180 * m)}件/月",
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

    async def _llm_selection_advice(self, category: str, region: str, budget: str,
                                    score: Dict[str, Any],
                                    products: List[Dict[str, Any]]) -> Any:
        """调用 LLM 生成选品策略建议；未配置 API Key 时返回 None（降级为纯规则结果）。"""
        if not llm_service.api_key:
            return None
        top = "、".join(p["product"] for p in products[:3]) or category
        prompt = (
            f"请针对以下义乌小商品跨境选品场景，给出3条可执行的选品策略建议（每条不超过60字，聚焦实操）：\n"
            f"品类：{category}\n目标区域：{region}\n预算等级：{budget}\n"
            f"综合评分：{score['total']}（{score['level']}）\n"
            f"维度分：市场需求{score['market_demand']}、利润潜力{score['profit_potential']}、"
            f"供应链稳定{score['supply_stability']}、竞争友好度{score['competition']}\n"
            f"热门推荐产品：{top}\n"
            f"请围绕差异化选品、定价区间与首批备货量给出专业建议。"
        )
        return await self.llm_generate(prompt, temperature=0.6, max_tokens=420)
