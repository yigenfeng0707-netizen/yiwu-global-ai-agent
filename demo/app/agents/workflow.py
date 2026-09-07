"""义乌小商品出海智能体 - 工作流模块（LangGraph编排）"""

import logging
import time
from typing import Any, Dict, List, Optional, TypedDict
from dataclasses import dataclass, field

from .base import BaseAgent
from .market_insight import MarketInsightAgent
from .smart_selection import SmartSelectionAgent
from .content_generation import ContentGenerationAgent
from .compliance_agent import ComplianceAgent
from .customer_service_agent import CustomerServiceAgent
from .supply_chain_agent import SupplyChainAgent
from .policy_replication_agent import PolicyReplicationAgent

logger = logging.getLogger(__name__)

try:
    from langgraph.graph import StateGraph, START, END
    LANGGRAPH_AVAILABLE = True
except ImportError:  # 优雅降级：无LangGraph时退化为顺序执行
    LANGGRAPH_AVAILABLE = False


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


class GraphState(TypedDict, total=False):
    """LangGraph共享状态 - 各节点读写"""
    # 输入参数
    category: str
    region: str
    budget: str
    target_country: str
    platform: str
    target_language: str
    product_name: str
    # 节点结果（key与STEPS一致）
    market_insight: Dict[str, Any]
    smart_selection: Dict[str, Any]
    supply_chain: Dict[str, Any]
    content_generation: Dict[str, Any]
    compliance: Dict[str, Any]
    customer_service: Dict[str, Any]
    policy_replication: Dict[str, Any]
    # 元数据
    errors: List[Dict[str, str]]
    summary: Dict[str, Any]


class CrossBorderWorkflow:
    """跨境出海全链路工作流 - LangGraph StateGraph编排，7个Agent节点 + 条件路由"""

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
        self._graph = self._build_graph() if LANGGRAPH_AVAILABLE else None

    # ==================== 节点定义 ====================

    def _node_kwargs(self, key: str, state: GraphState) -> Dict[str, Any]:
        """构建各Agent节点所需的调用参数"""
        kwargs = {
            "category": state.get("category", ""),
            "region": state.get("region", ""),
            "budget": state.get("budget", "中"),
        }
        if key == "content_generation":
            kwargs["product_name"] = state.get("product_name") or state.get("category", "")
            kwargs["platform"] = state.get("platform", "amazon")
            kwargs["target_language"] = state.get("target_language", "en")
        elif key == "compliance":
            kwargs["target_country"] = state.get("target_country", "")
        elif key == "customer_service":
            kwargs["message"] = (
                f"我想了解{state.get('category', '')}出口到"
                f"{state.get('target_country') or state.get('region', '')}的流程"
            )
            kwargs["language"] = "zh"
            kwargs["session_id"] = f"pipeline_{int(time.time())}"
        elif key == "policy_replication":
            kwargs["action"] = "overview"
        return kwargs

    async def _run_agent_node(self, key: str, state: GraphState) -> Dict[str, Any]:
        """通用Agent节点：执行Agent并容错（单节点失败不阻断全链路）"""
        agent = self.agents[key]
        try:
            result = await agent.execute(**self._node_kwargs(key, state))
            return {key: result}
        except Exception as e:
            logger.warning("工作流节点 %s 执行失败: %s", key, e)
            errors = list(state.get("errors", []))
            errors.append({"step": key, "error": str(e)})
            return {
                key: {"agent": key, "status": "error", "error": str(e)},
                "errors": errors,
            }

    async def _summarize(self, state: GraphState) -> Dict[str, Any]:
        """汇总节点：统计完成度"""
        step_keys = [s["key"] for s in self.STEPS]
        completed = sum(
            1 for k in step_keys
            if state.get(k, {}).get("status") == "success"
        )
        summary = {
            "total_steps": len(step_keys),
            "steps_completed": completed,
            "errors": len(state.get("errors", [])),
            "product": state.get("category", ""),
            "engine": "langgraph" if LANGGRAPH_AVAILABLE else "sequential",
        }
        return {"summary": summary}

    def _route_after_content(self, state: GraphState) -> str:
        """条件路由：指定了目标国家才执行合规查询，否则跳过直达客服"""
        if state.get("target_country"):
            return "compliance"
        return "customer_service"

    # ==================== 图构建 ====================

    def _build_graph(self):
        """
        构建编排图：

            START → 市场洞察 → 智能选品 → 供应链 → 内容生成
                  → (有目标国家? 合规查询 : 跳过) → 智能客服 → 政策复制 → 汇总 → END
        """
        builder = StateGraph(GraphState)

        def make_node(key: str):
            async def node(state: GraphState) -> Dict[str, Any]:
                return await self._run_agent_node(key, state)
            return node

        for step in self.STEPS:
            builder.add_node(step["key"], make_node(step["key"]))
        builder.add_node("summarize", self._summarize)

        builder.add_edge(START, "market_insight")
        builder.add_edge("market_insight", "smart_selection")
        builder.add_edge("smart_selection", "supply_chain")
        builder.add_edge("supply_chain", "content_generation")
        builder.add_conditional_edges(
            "content_generation",
            self._route_after_content,
            {"compliance": "compliance", "customer_service": "customer_service"},
        )
        builder.add_edge("compliance", "customer_service")
        builder.add_edge("customer_service", "policy_replication")
        builder.add_edge("policy_replication", "summarize")
        builder.add_edge("summarize", END)

        return builder.compile()

    # ==================== 对外入口 ====================

    async def run(self, state: WorkflowState) -> Dict[str, Any]:
        """执行全链路工作流（LangGraph优先，未安装时顺序降级）"""
        start_time = time.time()

        init_state: GraphState = {
            "category": state.category,
            "region": state.region,
            "budget": state.budget,
            "target_country": state.target_country,
            "platform": state.platform,
            "target_language": state.target_language,
            "product_name": state.product_name,
            "errors": [],
        }

        if self._graph is not None:
            try:
                final = await self._graph.ainvoke(init_state)
            except Exception as e:
                logger.warning("LangGraph执行异常，降级为顺序执行: %s", e)
                final = await self._run_sequential(init_state)
        else:
            final = await self._run_sequential(init_state)

        summary = dict(final.get("summary", {}))
        summary["duration_seconds"] = round(time.time() - start_time, 2)

        step_results = {k: final.get(k, {}) for k in (s["key"] for s in self.STEPS)}
        return {"state": step_results, "summary": summary}

    async def _run_sequential(self, init_state: GraphState) -> Dict[str, Any]:
        """顺序降级执行：LangGraph不可用或执行异常时兜底"""
        state = dict(init_state)
        for step in self.STEPS:
            if step["key"] == "compliance" and not self._route_after_content(state) == "compliance":
                continue
            state.update(await self._run_agent_node(step["key"], state))
        state.update(await self._summarize(state))
        return state

    def get_steps(self) -> list:
        """获取工作流步骤"""
        return [{"key": s["key"], "name": s["name"]} for s in self.STEPS]

    def get_graph_info(self) -> Dict[str, Any]:
        """获取编排图信息（供技术展示/健康检查）"""
        return {
            "engine": "langgraph" if LANGGRAPH_AVAILABLE else "sequential",
            "nodes": [s["key"] for s in self.STEPS] + ["summarize"],
            "conditional_edges": [
                {"from": "content_generation", "router": "_route_after_content",
                 "routes": {"compliance": "指定目标国家", "customer_service": "未指定则跳过合规"}},
            ],
        }
