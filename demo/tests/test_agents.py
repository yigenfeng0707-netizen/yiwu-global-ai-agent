"""测试Agent模块"""

import pytest
import asyncio
from app.agents.market_insight import MarketInsightAgent
from app.agents.smart_selection import SmartSelectionAgent
from app.agents.supply_chain_agent import SupplyChainAgent
from app.agents.content_generation import ContentGenerationAgent
from app.agents.compliance_agent import ComplianceAgent
from app.agents.customer_service_agent import CustomerServiceAgent
from app.agents.policy_replication_agent import PolicyReplicationAgent
from app.agents.workflow import CrossBorderWorkflow, WorkflowState


# ==================== 市场洞察Agent ====================

class TestMarketInsightAgent:
    def setup_method(self):
        self.agent = MarketInsightAgent()

    @pytest.mark.asyncio
    async def test_execute_default(self):
        result = await self.agent.execute()
        assert result["status"] == "success"
        assert result["agent"] == "market_insight"
        assert "category" in result
        assert "region" in result
        assert "hot_categories" in result
        assert "trends" in result
        assert "risks" in result
        assert "yiwu_index" in result

    @pytest.mark.asyncio
    async def test_execute_with_params(self):
        result = await self.agent.execute(category="玩具", region="东南亚")
        assert result["category"] == "玩具"
        assert result["region"] == "东南亚"
        assert len(result["hot_categories"]) > 0
        assert len(result["trends"]) > 0

    @pytest.mark.asyncio
    async def test_yiwu_index_present(self):
        result = await self.agent.execute()
        yiwu = result["yiwu_index"]
        assert "current" in yiwu
        assert "change" in yiwu
        assert "trend" in yiwu
        assert "category_score" in yiwu

    def test_agent_info(self):
        info = self.agent.info()
        assert info["name"] == "market_insight"
        assert len(info["description"]) > 0


# ==================== 智能选品Agent ====================

class TestSmartSelectionAgent:
    def setup_method(self):
        self.agent = SmartSelectionAgent()

    @pytest.mark.asyncio
    async def test_execute_default(self):
        result = await self.agent.execute()
        assert result["status"] == "success"
        assert "overall_score" in result
        assert "product_recommendations" in result
        assert "profit_analysis" in result
        assert "action_plan" in result

    @pytest.mark.asyncio
    async def test_score_range(self):
        result = await self.agent.execute(category="日用百货")
        score = result["overall_score"]["total"]
        assert 0 <= score <= 100

    @pytest.mark.asyncio
    async def test_budget_affects_analysis(self):
        low = await self.agent.execute(budget="低")
        high = await self.agent.execute(budget="高")
        assert low["budget"] == "低"
        assert high["budget"] == "高"


# ==================== 供应链匹配Agent ====================

class TestSupplyChainAgent:
    def setup_method(self):
        self.agent = SupplyChainAgent()

    @pytest.mark.asyncio
    async def test_execute_default(self):
        result = await self.agent.execute()
        assert result["status"] == "success"
        assert "suppliers" in result
        assert "logistics" in result
        assert "trade_1039" in result
        assert "supply_score" in result

    @pytest.mark.asyncio
    async def test_suppliers_have_required_fields(self):
        result = await self.agent.execute(category="玩具")
        for supplier in result["suppliers"]:
            assert "supplier" in supplier
            assert "product" in supplier
            assert "moq" in supplier
            assert "rating" in supplier

    @pytest.mark.asyncio
    async def test_district_mapping(self):
        result = await self.agent.execute(category="玩具")
        assert result["yiwu_trade_city"]["district"] == "一区"


# ==================== 内容生成Agent ====================

class TestContentGenerationAgent:
    def setup_method(self):
        self.agent = ContentGenerationAgent()

    @pytest.mark.asyncio
    async def test_execute_default(self):
        result = await self.agent.execute()
        assert result["status"] == "success"
        assert "content" in result
        assert "marketing" in result
        assert "platform_compliance" in result

    @pytest.mark.asyncio
    async def test_execute_with_product(self):
        result = await self.agent.execute(
            product_name="USB小风扇",
            category="电子电器",
            platform="amazon",
            target_language="en",
        )
        assert result["product_name"] == "USB小风扇"
        assert result["category"] == "电子电器"
        assert "title" in result["content"]
        assert "seo_keywords" in result["content"]

    @pytest.mark.asyncio
    async def test_platform_warnings(self):
        result = await self.agent.execute(platform="amazon")
        assert len(result["platform_compliance"]["warnings"]) > 0


