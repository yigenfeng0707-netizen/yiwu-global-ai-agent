"""义乌小商品出海智能体 - API路由"""

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..agents.market_insight import MarketInsightAgent
from ..agents.smart_selection import SmartSelectionAgent
from ..agents.content_generation import ContentGenerationAgent
from ..agents.compliance_agent import ComplianceAgent
from ..agents.customer_service_agent import CustomerServiceAgent
from ..agents.supply_chain_agent import SupplyChainAgent
from ..agents.policy_replication_agent import PolicyReplicationAgent
from ..agents.workflow import CrossBorderWorkflow, WorkflowState
from ..data.market_data import CATEGORY_LIST, SUPPORTED_REGIONS, YIWU_INDEX, YIXINOU_DATA, YIWU_TRADE_CITY
from ..data.sources import DataSourceManager
from ..data.etl import get_registry
from ..models.schemas import (
    ContentGenerateRequest, CustomerChatRequest, TariffCalcRequest,
    LoginRequest, RegisterRequest, PipelineRequest, SupplyChainRequest, LogisticsRequest,
    PolicyBenefitCalcRequest, LocalizedCaseRequest,
)
from ..services.auth import auth_service
from ..services.llm import llm_service
from ..cache import cache, cached

router = APIRouter()

# Agent 引擎类型（P1-2 后 7 个 Agent 均接入 LLM 增强：确定性/规则骨架 + LLM 推理）
# 用于 /status 与 /agents/info 对外如实反映 AI 接入程度，避免"7个AI数字员工"叙事与实现不符
AGENT_ENGINES = {
    "market_insight": "llm-enhanced",
    "content_generation": "llm-enhanced",
    "customer_service": "llm-enhanced",
    "smart_selection": "llm-enhanced",
    "supply_chain": "llm-enhanced",
    "compliance": "llm-enhanced",
    "policy_replication": "llm-enhanced",
}

# 初始化Agents
market_agent = MarketInsightAgent()
selection_agent = SmartSelectionAgent()
content_agent = ContentGenerationAgent()
compliance_agent = ComplianceAgent()
customer_agent = CustomerServiceAgent()
supply_chain_agent = SupplyChainAgent()
policy_replication_agent = PolicyReplicationAgent()
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
    agents = [
        {"name": "market_insight", "display_name": "市场洞察", "status": "online", "description": "分析全球市场趋势与义乌指数"},
        {"name": "smart_selection", "display_name": "智能选品", "status": "online", "description": "基于多维度数据智能推荐选品"},
        {"name": "content_generation", "display_name": "内容生成", "status": "online", "description": "生成多语言跨境电商内容"},
        {"name": "compliance", "display_name": "合规查询", "status": "online", "description": "查询目标市场合规要求与关税"},
        {"name": "customer_service", "display_name": "智能客服", "status": "online", "description": "多语言智能客服与FAQ"},
        {"name": "supply_chain", "display_name": "供应链匹配", "status": "online", "description": "供应链与物流智能匹配"},
        {"name": "policy_replication", "display_name": "政策复制", "status": "online", "description": "1039政策解读、39城复制推广、红利计算"},
    ]
    for a in agents:
        a["engine"] = AGENT_ENGINES.get(a["name"], "rule-based")
    return {
        "agents": agents,
        "ai_enhanced_count": sum(1 for a in agents if a["engine"] == "llm-enhanced"),
    }


@router.get("/categories")
@cached(ttl=3600)
async def get_categories():
    """获取品类列表（静态常量，缓存1小时）"""
    return {"categories": CATEGORY_LIST}


@router.get("/regions")
@cached(ttl=3600)
async def get_regions():
    """获取目标市场区域（静态常量，缓存1小时）"""
    return {"regions": SUPPORTED_REGIONS}


@router.get("/data-sources")
async def get_data_sources():
    """获取数据源三态清单（real 真实接入 / demo 演示 / planned 规划中，含新鲜度溯源）"""
    sources = data_manager.list_all_sources()
    return {
        "sources": sources,
        "real_count": sum(1 for s in sources if s.get("is_real")),
        "total": len(sources),
        "note": "real=已接入真实外部数据管道（带时间戳可自证）；demo=静态演示数据；planned=接入规划中",
    }


@router.post("/data-sources/refresh")
async def refresh_data_sources(force: bool = True):
    """手动触发真实数据源刷新（答辩现场可演示真实请求-响应）。

    返回各源刷新结果：is_real / 数据年龄 / 失败原因。
    """
    reg = get_registry()
    results = reg.refresh(force=force)
    return {
        "refreshed": [r.to_dict() for r in results.values()],
        "real_count": reg.real_count(),
        "total_real_sources": len(reg.source_names),
    }


