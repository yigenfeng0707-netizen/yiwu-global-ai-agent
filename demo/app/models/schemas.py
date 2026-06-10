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
