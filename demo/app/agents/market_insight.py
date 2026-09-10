"""义乌小商品出海智能体 - 市场洞察Agent"""

from typing import Any, Dict, List

from .base import BaseAgent
from ..data.market_data import MARKET_DATA, CATEGORY_LIST, SUPPORTED_REGIONS, YIWU_INDEX
from ..data.sources import DataSourceManager
from ..data.etl import get_registry


class MarketInsightAgent(BaseAgent):
    """市场洞察Agent - 基于义乌指数和市场数据，LLM增强洞察"""

    name = "market_insight"
    description = "市场洞察Agent - 义乌指数、市场规模、趋势分析、竞争格局"

    LLM_SYSTEM_PROMPT = (
        "你是义乌小商品城市场分析师，专精全球市场趋势分析、义乌指数解读、"
        "跨境电商市场洞察。给出简洁专业的商业建议。"
    )

    def __init__(self):
        super().__init__()
        self.data_manager = DataSourceManager()

    async def execute(self, **kwargs) -> Dict[str, Any]:
        category = kwargs.get("category", CATEGORY_LIST[0])
        region = kwargs.get("region", SUPPORTED_REGIONS[0])

        market_data = MARKET_DATA.get(category, {})

        # 市场规模
        market_size = market_data.get("market_size", "N/A")
        market_growth = market_data.get("growth_rate", "N/A")

        # 热门品类
        hot_categories = self._get_hot_categories(category)

        # 趋势分析
        trends = self._get_trends(category, region)

        # 价格区间
        price_tiers = self._get_price_tiers(category)

        # 竞争格局
        competitors = self._get_competitors(category, region)

        # 推荐产品
        recommendations = self._get_recommendations(category, region)

        # 风险预警
        risks = self._get_risks(category, region)

        # 义乌指数（P1-1：演示基准 + 官方发布真实值 + 实时汇率，均带溯源）
        reg = get_registry()
        official = reg.get_index_for_category(category)
        fx = reg.get_exchange_rate("CNY")
        yiwu_index = {
            # 演示基准（向后兼容前端旧字段）
            "current": YIWU_INDEX["current"],
            "change": YIWU_INDEX["change"],
            "trend": YIWU_INDEX["trend"],
            "category_score": YIWU_INDEX["categories"].get(category, 100),
            "demo_scale": "演示基准(98-110)，非实时",
            # 真实官方发布值（千点基准·定期更新）
            "is_real": bool(official.get("is_real")),
            "official": official,
            # 实时汇率（每日参考汇率）
            "exchange_rate": fx,
        }

        # 数据源
        data_sources = self.data_manager.fetch_all(category, region)
        source_names = [s.get("source", "") for s in data_sources]

        result = self._wrap_response(
            {
                "category": category,
                "region": region,
                "market_size": market_size,
                "market_growth": market_growth,
                "hot_categories": hot_categories,
                "trends": trends,
                "price_tiers": price_tiers,
                "competitors": competitors,
                "recommendations": recommendations,
                "risks": risks,
                "yiwu_index": yiwu_index,
                "data_sources": source_names,
            }
        )

        # 记录查询
        self.record_query({"category": category, "region": region})

        # LLM增强：添加AI洞察
        result = await self.llm_enhance(
            result,
            context=f"品类:{category}, 区域:{region}, 市场规模:{market_size}, 增长率:{market_growth}, 义乌指数:{yiwu_index['current']}",
        )
        return result

    # 确定性阶梯（按序号取模，同输入同输出）
    _SHARE_LADDER = [32, 28, 22, 18, 15]
    _GROWTH_LADDER = [23, 18, 15, 10, 7]
    _COMPETITOR_SHARE = [35, 22, 18, 12]
    _RATING_LADDER = [9.2, 8.7, 8.3, 7.8]
    _SALES_LADDER = [8500, 6200, 4100, 2800]

    def _get_hot_categories(self, category: str) -> List[Dict[str, Any]]:
        """获取热门品类"""
        market_data = MARKET_DATA.get(category, {})
        hot_products = market_data.get("hot_products", [])

        result = []
        for i, product in enumerate(hot_products):
            idx = i % len(self._SHARE_LADDER)
            result.append(
                {
                    "name": product,
                    "share": f"{self._SHARE_LADDER[idx]}%",
                    "growth": f"+{self._GROWTH_LADDER[idx]}%",
                }
            )
        return result

    def _get_trends(self, category: str, region: str) -> List[Dict[str, Any]]:
        """获取趋势分析"""
        trend_templates = [
            {
                "description": f"{category}在{region}市场需求持续增长，义乌指数显示上涨趋势",
                "impact": "high",
            },
            {
                "description": f"义新欧班列直达带动{category}出口{region}物流成本下降15%",
                "impact": "high",
            },
            {
                "description": f"1039市场采购贸易模式简化了{category}出口流程",
                "impact": "medium",
            },
            {
                "description": f"{region}消费者对{category}品质要求提升，需关注认证合规",
                "impact": "medium",
            },
            {
                "description": f"义乌{category}新品更新速度加快，紧跟市场潮流",
                "impact": "low",
            },
        ]
        return trend_templates[:4]

    def _get_price_tiers(self, category: str) -> List[Dict[str, Any]]:
        """获取价格区间"""
        market_data = MARKET_DATA.get(category, {})
        avg_price = market_data.get("avg_price_range", "$1-20")

        return [
            {
                "tier": "低端",
                "price_range": avg_price.split("-")[0]
                + "-"
                + str(round(float(avg_price.split("-")[0].replace("$", "")) * 2, 1)),
                "volume_share": "42%",
            },
            {"tier": "中端", "price_range": avg_price, "volume_share": "35%"},
            {
                "tier": "高端",
                "price_range": str(
                    round(float(avg_price.split("-")[-1].replace("$", "")) * 0.8, 1)
                )
                + "-"
                + str(round(float(avg_price.split("-")[-1].replace("$", "")) * 2, 1)),
                "volume_share": "23%",
            },
        ]

    def _get_competitors(self, category: str, region: str) -> List[Dict[str, Any]]:
        """获取竞争格局"""
        competitors = [
            {
                "name": "义乌本地供应商",
                "market_share": f"{self._COMPETITOR_SHARE[0]}%",
                "strength": "价格优势、品类齐全、供应链成熟",
            },
            {
                "name": "广东供应商",
                "market_share": f"{self._COMPETITOR_SHARE[1]}%",
                "strength": "电子电器类优势明显",
            },
            {
                "name": "东南亚本地品牌",
                "market_share": f"{self._COMPETITOR_SHARE[2]}%",
                "strength": "本地化优势、物流便捷",
            },
            {
                "name": "欧美品牌",
                "market_share": f"{self._COMPETITOR_SHARE[3]}%",
                "strength": "品牌溢价、品质认知",
            },
        ]
        return competitors

    def _get_recommendations(self, category: str, region: str) -> List[Dict[str, Any]]:
        """获取推荐产品"""
        market_data = MARKET_DATA.get(category, {})
        hot_products = market_data.get("hot_products", [])

        result = []
        for i, product in enumerate(hot_products[:4]):
            idx = i % len(self._RATING_LADDER)
            result.append(
                {
                    "product": product,
                    "rating": self._RATING_LADDER[idx],
                    "reason": f"义乌直供，价格优势明显，{region}市场需求旺盛",
                    "predicted_sales": f"{self._SALES_LADDER[idx]}件/月",
                }
            )
        return result

    def _get_risks(self, category: str, region: str) -> List[Dict[str, Any]]:
        """获取风险预警"""
        risks = [
            {
                "description": f"{region}认证要求可能变更，需持续关注",
                "level": "medium",
                "mitigation": "关注目标市场法规动态，提前做好认证规划",
            },
            {
                "description": "汇率波动可能影响利润",
                "level": "medium",
                "mitigation": "建议使用人民币结算，1039模式支持人民币收汇",
            },
            {
                "description": f"{category}同质化竞争加剧",
                "level": "low",
                "mitigation": "差异化选品，关注义乌新品趋势",
            },
        ]
        return risks