# ==================== 合规助手Agent ====================

class TestComplianceAgent:
    def setup_method(self):
        self.agent = ComplianceAgent()

    @pytest.mark.asyncio
    async def test_execute_default(self):
        result = await self.agent.execute()
        assert result["status"] == "success"
        assert "certifications" in result
        assert "clearance_documents" in result
        assert "compliance_check" in result

    @pytest.mark.asyncio
    async def test_tariff_calculation(self):
        result = await self.agent.calculate_tariff(
            category="玩具",
            target_country="德国",
            product_value=10000,
        )
        assert result["product_value"] == 10000
        assert result["tariff_amount"] > 0
        assert result["vat_amount"] > 0
        assert result["total_cost"] > 10000

    @pytest.mark.asyncio
    async def test_european_certifications(self):
        result = await self.agent.execute(target_country="德国")
        certs = result["certifications"]
        assert len(certs) > 0
        cert_names = [c["name"] for c in certs]
        assert "CE认证" in cert_names


# ==================== 智能客服Agent ====================

class TestCustomerServiceAgent:
    def setup_method(self):
        self.agent = CustomerServiceAgent()

    @pytest.mark.asyncio
    async def test_execute_basic(self):
        result = await self.agent.execute(message="你好")
        assert result["status"] == "success"
        assert "reply" in result
        assert "emotion" in result
        assert "session_id" in result

    @pytest.mark.asyncio
    async def test_emotion_detection(self):
        result = await self.agent.execute(message="我非常不满意，要投诉")
        assert result["emotion"]["type"] == "negative"

    @pytest.mark.asyncio
    async def test_positive_emotion(self):
        result = await self.agent.execute(message="非常满意，太棒了")
        assert result["emotion"]["type"] == "positive"

    @pytest.mark.asyncio
    async def test_dispute_detection(self):
        result = await self.agent.execute(message="货物破损了，要退款")
        assert result["dispute"]["detected"] is True

    @pytest.mark.asyncio
    async def test_faq_retrieval(self):
        result = await self.agent.get_faq(category="日用百货")
        assert "faqs" in result
        assert isinstance(result["faqs"], list)


# ==================== 政策复制Agent ====================

class TestPolicyReplicationAgent:
    def setup_method(self):
        self.agent = PolicyReplicationAgent()

    @pytest.mark.asyncio
    async def test_execute_overview(self):
        result = await self.agent.execute()
        assert result["status"] == "success"
        assert "total_cities" in result
        assert result["total_cities"] > 0

    @pytest.mark.asyncio
    async def test_get_policy_guide(self):
        result = await self.agent.get_policy_guide()
        assert result["status"] == "success"
        assert "policy_name" in result
        assert "key_points" in result
        assert "tax_benefits" in result

    @pytest.mark.asyncio
    async def test_get_cities(self):
        result = await self.agent.get_city_info()
        assert result["status"] == "success"
        assert "cities" in result
        assert len(result["cities"]) > 0

    @pytest.mark.asyncio
    async def test_calculate_benefit(self):
        result = await self.agent.calculate_policy_benefit(
            annual_export=1000000,
            category="日用百货",
            city="义乌",
        )
        assert result["status"] == "success"
        assert result["total_saving"] > 0
        assert "benefits" in result


# ==================== 全链路工作流 ====================

class TestWorkflow:
    def setup_method(self):
        self.workflow = CrossBorderWorkflow()

    @pytest.mark.asyncio
    async def test_workflow_run(self):
        state = WorkflowState(
            category="玩具",
            region="东南亚",
            budget="中",
            target_country="泰国",
        )
        result = await self.workflow.run(state)
        assert "state" in result
        assert "summary" in result
        assert result["summary"]["total_steps"] == 7
        assert result["summary"]["steps_completed"] > 0

    def test_get_steps(self):
        steps = self.workflow.get_steps()
        assert len(steps) == 7
        assert steps[0]["key"] == "market_insight"
        assert steps[-1]["key"] == "policy_replication"
