"""义乌小商品出海智能体 - API路由"""

from fastapi import APIRouter

from ..agents.market_insight import MarketInsightAgent
from ..agents.smart_selection import SmartSelectionAgent
from ..agents.content_generation import ContentGenerationAgent
from ..agents.compliance_agent import ComplianceAgent
from ..agents.customer_service_agent import CustomerServiceAgent
from ..agents.supply_chain_agent import SupplyChainAgent
from ..agents.policy_replication_agent import PolicyReplicationAgent
from ..agents.competitor_research_agent import CompetitorResearchAgent
from ..agents.workflow import CrossBorderWorkflow, WorkflowState
from ..data.market_data import CATEGORY_LIST, SUPPORTED_REGIONS, YIWU_INDEX, YIXINOU_DATA, YIWU_TRADE_CITY
from ..data.sources import DataSourceManager
from ..models.schemas import (
    ContentGenerateRequest, CustomerChatRequest, TariffCalcRequest,
    LoginRequest, RegisterRequest, PipelineRequest, SupplyChainRequest, LogisticsRequest,
    PolicyBenefitCalcRequest, LocalizedCaseRequest, CompetitorResearchRequest,
)
from ..services.auth import auth_service
from ..services.llm import llm_service

router = APIRouter()

# 初始化Agents
market_agent = MarketInsightAgent()
selection_agent = SmartSelectionAgent()
content_agent = ContentGenerationAgent()
compliance_agent = ComplianceAgent()
customer_agent = CustomerServiceAgent()
supply_chain_agent = SupplyChainAgent()
policy_replication_agent = PolicyReplicationAgent()
competitor_agent = CompetitorResearchAgent()
workflow = CrossBorderWorkflow()
data_manager = DataSourceManager()


# ==================== 基础接口 ====================

@router.get("/")
async def api_root():
    """API根路径"""
    return {
        "service": "义乌小商品出海智能体",
        "version": "2.0.0",
        "description": "基于义乌小商品城7.5万商户、210万+SKU，为跨境电商提供一站式AI智能服务",
    }


@router.get("/agents/info")
async def get_agents_info():
    """获取智能体信息"""
    return {
        "agents": [
            {"name": "market_insight", "display_name": "市场洞察", "status": "online", "description": "分析全球市场趋势与义乌指数"},
            {"name": "smart_selection", "display_name": "智能选品", "status": "online", "description": "基于多维度数据智能推荐选品"},
            {"name": "content_generation", "display_name": "内容生成", "status": "online", "description": "生成多语言跨境电商内容"},
            {"name": "compliance", "display_name": "合规查询", "status": "online", "description": "查询目标市场合规要求与关税"},
            {"name": "customer_service", "display_name": "智能客服", "status": "online", "description": "多语言智能客服与FAQ"},
            {"name": "supply_chain", "display_name": "供应链匹配", "status": "online", "description": "供应链与物流智能匹配"},
            {"name": "policy_replication", "display_name": "政策复制", "status": "online", "description": "1039政策解读、39城复制推广、红利计算"},
            {"name": "competitor_research", "display_name": "竞品实采", "status": "online", "description": "浏览器自主操作，在Amazon/1688真实调研竞品"},
        ]
    }


@router.get("/categories")
async def get_categories():
    """获取品类列表"""
    return {"categories": CATEGORY_LIST}


@router.get("/regions")
async def get_regions():
    """获取目标市场区域"""
    return {"regions": SUPPORTED_REGIONS}


@router.get("/data-sources")
async def get_data_sources():
    """获取数据源列表"""
    return {"sources": data_manager.list_sources()}


@router.get("/yiwu-index")
async def get_yiwu_index():
    """获取义乌指数"""
    return YIWU_INDEX


@router.get("/yiwu-trade-city")
async def get_yiwu_trade_city():
    """获取义乌国际商贸城数据"""
    return YIWU_TRADE_CITY


# ==================== 市场洞察 ====================

@router.get("/market-insight")
async def get_market_insight(category: str = CATEGORY_LIST[0], region: str = SUPPORTED_REGIONS[0]):
    """市场洞察"""
    result = await market_agent.execute(category=category, region=region)
    return result


# ==================== 竞品实采（智能体自主性 / 工具调用） ====================

@router.post("/competitor-research")
async def post_competitor_research(req: CompetitorResearchRequest):
    """竞品实采：智能体在真实电商网站自主搜索并抽取竞品情报"""
    result = await competitor_agent.execute(
        query=req.query or req.category,
        platform=req.platform,
        country=req.country,
        max_items=req.max_items,
    )
    return result


@router.get("/competitor-research")
async def get_competitor_research(query: str = "", category: str = CATEGORY_LIST[0], platform: str = "amazon", country: str = "US", max_items: int = 8):
    """竞品实采（GET）：智能体在真实电商网站自主调研竞品"""
    result = await competitor_agent.execute(
        query=query or category, platform=platform, country=country, max_items=max_items,
    )
    return result


