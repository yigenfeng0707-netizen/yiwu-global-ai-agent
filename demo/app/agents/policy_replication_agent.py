"""义乌小商品出海智能体 - 政策复制Agent"""

from typing import Any, Dict, List, Optional

from .base import BaseAgent
from ..knowledge.remio_kb import remio_kb
from ..data.policy_data import (
    CITY_1039_DATA, POLICY_1039_DETAIL, YIWU_SUCCESS_CASES,
    POLICY_BENEFIT_PARAMS,
)


class PolicyReplicationAgent(BaseAgent):
    """政策复制Agent - 1039市场采购贸易政策解读、39城复制推广、政策红利计算、义乌案例本地化"""

    name = "policy_replication"
    description = "政策复制Agent - 1039市场采购贸易政策解读、39城复制推广信息查询、政策红利计算器、义乌成功案例本地化适配"

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """执行政策复制Agent任务"""
        action = kwargs.get("action", "overview")

        if action == "policy_guide":
            return await self.get_policy_guide()
        elif action == "city_info":
            city_name = kwargs.get("city_name", "")
            return await self.get_city_info(city_name)
        elif action == "calculate_benefit":
            return await self.calculate_policy_benefit(
                annual_export=kwargs.get("annual_export", 1000000),
                category=kwargs.get("category", "日用百货"),
                city=kwargs.get("city", "义乌"),
            )
        elif action == "localized_case":
            return await self.get_localized_case(
                case_id=kwargs.get("case_id", 1),
                target_city=kwargs.get("target_city", ""),
            )
        else:
            # 默认返回概览
            remio_ctx = remio_kb.context_for("1039市场采购贸易 政策 红利 复制推广")
            knowledge_source = "remio 睿妙知识库 + 内置数据" if remio_ctx else "内置数据"
            return self._wrap_response({
                "total_cities": len(CITY_1039_DATA),
                "policy_name": POLICY_1039_DETAIL["policy_name"],
                "policy_code": POLICY_1039_DETAIL["policy_code"],
                "key_benefits": [p["title"] for p in POLICY_1039_DETAIL["key_points"][:3]],
                "cases_count": len(YIWU_SUCCESS_CASES),
                "knowledge_source": knowledge_source,
                "remio_knowledge": remio_ctx,
            })

    async def get_policy_guide(self) -> Dict[str, Any]:
        """1039市场采购贸易政策解读"""
        return self._wrap_response({
            "policy_name": POLICY_1039_DETAIL["policy_name"],
            "policy_code": POLICY_1039_DETAIL["policy_code"],
            "background": POLICY_1039_DETAIL["background"],
            "key_points": POLICY_1039_DETAIL["key_points"],
            "applicable_conditions": POLICY_1039_DETAIL["applicable_conditions"],
            "operation_process": POLICY_1039_DETAIL["operation_process"],
            "tax_benefits": POLICY_1039_DETAIL["tax_benefits"],
        })

    async def get_city_info(self, city_name: str = "") -> Dict[str, Any]:
        """39城复制推广信息查询"""
        if city_name:
            # 查询指定城市
            for city in CITY_1039_DATA:
                if city["city"] == city_name:
                    return self._wrap_response({
                        "city": city,
                        "policy_detail": {
                            "applicable": True,
                            "max_value_per_shipment": f"${POLICY_BENEFIT_PARAMS['max_value_per_shipment']:,}",
                            "vat_exemption": True,
                            "simplified_declaration": True,
                        },
                    })
            return self._wrap_response({
                "city": None,
                "message": f"未找到城市'{city_name}'的1039试点信息，请确认城市名称是否正确",
            })
        else:
            # 返回所有城市列表
            return self._wrap_response({
                "total": len(CITY_1039_DATA),
                "cities": CITY_1039_DATA,
            })

    async def calculate_policy_benefit(
        self,
        annual_export: float = 1000000,
        category: str = "日用百货",
        city: str = "义乌",
    ) -> Dict[str, Any]:
        """政策红利计算器 - 计算税收优惠、通关便利等"""
        params = POLICY_BENEFIT_PARAMS

        # 增值税免征优惠
        vat_saving = annual_export * params["vat_rate"]

        # 所得税优惠（核定征收 vs 查账征收）
        # 假设利润率10%
        profit_rate = 0.10
        profit = annual_export * profit_rate
        # 查账征收所得税
        general_income_tax = profit * 0.25
        # 核定征收所得税
        market_purchase_income_tax = annual_export * params["income_tax_rate"] * params["income_tax_bracket"]
        income_tax_saving = general_income_tax - market_purchase_income_tax

        # 合规成本节省
        general_compliance_cost = annual_export * params["general_trade_compliance_cost_rate"]
        market_purchase_compliance_cost = annual_export * params["market_purchase_compliance_cost_rate"]
        compliance_cost_saving = general_compliance_cost - market_purchase_compliance_cost

        # 通关时间节省
        clearance_time_saving = params["clearance_time_general"] - params["clearance_time_1039"]

        # 物流成本节省（组柜拼箱）
        logistics_saving = annual_export * params["logistics_saving_rate"] * 0.3  # 假设30%货物适用组柜

        # 总节省
        total_saving = vat_saving + income_tax_saving + compliance_cost_saving + logistics_saving

        # 查找城市信息
        city_info = None
        for c in CITY_1039_DATA:
            if c["city"] == city:
                city_info = c
                break

        return self._wrap_response({
            "annual_export": annual_export,
            "category": category,
            "city": city,
            "city_info": city_info,
            "benefits": {
                "vat_saving": {
                    "description": "增值税免征优惠",
                    "amount": round(vat_saving, 2),
                    "detail": f"出口额${annual_export:,.0f} × 增值税率{params['vat_rate']*100:.0f}% = ${vat_saving:,.2f}",
                },
                "income_tax_saving": {
                    "description": "所得税优惠（核定征收）",
                    "amount": round(income_tax_saving, 2),
                    "detail": f"查账征收${general_income_tax:,.2f} - 核定征收${market_purchase_income_tax:,.2f} = ${income_tax_saving:,.2f}",
                },
                "compliance_cost_saving": {
                    "description": "合规成本节省",
                    "amount": round(compliance_cost_saving, 2),
                    "detail": f"一般贸易${general_compliance_cost:,.2f} - 1039模式${market_purchase_compliance_cost:,.2f} = ${compliance_cost_saving:,.2f}",
                },
                "logistics_saving": {
                    "description": "组柜拼箱物流节省",
                    "amount": round(logistics_saving, 2),
                    "detail": f"部分货物适用组柜拼箱，节省约{params['logistics_saving_rate']*100:.0f}%",
                },
                "clearance_time_saving": {
                    "description": "通关时间节省",
                    "amount": clearance_time_saving,
                    "detail": f"一般贸易{params['clearance_time_general']}天 → 1039模式{params['clearance_time_1039']}天，节省{clearance_time_saving}天",
                },
            },
            "total_saving": round(total_saving, 2),
            "saving_rate": f"{total_saving / annual_export * 100:.1f}%" if annual_export > 0 else "0%",
            "compared_to_general_trade": {
                "general_trade_total_cost": round(annual_export * 0.20, 2),  # 一般贸易综合成本约20%
                "market_purchase_total_cost": round(annual_export * 0.20 - total_saving, 2),
                "cost_reduction": f"{total_saving / (annual_export * 0.20) * 100:.1f}%" if annual_export > 0 else "0%",
            },
        })

    async def get_localized_case(self, case_id: int = 1, target_city: str = "") -> Dict[str, Any]:
        """义乌成功案例本地化适配"""
        # 查找案例
        case = None
        for c in YIWU_SUCCESS_CASES:
            if c["case_id"] == case_id:
                case = c
                break

        if not case:
            return self._wrap_response({
                "case": None,
                "message": f"未找到案例ID={case_id}",
            })

        # 查找目标城市信息
        target_city_info = None
        for city in CITY_1039_DATA:
            if city["city"] == target_city:
                target_city_info = city
                break

        # 本地化适配建议
        localization_advice = []
        if target_city_info:
            # 基于目标城市品类匹配
            case_categories = case["category"]
            city_categories = target_city_info["main_categories"]
            category_match = any(cat in city_categories for cat in case_categories.split("、") if cat in city_categories)

            if category_match:
                localization_advice.append({
                    "type": "品类匹配",
                    "level": "高",
                    "advice": f"目标城市{target_city}的主要品类（{city_categories}）与案例品类（{case_categories}）高度匹配，可直接复制核心策略",
                })
            else:
                localization_advice.append({
                    "type": "品类适配",
                    "level": "中",
                    "advice": f"目标城市{target_city}的主要品类为{city_categories}，需将案例中的{case_categories}策略适配到当地优势品类",
                })

            # 基于省份的物流建议
            province = target_city_info["province"]
            if province in ["浙江", "福建", "广东"]:
                localization_advice.append({
                    "type": "物流优势",
                    "level": "高",
                    "advice": f"{province}沿海省份，海运便利，可叠加海运+1039模式，物流成本更低",
                })
            elif province in ["四川", "重庆", "陕西", "河南", "湖北", "湖南"]:
                localization_advice.append({
                    "type": "物流建议",
                    "level": "中",
                    "advice": f"可利用中欧班列（{province}出发）+1039模式，实现铁路直达欧洲",
                })
            else:
                localization_advice.append({
                    "type": "物流建议",
                    "level": "中",
                    "advice": f"建议结合当地物流资源，探索多式联运+1039模式",
                })

            # 政策叠加建议
            localization_advice.append({
                "type": "政策叠加",
                "level": "高",
                "advice": f"建议叠加{target_city}的本地优惠政策（{target_city_info['policy_benefits']}）与1039国家政策，实现双红利",
            })
        else:
            localization_advice.append({
                "type": "通用建议",
                "level": "中",
                "advice": "请指定目标城市以获取更精准的本地化适配建议",
            })

        return self._wrap_response({
            "case": case,
            "target_city": target_city_info,
            "localization_advice": localization_advice,
            "replication_checklist": [
                "确认目标城市已获批1039市场采购贸易试点",
                "在市场采购贸易综合管理系统完成备案登记",
                "了解目标城市主要品类与案例品类的匹配度",
                "评估目标城市物流通道（海运/铁路/空运）",
                "叠加本地优惠政策与1039国家政策",
                "建立本地化供应链和分销网络",
            ],
        })
