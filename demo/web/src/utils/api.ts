const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

import {
  mockMarketInsight, mockSmartSelection, mockSupplyChain, mockLogistics,
  mockContentGeneration, mockCompliance, mockTariff, mockChatResponse, mockChatReply,
  mockFAQ, mockPipeline, mockPolicyCities, mockPolicyGuide,
  mockPolicyBenefit, mockPolicyCases,
} from './mockData';

// ==================== 类型定义 ====================

export interface HotCategory { name: string; share: string; growth: string; }
export interface Trend { description: string; impact: string; }
export interface PriceTier { tier: string; price_range: string; volume_share: string; }
export interface Competitor { name: string; market_share: string; strength?: string; }
export interface Recommendation { product: string; rating: number; reason?: string; predicted_sales?: string; }
export interface Risk { description: string; level: string; mitigation?: string; }

export interface MarketInsightData {
  category: string; region: string;
  market_size: string; market_growth: string;
  hot_categories: HotCategory[];
  trends: Trend[];
  price_tiers: PriceTier[];
  competitors: Competitor[];
  recommendations: Recommendation[];
  risks: Risk[];
  yiwu_index?: { current: number; change: number; trend: string; category_score: number; };
  data_sources?: string[];
}

export interface SmartSelectionData {
  category: string; budget: string; region: string;
  overall_score: { total: number; level: string; [key: string]: unknown };
  market_opportunity: { market_size: string; growth_rate: string; competition_level: string; entry_difficulty: string; };
  product_recommendations: { product: string; scores: Record<string, number>; suggested_moq: number; estimated_roi: string; }[];
  profit_analysis: { cost_breakdown: Record<string, string>; revenue: Record<string, string>; break_even: Record<string, string>; };
  supply_recommendations: { supplier: string; location: string; moq: string; price_range: string; rating: number; recommended: boolean; }[];
  action_plan: Record<string, { name: string; tasks: string[] }>;
}

export interface ContentGenerationData {
  product_name: string; category: string; platform: string; target_language: string;
  content: { title: string; description: string; highlights: { icon: string; text: string }[]; seo_keywords: string[]; };
  marketing: { social_copy: { hook: string; pain_point: string; solution: string; cta: string; hashtags: string[]; }; ad_copy: { headline: string; body: string; cta_button: string; }; };
  platform_compliance: { warnings: string[]; };
}

export interface ComplianceData {
  category: string; target_country: string;
  certifications: { name: string; required: boolean; estimated_time: string; estimated_cost: string; }[];
  clearance_documents: { name: string; required: boolean; description: string; }[];
  compliance_check: { checks: { item: string; status: string; risk_level: string; }[]; overall_status: string; };
  special_requirements?: string;
  tariff_benefits?: { description: string; benefits: string[]; };
}

export interface SupplyChainData {
  category: string; region: string; budget: string;
  suppliers: { supplier: string; product: string; district: string; moq: number; unit_price: string; delivery_days: number; rating: number; certifications: string[]; recommended: boolean; }[];
  purchase_info: { avg_price_range: string; yiwu_advantage: string; yiwu_index_score: number; price_trend: string; sample_available: boolean; sample_lead_time: string; bulk_lead_time: string; payment_terms: string[]; };
  logistics: { source: string; total_routes: number; countries_covered: number; cities_connected: number; routes: { name: string; days: number; frequency: string; cost_20ft: string; cost_40ft: string; }[]; advantages: string[]; };
  trade_1039: { applicable: boolean; name: string; description: string; advantages: string[]; conditions: string[]; max_value_per_shipment: string; simplified_declaration: boolean; vat_exemption: boolean; };
  supply_score: { total: number; level: string; dimensions: Record<string, number>; };
  yiwu_trade_city: { total_shops: number; total_skus: number; district: string; };
}

export interface LogisticsData {
  source: string; total_routes: number; countries_covered: number; cities_connected: number;
  routes: { name: string; days: number; frequency: string; cost_20ft: string; cost_40ft: string; }[];
  advantages: string[];
}

export interface ChatResponseData {
  reply: { text: string };
  emotion?: { type: string; label: string; color: string };
  dispute?: { detected: boolean; type?: string };
  needs_human_escalation: boolean;
  faq_match?: unknown;
  session_id: string;
}

export interface FAQResponseData {
  faqs: { q_zh: string; a_zh: string; q_en: string; a_en: string }[];
  category: string;
}

export interface PipelineResult {
  state: Record<string, unknown>;
  summary: { total_steps: number; steps_completed: number; duration_seconds: number; errors: number; product: string; };
}

export interface PolicyCityData {
  city: string; province: string; approved_year: string;
  main_categories: string; policy_benefits: string; customs_code: string;
}

export interface PolicyCitiesResponse {
  total: number; cities: PolicyCityData[];
}

export interface PolicyGuideData {
  policy_name: string; policy_code: string; background: string;
  key_points: { title: string; description: string; benefit_level: string; }[];
  applicable_conditions: string[];
  operation_process: { step: number; title: string; description: string; }[];
  tax_benefits: {
    vat_exemption: boolean; vat_description: string;
    income_tax: string; stamp_duty: string;
    compared_to_general_trade: {
      general_trade_vat: string; market_purchase_vat: string; cost_saving: string;
    };
  };
}

export interface PolicyBenefitData {
  annual_export: number; category: string; city: string;
  benefits: Record<string, { description: string; amount: number; detail: string; }>;
  total_saving: number; saving_rate: string;
  compared_to_general_trade: {
    general_trade_total_cost: number; market_purchase_total_cost: number; cost_reduction: string;
  };
}

