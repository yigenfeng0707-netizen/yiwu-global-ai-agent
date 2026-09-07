"""工作流编排测试 - LangGraph StateGraph 与顺序降级双路径"""

import pytest
from app.agents.workflow import (
    CrossBorderWorkflow, WorkflowState, LANGGRAPH_AVAILABLE,
)


@pytest.fixture
def workflow():
    return CrossBorderWorkflow()


class TestWorkflowGraph:
    def test_graph_engine_available(self):
        """LangGraph 已安装时应构建图，未安装时可降级"""
        wf = CrossBorderWorkflow()
        info = wf.get_graph_info()
        assert info["engine"] in ("langgraph", "sequential")
        if LANGGRAPH_AVAILABLE:
            assert info["engine"] == "langgraph"
            assert "summarize" in info["nodes"]
            assert info["conditional_edges"][0]["from"] == "content_generation"

    @pytest.mark.asyncio
    async def test_pipeline_with_target_country_runs_all_steps(self, workflow):
        """指定目标国家时执行全部7步（含合规查询）"""
        result = await workflow.run(WorkflowState(
            category="圣诞饰品", region="europe", target_country="德国",
        ))
        summary = result["summary"]
        assert summary["total_steps"] == 7
        assert summary["steps_completed"] == 7
        assert summary["errors"] == 0
        assert result["state"]["compliance"].get("status") == "success"

    @pytest.mark.asyncio
    async def test_pipeline_without_target_country_skips_compliance(self, workflow):
        """未指定目标国家时条件路由跳过合规查询"""
        result = await workflow.run(WorkflowState(
            category="圣诞饰品", region="europe",
        ))
        summary = result["summary"]
        assert summary["steps_completed"] == 6
        # 合规节点被跳过：结果为空
        assert not result["state"]["compliance"]

    @pytest.mark.asyncio
    async def test_pipeline_result_shape_compatible(self, workflow):
        """对 routes.py 的返回结构保持兼容：state + summary"""
        result = await workflow.run(WorkflowState(category="圣诞饰品"))
        assert "state" in result
        assert "summary" in result
        for key in ("total_steps", "steps_completed", "duration_seconds", "errors", "product"):
            assert key in result["summary"]

    @pytest.mark.asyncio
    async def test_sequential_fallback(self, workflow):
        """LangGraph 异常时降级为顺序执行，结果结构不变"""
        result = await workflow._run_sequential({
            "category": "圣诞饰品", "region": "europe",
            "budget": "中", "target_country": "德国",
            "platform": "amazon", "target_language": "en",
            "product_name": "", "errors": [],
        })
        assert result["summary"]["total_steps"] == 7
        assert result["market_insight"].get("status") == "success"

    def test_get_steps(self, workflow):
        steps = workflow.get_steps()
        assert len(steps) == 7
        assert steps[0] == {"key": "market_insight", "name": "市场洞察"}
