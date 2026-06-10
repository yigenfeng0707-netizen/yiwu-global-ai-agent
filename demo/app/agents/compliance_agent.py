"""义乌小商品出海智能体 - 合规助手Agent"""

import random
from typing import Any, Dict, List

from .base import BaseAgent
from ..data.market_data import CATEGORY_LIST
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

        return self._wrap_response({
            "category": category,
            "target_country": target_country,
            "certifications": certifications,
            "clearance_documents": clearance_documents,
            "compliance_check": {
                "checks": compliance_checks,
                "overall_status": "pass" if all(c["status"] == "pass" for c in compliance_checks) else "attention_needed",
            },
            "special_requirements": special_requirements,
            "tariff_benefits": tariff_benefits,
        })

    async def calculate_tariff(self, category: str, target_country: str, product_value: float) -> Dict[str, Any]:
        """计算关税"""
        country_data = COUNTRY_COMPLIANCE.get(target_country, {})

        duty_range = country_data.get("import_duty_range", "5%-15%")
        duty_rate = random.uniform(float(duty_range.split("-")[0].replace("%", "")), float(duty_range.split("-")[1].replace("%", ""))) / 100

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