# ==================== 智能选品 ====================

@router.get("/smart-selection")
async def get_smart_selection(category: str = CATEGORY_LIST[0], budget: str = "中", region: str = SUPPORTED_REGIONS[0]):
    """智能选品"""
    result = await selection_agent.execute(category=category, budget=budget, region=region)
    return result


# ==================== 供应链匹配 ====================

@router.get("/supply-chain/{category}")
async def get_supply_chain(category: str, region: str = "", budget: str = "中"):
    """供应链匹配"""
    result = await supply_chain_agent.execute(category=category, region=region, budget=budget)
    return result


@router.post("/supply-chain")
async def post_supply_chain(req: SupplyChainRequest):
    """供应链匹配（POST）"""
    result = await supply_chain_agent.execute(category=req.category, region=req.region, budget=req.budget)
    return result


# ==================== 义新欧班列物流 ====================

@router.get("/logistics/yixinou")
async def get_yixinou_logistics(region: str = "", category: str = ""):
    """义新欧班列物流信息"""
    result = data_manager.fetch_by_source("义新欧班列", category, region)
    if result:
        return result
    return YIXINOU_DATA


# ==================== 内容生成 ====================

@router.post("/content/generate")
async def generate_content(req: ContentGenerateRequest):
    """生成跨境内容"""
    result = await content_agent.execute(
        product_name=req.product_name,
        category=req.category,
        platform=req.platform,
        target_language=req.target_language,
    )
    return result


# ==================== 合规查询 ====================

@router.get("/compliance")
async def get_compliance(category: str = CATEGORY_LIST[0], target_country: str = "德国"):
    """合规查询"""
    result = await compliance_agent.execute(category=category, target_country=target_country)
    return result


@router.post("/tariff/calculate")
async def calculate_tariff(req: TariffCalcRequest):
    """关税计算"""
    result = await compliance_agent.calculate_tariff(
        category=req.category,
        target_country=req.target_country,
        product_value=req.product_value,
    )
    return result


# ==================== 智能客服 ====================

@router.post("/customer-service/chat")
async def customer_chat(req: CustomerChatRequest):
    """智能客服聊天"""
    result = await customer_agent.execute(
        message=req.message,
        category=req.category,
        language=req.language,
        session_id=req.session_id,
    )
    return result


@router.get("/customer-service/faq")
async def get_faq(category: str = CATEGORY_LIST[0], language: str = "zh"):
    """获取FAQ"""
    result = await customer_agent.get_faq(category=category, language=language)
    return result


# ==================== 政策复制 ====================

@router.get("/policy-replication/cities")
async def get_policy_cities():
    """39城市场采购贸易试点城市列表"""
    result = await policy_replication_agent.get_city_info()
    return result


@router.get("/policy-replication/city/{city_name}")
async def get_policy_city(city_name: str):
    """单个城市1039试点信息"""
    result = await policy_replication_agent.get_city_info(city_name=city_name)
    return result


@router.get("/policy-replication/policy-guide")
async def get_policy_guide():
    """1039市场采购贸易政策解读"""
    result = await policy_replication_agent.get_policy_guide()
    return result


@router.post("/policy-replication/calculate-benefit")
async def calculate_policy_benefit(req: PolicyBenefitCalcRequest):
    """政策红利计算"""
    result = await policy_replication_agent.calculate_policy_benefit(
        annual_export=req.annual_export,
        category=req.category,
        city=req.city,
    )
    return result


@router.get("/policy-replication/cases")
async def get_policy_cases():
    """义乌成功案例"""
    from ..data.policy_data import YIWU_SUCCESS_CASES
    return {"cases": YIWU_SUCCESS_CASES}


# ==================== 全链路工作流 ====================

@router.post("/pipeline")
async def run_pipeline(req: PipelineRequest):
    """全链路工作流"""
    state = WorkflowState(
        category=req.category,
        region=req.region,
        budget=req.budget,
        target_country=req.target_country,
        platform=req.platform,
        target_language=req.target_language,
    )
    result = await workflow.run(state)
    return result


# ==================== 认证接口 ====================

@router.post("/auth/register")
async def register(req: RegisterRequest):
    """注册"""
    result = auth_service.register(email=req.email, password=req.password, company=req.company or "")
    return result


@router.post("/auth/login")
async def login(req: LoginRequest):
    """登录"""
    result = auth_service.login(email=req.email, password=req.password)
    return result


# ==================== 系统状态 ====================

@router.get("/status")
async def get_status():
    """系统状态"""
    return {
        "service": "yiwu-chuhai-api",
        "version": "2.0.0",
        "agents": {
            "market_insight": "online",
            "smart_selection": "online",
            "content_generation": "online",
            "compliance": "online",
            "customer_service": "online",
            "supply_chain": "online",
            "policy_replication": "online",
            "competitor_research": "online",
        },
        "llm_usage": llm_service.daily_usage,
        "data_sources": len(data_manager.list_sources()),
    }