@router.get("/yiwu-index")
async def get_yiwu_index():
    """获取义乌指数：演示基准值 + 官方发布真实值 + 实时汇率（均带溯源）。

    诚实拆分（修复"102.8 常量冒充实时"痛点）：
      - demo_composite：旧演示基准（98-110 标度），明确 is_real=false；
      - official_published：义乌指数官网官方发布值（千点基准·定期更新），is_real=true 时带 as_of/source_url；
      - exchange_rate：open.er-api.com 每日参考汇率（USD/CNY 等），is_real=true 时带官方更新时间戳。
    """
    reg = get_registry()
    official = reg.get_data("yiwu_index")
    official_meta = reg.get_meta("yiwu_index")
    fx = reg.get_exchange_rate("CNY")
    return {
        "demo_composite": {
            **YIWU_INDEX,
            "is_real": False,
            "scale": "演示基准(98-110)",
            "note": "演示用综合基准值，非实时；真实官方发布值见 official_published",
        },
        "official_published": {
            "is_real": bool(official_meta.get("is_real")),
            "index_type": (official or {}).get("index_type", "义乌中国小商品指数（官方发布值）"),
            "index_scale": (official or {}).get("index_scale", "官方千点基准"),
            "update_mode": (official or {}).get("update_mode", "定期更新（官方发布，非实时面板）"),
            "records": (official or {}).get("records", []),
            "record_count": (official or {}).get("record_count", 0),
            "source_url": official_meta.get("source_url", ""),
            "fetched_at_iso": official_meta.get("fetched_at_iso", ""),
            "age_seconds": official_meta.get("age_seconds"),
            "error": official_meta.get("error", ""),
        },
        "exchange_rate": fx,
    }


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


@router.post("/pipeline/stream")
async def run_pipeline_stream(req: PipelineRequest):
    """全链路工作流 - SSE 实时进度上报。

    逐节点推送 LangGraph 真实执行状态（step/done/error 事件），
    前端据此驱动进度条，替代此前的 setTimeout 假动画。
    """
    state = WorkflowState(
        category=req.category,
        region=req.region,
        budget=req.budget,
        target_country=req.target_country,
        platform=req.platform,
        target_language=req.target_language,
    )

    async def event_generator():
        try:
            async for evt in workflow.run_stream(state):
                yield f"data: {json.dumps(evt, ensure_ascii=False)}\n\n"
        except Exception as e:  # 顶层兜底：把异常作为 error 事件推给前端
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # 禁止 Nginx/网关缓冲，保证逐条实时下发
            "Connection": "keep-alive",
        },
    )


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
    if not result.get("success"):
        raise HTTPException(status_code=401, detail=result.get("detail", "邮箱或密码错误"))
    return result


# ==================== 系统状态 ====================

@router.get("/status")
async def get_status():
    """系统状态（可自证的真实健康态）"""
    reg = get_registry()
    real_sources = []
    for name in reg.source_names:
        meta = reg.get_meta(name)
        real_sources.append({
            "source": name,
            "is_real": bool(meta.get("is_real")),
            "age_seconds": meta.get("age_seconds"),
            "is_fresh": meta.get("is_fresh"),
            "source_url": meta.get("source_url", ""),
            "fetched_at_iso": meta.get("fetched_at_iso", ""),
            "error": meta.get("error", ""),
        })
    real_count = sum(1 for s in real_sources if s["is_real"])
    # 诚实标注数据模式：有真实源接入为 hybrid，全不可用回退 static-demo
    data_mode = f"hybrid({real_count}real)" if real_count else "static-demo"
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
        },
        # 诚实标注：AI 增强是否真正生效（取决于是否配置 LLM_API_KEY）
        "llm_configured": bool(llm_service.api_key),
        # 诚实标注：数据模式（hybrid=已接入真实源 / static-demo=全演示）
        "data_mode": data_mode,
        # 真实数据源逐源状态（可自证：带 source_url 与数据年龄）
        "real_data_sources": real_sources,
        "real_source_count": real_count,
        # 各 Agent 引擎类型（llm-enhanced / rule-based）
        "agent_engines": AGENT_ENGINES,
        "ai_enhanced_count": sum(1 for e in AGENT_ENGINES.values() if e == "llm-enhanced"),
        "llm_usage": llm_service.daily_usage,
        "data_sources": len(data_manager.list_sources()),
        "cache": cache.stats,
    }


# ==================== 系统监控 ====================

@router.get("/stats/usage")
async def get_usage_stats():
    """API使用统计"""
    from ..db.database import get_db
    db = get_db()
    return {
        "api_usage": db.get_api_usage_stats(hours=24),
        "auth": auth_service.get_stats(),
        "chat_sessions": db.get_session_count(),
        "cache": cache.stats,
    }


@router.get("/stats/history")
async def get_query_history(limit: int = 20):
    """查询历史"""
    from ..db.database import get_db
    db = get_db()
    return {"history": db.get_query_history(limit=limit)}


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 50):
    """获取聊天会话历史"""
    from ..db.database import get_db
    db = get_db()
    return {"session_id": session_id, "messages": db.get_chat_history(session_id, limit=limit)}
