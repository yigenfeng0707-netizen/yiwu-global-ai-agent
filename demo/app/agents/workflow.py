"""义乌小商品出海智能体 - 工作流模块"""

import time
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

from .base import BaseAgent
from .market_insight import MarketInsightAgent
from .smart_selection import SmartSelectionAgent
from .content_generation import ContentGenerationAgent
from .compliance_agent import ComplianceAgent
from .customer_service_agent import CustomerServiceAgent
from .supply_chain_agent import SupplyChainAgent
from .policy_replication_agent import PolicyReplicationAgent


@dataclass
class WorkflowState:
    """工作流状态"""
    category: str = ""
    region: str = ""
    budget: str = "中"
    target_country: str = ""
    platform: str = "amazon"
    target_language: str = "en"
    product_name: str = ""

    # 各步骤结果
    market_insight: Dict[str, Any] = field(default_factory=dict)
    smart_selection: Dict[str, Any] = field(default_factory=dict)
    content_generation: Dict[str, Any] = field(default_factory=dict)
    compliance: Dict[str, Any] = field(default_factory=dict)
    customer_service: Dict[str, Any] = field(default_factory=dict)
    supply_chain: Dict[str, Any] = field(default_factory=dict)
    policy_replication: Dict[str, Any] = field(default_factory=dict)

    # 元数据
    current_step: str = "market_insight"
    errors: list = field(default_factory=list)


class CrossBorderWorkflow:
    """跨境出海全链路工作流 - 7步流程"""

    STEPS = [
        {"key": "market_insight", "name": "市场洞察", "agent_class": MarketInsightAgent},
        {"key": "smart_selection", "name": "智能选品", "agent_class": SmartSelectionAgent},
        {"key": "supply_chain", "name": "供应链匹配", "agent_class": SupplyChainAgent},
        {"key": "content_generation", "name": "内容生成", "agent_class": ContentGenerationAgent},
        {"key": "compliance", "name": "合规查询", "agent_class": ComplianceAgent},
        {"key": "customer_service", "name": "智能客服", "agent_class": CustomerServiceAgent},
        {"key": "policy_replication", "name": "政策复制", "agent_class": PolicyReplicationAgent},
    ]

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        for step in self.STEPS:
            self.agents[step["key"]] = step["agent_class"]()

    async def run(self, state: WorkflowState) -> Dict[str, Any]:
        """执行全链路工作流"""
        start_time = time.time()
        step_results = {}

        for step in self.STEPS:
            key = step["key"]
            agent = self.agents[key]
            state.current_step = key

            try:
                kwargs = {
                    "category": state.category,
                    "region": state.region,
                    "budget": state.budget,
                }

                # 各步骤特有参数
                if key == "smart_selection":
                    kwargs["budget"] = state.budget
                elif key == "content_generation":
                    kwargs["product_name"] = state.product_name or state.category
                    kwargs["platform"] = state.platform
                    kwargs["target_language"] = state.target_language
                elif key == "compliance":
                    kwargs["target_country"] = state.target_country
                elif key == "customer_service":
                    kwargs["message"] = f"我想了解{state.category}出口到{state.target_country}的流程"
                    kwargs["language"] = "zh"
                    kwargs["session_id"] = f"pipeline_{int(time.time())}"
                elif key == "supply_chain":
                    kwargs["region"] = state.region
                elif key == "policy_replication":
                    kwargs["action"] = "overview"
                    kwargs["category"] = state.category

                result = await agent.execute(**kwargs)
                step_results[key] = result

                # 更新state
                setattr(state, key, result)

            except Exception as e:
                state.errors.append({"step": key, "error": str(e)})
                step_results[key] = {"agent": key, "status": "error", "error": str(e)}

        duration = time.time() - start_time
        completed_steps = sum(1 for v in step_results.values() if v.get("status") == "success")

        return {
            "state": step_results,
            "summary": {
                "total_steps": len(self.STEPS),
                "steps_completed": completed_steps,
                "duration_seconds": round(duration, 2),
                "errors": len(state.errors),
                "product": state.category,
            },
        }

    def get_steps(self) -> list:
        """获取工作流步骤"""
        return [{"key": s["key"], "name": s["name"]} for s in self.STEPS]