export interface PolicyCaseData {
  case_id: number; title: string; category: string; target_market: string;
  annual_export: string; key_strategies: string[];
  localization_tips: string[]; replication_difficulty: string; replicable_points: string[];
}

// ==================== API 函数 ====================

async function apiFetch<T>(url: string, options?: RequestInit & { timeout?: number }): Promise<T> {
  const timeoutMs = options?.timeout || 10000;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${BASE_URL}${url}`, {
      headers: { 'Content-Type': 'application/json', ...options?.headers },
      ...options,
      signal: controller.signal,
    });
    if (!res.ok) {
      throw new Error(`API Error: ${res.status}`);
    }
    return res.json();
  } finally {
    clearTimeout(timer);
  }
}

// 市场洞察
export async function fetchMarketInsight(category: string, region: string): Promise<MarketInsightData> {
  try {
    return await apiFetch(`/market-insight?category=${encodeURIComponent(category)}&region=${encodeURIComponent(region)}`);
  } catch {
    return mockMarketInsight(category, region);
  }
}

// 智能选品
export async function fetchSmartSelection(category: string, budget: string, region: string): Promise<SmartSelectionData> {
  try {
    return await apiFetch(`/smart-selection?category=${encodeURIComponent(category)}&budget=${encodeURIComponent(budget)}&region=${encodeURIComponent(region)}`);
  } catch {
    return mockSmartSelection(category, budget, region);
  }
}

// 供应链匹配
export async function fetchSupplyChain(category: string, region: string, budget: string): Promise<SupplyChainData> {
  try {
    return await apiFetch(`/supply-chain/${encodeURIComponent(category)}?region=${encodeURIComponent(region)}&budget=${encodeURIComponent(budget)}`);
  } catch {
    return mockSupplyChain(category, region, budget);
  }
}

// 义新欧班列物流
export async function fetchYixinouLogistics(region: string = ''): Promise<LogisticsData> {
  try {
    return await apiFetch(`/logistics/yixinou?region=${encodeURIComponent(region)}`);
  } catch {
    return mockLogistics();
  }
}

// 内容生成
export async function generateContent(req: { product_name: string; category: string; platform: string; target_language: string }): Promise<ContentGenerationData> {
  try {
    return await apiFetch('/content/generate', { method: 'POST', body: JSON.stringify(req) });
  } catch {
    return mockContentGeneration(req.product_name, req.category, req.platform, req.target_language);
  }
}

// 合规查询
export async function fetchComplianceCheck(category: string, target_country: string): Promise<ComplianceData> {
  try {
    return await apiFetch(`/compliance?category=${encodeURIComponent(category)}&target_country=${encodeURIComponent(target_country)}`);
  } catch {
    return mockCompliance(category, target_country);
  }
}

// 关税计算
export async function calculateTariff(req: { category: string; target_country: string; product_value: number }) {
  try {
    return await apiFetch('/tariff/calculate', { method: 'POST', body: JSON.stringify(req) });
  } catch {
    return mockTariff(req.product_value);
  }
}

// 智能客服
export async function sendChatMessage(req: { message: string; category: string; language: string; session_id: string }): Promise<ChatResponseData> {
  try {
    return await apiFetch('/customer-service/chat', { method: 'POST', body: JSON.stringify(req), timeout: 5000 });
  } catch {
    return mockChatReply(req.message);
  }
}

// FAQ
export async function fetchFAQ(category: string, language: string = 'zh'): Promise<FAQResponseData> {
  try {
    return await apiFetch(`/customer-service/faq?category=${encodeURIComponent(category)}&language=${language}`);
  } catch {
    return mockFAQ(category, language);
  }
}

// 全链路工作流
export async function runPipeline(req: { category: string; region: string; budget: string; target_country: string; platform: string; target_language: string }): Promise<PipelineResult> {
  try {
    return await apiFetch('/pipeline', { method: 'POST', body: JSON.stringify(req) });
  } catch {
    return mockPipeline();
  }
}

// 政策复制 - 39城列表
export async function fetchPolicyCities(): Promise<PolicyCitiesResponse> {
  try {
    return await apiFetch('/policy-replication/cities');
  } catch {
    return mockPolicyCities();
  }
}

// 政策复制 - 单个城市信息
export async function fetchPolicyCity(cityName: string): Promise<unknown> {
  try {
    return await apiFetch(`/policy-replication/city/${encodeURIComponent(cityName)}`);
  } catch {
    const cities = mockPolicyCities().cities;
    return cities.find(c => c.city === cityName) || cities[0];
  }
}

// 政策复制 - 1039政策解读
export async function fetchPolicyGuide(): Promise<PolicyGuideData> {
  try {
    return await apiFetch('/policy-replication/policy-guide');
  } catch {
    return mockPolicyGuide();
  }
}

// 政策复制 - 政策红利计算
export async function calculatePolicyBenefit(req: { annual_export: number; category: string; city: string }): Promise<PolicyBenefitData> {
  try {
    return await apiFetch('/policy-replication/calculate-benefit', { method: 'POST', body: JSON.stringify(req) });
  } catch {
    return mockPolicyBenefit(req.annual_export, req.category, req.city);
  }
}

// 政策复制 - 义乌成功案例
export async function fetchPolicyCases(): Promise<{ cases: PolicyCaseData[] }> {
  try {
    return await apiFetch('/policy-replication/cases');
  } catch {
    return mockPolicyCases();
  }
}
