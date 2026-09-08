"""义乌小商品出海智能体 - 合规助手Agent（确定性关税 + LLM合规解读）"""

from typing import Any, Dict, List

from .base import BaseAgent
from ..data.market_data import CATEGORY_LIST
from ..services.llm import llm_service
from ..data.compliance_data import (
    COUNTRY_COMPLIANCE, CLEARANCE_DOCUMENTS, YIXINOU_TARIFF_BENEFITS,
    RCEP_TARIFF_BENEFITS, CATEGORY_SPECIAL_REQUIREMENTS, CERTIFICATION_PROCESS,
)


class ComplianceAgent(BaseAgent):
    """合规助手Agent - 认证查询、清关文件、合规检查、关税计算"""

    name = "compliance"
    description = "合规助手Agent - 认证查询、清关文件、合规检查、关税计算、义新欧班列优惠"

    async def execute(self, **kwargs) -> Dict[str, Any]:
        category = kwargs.get("category", CATEGORY_LIST[0])
        target_country = kwargs.get("target_country", "德国")

        # 认证要求
        certifications = self._get_certifications(category, target_country)

        # 清关文件
        clearance_documents = self._get_clearance_documents(target_country)

        # 合规检查
        compliance_checks = self._get_compliance_checks(category, target_country)

        # 特殊要求
        special_requirements = CATEGORY_SPECIAL_REQUIREMENTS.get(category, "")

        # 关税优惠
        tariff_benefits = self._get_tariff_benefits(target_country)

        overall_status = "pass" if all(c["status"] == "pass" for c in compliance_checks) else "attention_needed"

        result = self._wrap_response({
            "category": category,
            "target_country": target_country,
            "certifications": certifications,
            "clearance_documents": clearance_documents,
            "compliance_check": {
                "checks": compliance_checks,
                "overall_status": overall_status,
            },
            "special_requirements": special_requirements,
            "tariff_benefits": tariff_benefits,
        })

        # LLM 增强：生成合规风险提示与通关建议（无 API Key 时降级为纯规则结果）
        advice = await self._llm_compliance_advice(category, target_country, certifications, compliance_checks, overall_status)
        if advice:
            result["ai_compliance_advice"] = advice.strip()
            result["ai_used"] = True
        else:
            result["ai_used"] = False

        self.record_query({"category": category, "target_country": target_country}, f"合规判定:{overall_status}")
        return result

    async def calculate_tariff(self, category: str, target_country: str, product_value: float) -> Dict[str, Any]:
        """计算关税"""
        country_data = COUNTRY_COMPLIANCE.get(target_country, {})

        duty_range = country_data.get("import_duty_range", "5%-15%")
        # 确定性税率：取进口关税区间中值（原 random.uniform 会导致同商品关税每次不同）
        try:
            lo_s, hi_s = duty_range.split("-")
            lo_val = float(lo_s.replace("%", "").strip())
            hi_val = float(hi_s.replace("%", "").strip())
        except (ValueError, AttributeError):
            lo_val, hi_val = 5.0, 15.0
        duty_rate = (lo_val + hi_val) / 2 / 100
        duty_rate_note = f"按进口关税区间 {duty_range} 的中值估算，实际税率以海关核定为准"

        vat_str = country_data.get("vat_rate", "20%")
        vat_rate = float(vat_str.replace("%", "")) / 100

        tariff_amount = product_value * duty_rate
        vat_amount = (product_value + tariff_amount) * vat_rate
        import_tax = tariff_amount * 0.3
        total_tax = tariff_amount + vat_amount + import_tax
        total_cost = product_value + total_tax

        # 优惠信息
        benefits = None
        if "欧洲" in target_country or target_country in ["德国", "法国", "西班牙", "荷兰", "波兰"]:
            benefits = "义新欧班列通关便利化，可享受中欧双边协定优惠税率"
        elif target_country in ["哈萨克斯坦", "乌兹别克斯坦", "吉尔吉斯斯坦"]:
            benefits = "EAEU成员国间关税优惠，部分商品零关税"
        elif target_country in ["沙特阿拉伯", "阿联酋", "伊朗", "土耳其"]:
            benefits = "中东自贸区可享受免税仓储和转口贸易优惠"
        elif target_country in ["印尼", "泰国", "越南", "马来西亚"]:
            benefits = RCEP_TARIFF_BENEFITS["description"]

        return {
            "product_value": product_value,
            "tariff_rate": f"{duty_rate * 100:.1f}%",
            "tariff_rate_note": duty_rate_note,
            "tariff_amount": round(tariff_amount, 2),
            "vat_rate": f"{vat_rate * 100:.0f}%",
            "vat_amount": round(vat_amount, 2),
            "import_tax": round(import_tax, 2),
            "total_tax": round(total_tax, 2),
            "total_cost": round(total_cost, 2),
            "rcep_benefits": benefits,
        }

    def _get_certifications(self, category: str, target_country: str) -> List[Dict[str, Any]]:
        """获取认证要求"""
        country_data = COUNTRY_COMPLIANCE.get(target_country, {})
        cert_names = country_data.get("certifications", ["CE认证"])

        result = []
        for cert in cert_names:
            process = CERTIFICATION_PROCESS.get(cert, {})
            result.append({
                "name": cert,
                "required": True,
                "estimated_time": process.get("estimated_time", "4-8周"),
                "estimated_cost": process.get("estimated_cost", "¥5,000-30,000"),
            })
        return result

    def _get_clearance_documents(self, target_country: str) -> List[Dict[str, Any]]:
        """获取清关文件"""
        result = []
        for doc in CLEARANCE_DOCUMENTS:
            result.append({
                "name": doc["name"],
                "required": doc["required"],
                "description": doc["description"],
            })
        return result

    def _get_compliance_checks(self, category: str, target_country: str) -> List[Dict[str, Any]]:
        """获取合规检查"""
        checks = [
            {"item": "产品认证合规", "status": "pass", "risk_level": "low"},
            {"item": "标签语言要求", "status": "pass", "risk_level": "low"},
            {"item": "包装法规合规", "status": "attention", "risk_level": "medium"},
            {"item": "进口许可证", "status": "pass", "risk_level": "low"},
            {"item": "质量检测报告", "status": "pass", "risk_level": "low"},
        ]
        return checks

    def _get_tariff_benefits(self, target_country: str) -> Dict[str, Any]:
        """获取关税优惠"""
        if target_country in ["德国", "法国", "西班牙", "荷兰", "波兰"]:
            return YIXINOU_TARIFF_BENEFITS
        elif target_country in ["印尼", "泰国", "越南", "马来西亚"]:
            return RCEP_TARIFF_BENEFITS
        else:
            return {
                "description": f"出口至{target_country}可享受双边贸易协定优惠",
                "benefits": ["双边贸易协定优惠税率", "义乌市场采购贸易1039模式简化申报"],
            }

    async def _llm_compliance_advice(self, category: str, target_country: str,
                                     certifications: List[Dict[str, Any]],
                                     checks: List[Dict[str, Any]],
                                     overall_status: str) -> Any:
        """调用 LLM 生成合规风险提示与通关建议；未配置 API Key 时返回 None（降级为纯规则结果）。"""
        if not llm_service.api_key:
            return None
        certs = "、".join(c["name"] for c in certifications) or "目标市场常规认证"
        attention = [c["item"] for c in checks if c.get("status") != "pass"]
        attention_txt = "、".join(attention) if attention else "无"
        prompt = (
            f"请针对以下义乌小商品出口合规场景，给出3条合规风险提示与通关建议（每条不超过60字，聚焦可执行动作）：\n"
            f"出口品类：{category}\n目标国家：{target_country}\n"
            f"所需认证：{certs}\n合规检查总体判定：{overall_status}\n需重点关注项：{attention_txt}\n"
            f"请结合 1039 市场采购贸易模式与目标国准入要求给出专业建议。"
        )
        return await self.llm_generate(
            prompt,
            system_prompt="你是资深跨境贸易合规顾问，精通各国进口准入、认证与 1039 市场采购贸易政策，回答专业、简洁、可执行。",
            temperature=0.4, max_tokens=420,
        )
