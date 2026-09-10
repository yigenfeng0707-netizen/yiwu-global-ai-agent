"""义乌小商品出海智能体 - Pydantic模型"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class HotCategory(BaseModel):
    name: str
    share: str
    growth: str


class Trend(BaseModel):
    description: str
    impact: str


class PriceTier(BaseModel):
    tier: str
    price_range: str
    volume_share: str


class Competitor(BaseModel):
    name: str
    market_share: str
    strength: Optional[str] = None


class Recommendation(BaseModel):
    product: str
    rating: float
    reason: Optional[str] = None
    predicted_sales: Optional[str] = None


class Risk(BaseModel):
    description: str
    level: str
    mitigation: Optional[str] = None


class MarketReport(BaseModel):
    category: str
    region: str
    market_size: str
    market_growth: str
    hot_categories: List[HotCategory]
    trends: List[Trend]
    price_tiers: List[PriceTier]
    competitors: List[Competitor]
    recommendations: List[Recommendation]
    risks: List[Risk]


class ContentGenerateRequest(BaseModel):
    product_name: str = ""
    category: str = "日用百货"
    platform: str = "amazon"
    target_language: str = "en"


class CustomerChatRequest(BaseModel):
    message: str
    category: str = "日用百货"
    language: str = "zh"
    session_id: str = "default"


class TariffCalcRequest(BaseModel):
    category: str = "日用百货"
    target_country: str = "德国"
    product_value: float = 1000


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    company: Optional[str] = ""


class PipelineRequest(BaseModel):
    category: str = "日用百货"
    region: str = "欧洲（义新欧班列直达）"
    budget: str = "中"
    target_country: str = "德国"
    platform: str = "amazon"
    target_language: str = "en"


class SupplyChainRequest(BaseModel):
    category: str = "日用百货"
    region: str = ""
    budget: str = "中"


class LogisticsRequest(BaseModel):
    region: str = ""
    category: str = ""


class PolicyBenefitCalcRequest(BaseModel):
    annual_export: float = 1000000
    category: str = "日用百货"
    city: str = "义乌"


class LocalizedCaseRequest(BaseModel):
    case_id: int = 1
    target_city: str = ""


# ==================== 响应模型（P2-4：稳定端点契约化，Agent 动态响应除外） ====================


class ApiRootResponse(BaseModel):
    service: str
    version: str
    description: str


class AgentInfoItem(BaseModel):
    name: str
    display_name: str
    status: str
    description: str
    engine: str


class AgentsInfoResponse(BaseModel):
    agents: List[AgentInfoItem]
    ai_enhanced_count: int


class CategoriesResponse(BaseModel):
    categories: List[str]


class RegionsResponse(BaseModel):
    regions: List[str]


class DataSourcesResponse(BaseModel):
    sources: List[Dict[str, Any]]
    real_count: int
    total: int
    note: str


class RealDataSourceStatus(BaseModel):
    """/status 中逐源真实数据状态（可自证：带 source_url 与数据年龄）。"""

    source: str
    is_real: bool
    age_seconds: Optional[float] = None
    is_fresh: Optional[bool] = None
    source_url: str = ""
    fetched_at_iso: str = ""
    error: str = ""


class SystemStatusResponse(BaseModel):
    service: str
    version: str
    agents: Dict[str, str]
    llm_configured: bool
    data_mode: str
    real_data_sources: List[RealDataSourceStatus]
    real_source_count: int
    agent_engines: Dict[str, str]
    ai_enhanced_count: int
    llm_usage: Dict[str, Any]
    data_sources: int
    cache: Dict[str, Any]


class AuthLoginResponse(BaseModel):
    success: bool
    token: str
    email: str
    user_id: str
    company: str = ""


class AuthRegisterResponse(BaseModel):
    success: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    detail: Optional[str] = None


class UsageStatsResponse(BaseModel):
    api_usage: Dict[str, Any]
    auth: Dict[str, Any]
    chat_sessions: int
    cache: Dict[str, Any]


class QueryHistoryResponse(BaseModel):
    history: List[Dict[str, Any]]


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]


class PolicyCasesResponse(BaseModel):
    cases: List[Dict[str, Any]]


# ==================== P3-5 商业化：定价/支付/转化模型 ====================


class PricingPlanItem(BaseModel):
    code: str
    name: str
    price_cny: float
    price_display: str
    period: str
    description: str
    features: List[str]
    highlight: bool
    cta: str
    duration_days: int


class PricingPlansResponse(BaseModel):
    plans: List[Dict[str, Any]]
    variant: str
    variant_label: str
    layout: str
    experiment: str


class TrackEventRequest(BaseModel):
    event_type: str
    plan_code: str = ""
    session_id: str = ""
    metadata: Dict[str, Any] = {}


class TrackEventResponse(BaseModel):
    success: bool
    event_id: int


class CheckoutRequest(BaseModel):
    plan_code: str
    pay_method: str = "alipay_sandbox"


class CheckoutResponse(BaseModel):
    success: bool
    order_no: Optional[str] = None
    amount_cny: Optional[float] = None
    plan_name: Optional[str] = None
    plan_code: Optional[str] = None
    status: Optional[str] = None
    provider: Optional[str] = None
    pay_method: Optional[str] = None
    pay_url: Optional[str] = None
    expires_in_seconds: Optional[int] = None
    note: Optional[str] = None
    detail: Optional[str] = None


class PaymentConfirmRequest(BaseModel):
    order_no: str
    pay_method: str = "alipay_sandbox"


class PaymentConfirmResponse(BaseModel):
    success: bool
    order_no: Optional[str] = None
    status: Optional[str] = None
    plan_code: Optional[str] = None
    plan_name: Optional[str] = None
    subscription_id: Optional[int] = None
    expires_at: Optional[float] = None
    detail: Optional[str] = None
    already_paid: Optional[bool] = None


class OrdersResponse(BaseModel):
    orders: List[Dict[str, Any]]


class SubscriptionResponse(BaseModel):
    subscription: Optional[Dict[str, Any]] = None


class FunnelSummaryResponse(BaseModel):
    events: Dict[str, int]
    conversion_rate: float
    checkout_rate: float
    payment_rate: float
    total_events: int
    hours: int
