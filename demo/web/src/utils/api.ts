const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

import {
  mockMarketInsight, mockSmartSelection, mockSupplyChain, mockLogistics,
  mockContentGeneration, mockCompliance, mockTariff, mockChatReply,
  mockFAQ, mockPipeline, mockPolicyCities, mockPolicyGuide,
  mockPolicyBenefit, mockPolicyCases,
} from './mockData';
import { withSource } from '@/store/useDataSource';
import { TOKEN_STORAGE_KEY } from '@/store/useStore';

// ==================== 类型定义 ====================

export interface HotCategory { name: string; share: string; growth: string; }
export interface Trend { description: string; impact: string; }
export interface PriceTier { tier: string; price_range: string; volume_share: string; }
export interface Competitor { name: string; market_share: string; strength?: string; }
export interface Recommendation { product: string; rating: number; reason?: string; predicted_sales?: string; }
export interface Risk { description: string; level: string; mitigation?: string; }

export interface OfficialIndex {
  is_real: boolean;
  index_value: number | null;
  scale?: string;
  as_of?: string;
  category_matched?: string;
  change_pct?: number | null;
  source_url?: string;
  fetched_at_iso?: string;
  excerpt?: string;
  note?: string;
}

export interface ExchangeRate {
  is_real: boolean;
  currency?: string;
  base?: string;
  rate: number | null;
  as_of?: string;
  source_url?: string;
  fetched_at_iso?: string;
  provider?: string;
  note?: string;
}

export interface MarketInsightData {
  category: string; region: string;
  market_size: string; market_growth: string;
  hot_categories: HotCategory[];
  trends: Trend[];
  price_tiers: PriceTier[];
  competitors: Competitor[];
  recommendations: Recommendation[];
  risks: Risk[];
  yiwu_index?: {
    current: number; change: number; trend: string; category_score: number;
    demo_scale?: string;
    is_real?: boolean;
    official?: OfficialIndex;
    exchange_rate?: ExchangeRate;
  };
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
  ai_recommendation?: string;
  ai_used?: boolean;
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
  ai_compliance_advice?: string;
  ai_used?: boolean;
}

export interface SupplyChainData {
  category: string; region: string; budget: string;
  suppliers: { supplier: string; product: string; district: string; moq: number; unit_price: string; delivery_days: number; rating: number; certifications: string[]; recommended: boolean; }[];
  purchase_info: { avg_price_range: string; yiwu_advantage: string; yiwu_index_score: number; price_trend: string; sample_available: boolean; sample_lead_time: string; bulk_lead_time: string; payment_terms: string[]; };
  logistics: { source: string; total_routes: number; countries_covered: number; cities_connected: number; routes: { name: string; days: number; frequency: string; cost_20ft: string; cost_40ft: string; }[]; advantages: string[]; };
  trade_1039: { applicable: boolean; name: string; description: string; advantages: string[]; conditions: string[]; max_value_per_shipment: string; simplified_declaration: boolean; vat_exemption: boolean; };
  supply_score: { total: number; level: string; dimensions: Record<string, number>; };
  yiwu_trade_city: { total_shops: number; total_skus: number; district: string; };
  ai_recommendation?: string;
  ai_used?: boolean;
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
  _demo?: boolean; // true = 后端不可达时的演示降级数据
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
  const timeoutMs = options?.timeout || 20000;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    // P3-1：注入 JWT（登录后 localStorage 有则带，未登录/登出后不带）
    let token: string | null = null;
    try { token = localStorage.getItem(TOKEN_STORAGE_KEY); } catch { /* SSR/隐私模式下降级 */ }
    const authHeaders: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};

    const res = await fetch(`${BASE_URL}${url}`, {
      headers: { 'Content-Type': 'application/json', ...authHeaders, ...options?.headers },
      ...options,
      signal: controller.signal,
    });
    // P3-1：401 表示 token 过期/无效，主动清除避免下次继续带坏 token
    if (res.status === 401 && token) {
      try { localStorage.removeItem(TOKEN_STORAGE_KEY); } catch { /* ignore */ }
    }
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
  return withSource(
    apiFetch<MarketInsightData>(`/market-insight?category=${encodeURIComponent(category)}&region=${encodeURIComponent(region)}`),
    () => mockMarketInsight(category, region),
  );
}

// 智能选品
export async function fetchSmartSelection(category: string, budget: string, region: string): Promise<SmartSelectionData> {
  return withSource(
    apiFetch<SmartSelectionData>(`/smart-selection?category=${encodeURIComponent(category)}&budget=${encodeURIComponent(budget)}&region=${encodeURIComponent(region)}`),
    () => mockSmartSelection(category, budget, region),
  );
}

// 供应链匹配
export async function fetchSupplyChain(category: string, region: string, budget: string): Promise<SupplyChainData> {
  return withSource(
    apiFetch<SupplyChainData>(`/supply-chain/${encodeURIComponent(category)}?region=${encodeURIComponent(region)}&budget=${encodeURIComponent(budget)}`),
    () => mockSupplyChain(category, region, budget),
  );
}

// 义新欧班列物流
export async function fetchYixinouLogistics(region: string = ''): Promise<LogisticsData> {
  return withSource(
    apiFetch<LogisticsData>(`/logistics/yixinou?region=${encodeURIComponent(region)}`),
    () => mockLogistics(),
  );
}

// 内容生成
export async function generateContent(req: { product_name: string; category: string; platform: string; target_language: string }): Promise<ContentGenerationData> {
  return withSource(
    apiFetch<ContentGenerationData>('/content/generate', { method: 'POST', body: JSON.stringify(req) }),
    () => mockContentGeneration(req.product_name, req.category, req.platform, req.target_language),
  );
}

// 合规查询
export async function fetchComplianceCheck(category: string, target_country: string): Promise<ComplianceData> {
  return withSource(
    apiFetch<ComplianceData>(`/compliance?category=${encodeURIComponent(category)}&target_country=${encodeURIComponent(target_country)}`),
    () => mockCompliance(category, target_country),
  );
}

// 关税计算
export async function calculateTariff(req: { category: string; target_country: string; product_value: number }) {
  return withSource(
    apiFetch('/tariff/calculate', { method: 'POST', body: JSON.stringify(req) }),
    () => mockTariff(req.product_value, req.target_country),
  );
}

// 智能客服
export async function sendChatMessage(req: { message: string; category: string; language: string; session_id: string }): Promise<ChatResponseData> {
  return withSource(
    apiFetch<ChatResponseData>('/customer-service/chat', { method: 'POST', body: JSON.stringify(req), timeout: 45000 }),
    () => mockChatReply(req.message),
  );
}

// FAQ
export async function fetchFAQ(category: string, language: string = 'zh'): Promise<FAQResponseData> {
  return withSource(
    apiFetch<FAQResponseData>(`/customer-service/faq?category=${encodeURIComponent(category)}&language=${language}`),
    () => mockFAQ(category, language),
  );
}

// 全链路工作流（多Agent+真实LLM，耗时较长）
export async function runPipeline(req: { category: string; region: string; budget: string; target_country: string; platform: string; target_language: string }): Promise<PipelineResult> {
  return withSource(
    apiFetch<PipelineResult>('/pipeline', { method: 'POST', body: JSON.stringify(req), timeout: 120000 }),
    () => mockPipeline(),
  );
}

// ==================== 全链路 SSE 实时进度 ====================

export interface PipelineStreamEvent {
  type: 'step' | 'done' | 'error';
  step?: string;
  name?: string;
  status?: string;   // success | error | skipped
  index?: number;
  total?: number;
  elapsed?: number;
  summary?: PipelineResult['summary'];
  state?: Record<string, unknown>;
  error?: string;
}

/**
 * 以 SSE 流式执行全链路，逐节点回调真实进度事件。
 * 返回 true 表示流式成功并收到 done；false 表示流不可用，调用方应降级到 runPipeline。
 * 纯函数：不触碰 useDataSource，降级标记由调用方通过 runPipeline 完成。
 */
export async function runPipelineStream(
  req: { category: string; region: string; budget: string; target_country: string; platform: string; target_language: string },
  onEvent: (e: PipelineStreamEvent) => void,
): Promise<boolean> {
  try {
    const res = await fetch(`${BASE_URL}/pipeline/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    if (!res.ok || !res.body) return false;
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = '';
    let gotDone = false;
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const frames = buf.split('\n\n');
      buf = frames.pop() ?? '';
      for (const frame of frames) {
        const line = frame.trim();
        if (!line.startsWith('data:')) continue;
        const payload = line.slice(5).trim();
        if (!payload) continue;
        try {
          const evt = JSON.parse(payload) as PipelineStreamEvent;
          onEvent(evt);
          if (evt.type === 'done') gotDone = true;
        } catch {
          /* 忽略半截帧，等待后续数据补齐 */
        }
      }
    }
    return gotDone;
  } catch {
    return false;
  }
}

// 政策复制 - 39城列表
export async function fetchPolicyCities(): Promise<PolicyCitiesResponse> {
  return withSource(
    apiFetch<PolicyCitiesResponse>('/policy-replication/cities'),
    () => mockPolicyCities(),
  );
}

// 政策复制 - 单个城市信息
export async function fetchPolicyCity(cityName: string): Promise<unknown> {
  return withSource(
    apiFetch(`/policy-replication/city/${encodeURIComponent(cityName)}`),
    () => {
      const cities = mockPolicyCities().cities;
      return cities.find(c => c.city === cityName) || cities[0];
    },
  );
}

// 政策复制 - 1039政策解读
export async function fetchPolicyGuide(): Promise<PolicyGuideData> {
  return withSource(
    apiFetch<PolicyGuideData>('/policy-replication/policy-guide'),
    () => mockPolicyGuide(),
  );
}

// 政策复制 - 政策红利计算
export async function calculatePolicyBenefit(req: { annual_export: number; category: string; city: string }): Promise<PolicyBenefitData> {
  return withSource(
    apiFetch<PolicyBenefitData>('/policy-replication/calculate-benefit', { method: 'POST', body: JSON.stringify(req) }),
    () => mockPolicyBenefit(req.annual_export, req.category, req.city),
  );
}

// 政策复制 - 义乌成功案例
export async function fetchPolicyCases(): Promise<{ cases: PolicyCaseData[] }> {
  return withSource(
    apiFetch<{ cases: PolicyCaseData[] }>('/policy-replication/cases'),
    () => mockPolicyCases(),
  );
}

// ==================== 系统真实状态（不做 mock 兜底，拿不到即 null） ====================

export interface SystemStatus {
  service: string;
  version: string;
  agents: Record<string, string>;
  agent_engines: Record<string, string>;
  llm_configured: boolean;   // AI 增强是否真正生效（后端已配置 LLM_API_KEY）
  data_mode: string;         // 诚实标注：hybrid(Nreal)=已接入N个真实源 / static-demo=全演示
  ai_enhanced_count: number; // 真正接入 LLM 的 Agent 数
  data_sources: number;
  real_source_count?: number; // P1-1：真实接入的外部数据源数量
  real_data_sources?: {       // P1-1：逐源真实状态（可自证）
    source: string; is_real: boolean; age_seconds: number | null;
    is_fresh: boolean; source_url: string; fetched_at_iso: string; error: string;
  }[];
}

/**
 * 拉取后端真实系统状态。失败返回 null（由调用方显示"待检测"），
 * 绝不回退到假数据，避免顶栏"全部在线/AI已接入"说谎。
 */
export async function fetchSystemStatus(): Promise<SystemStatus | null> {
  try {
    return await apiFetch<SystemStatus>('/status', { timeout: 8000 });
  } catch {
    return null;
  }
}

// ==================== P3-5 商业化：定价/支付/转化 ====================

export interface PricingPlan {
  code: string;
  name: string;
  price_cny: number;
  price_display: string;
  period: string;
  description: string;
  features: string[];
  highlight: boolean;
  cta: string;
  duration_days: number;
}

export interface PricingPlansResponse {
  plans: PricingPlan[];
  variant: string;
  variant_label: string;
  layout: string;
  experiment: string;
}

export interface CheckoutResult {
  success: boolean;
  order_no: string;
  amount_cny: number;
  plan_name: string;
  plan_code: string;
  status: string;
  provider: string;
  pay_method: string;
  pay_url: string;
  expires_in_seconds: number;
  note: string;
}

export interface PaymentConfirmResult {
  success: boolean;
  order_no: string;
  status: string;
  plan_code: string;
  plan_name: string;
  subscription_id: number;
  expires_at: number;
}

export interface OrderRecord {
  id: number;
  order_no: string;
  user_email: string;
  plan_code: string;
  amount_cny: number;
  status: string;
  provider: string;
  pay_method: string;
  created_at: number;
  paid_at: number | null;
}

export interface SubscriptionRecord {
  id: number;
  user_email: string;
  plan_code: string;
  status: string;
  started_at: number;
  expires_at: number;
  payment_order_id: string;
}

export interface FunnelSummary {
  events: Record<string, number>;
  conversion_rate: number;
  checkout_rate: number;
  payment_rate: number;
  total_events: number;
  hours: number;
}

/** 获取套餐列表 + A/B 变体（无需登录） */
export async function fetchPricingPlans(sessionId: string = ''): Promise<PricingPlansResponse> {
  const qs = sessionId ? `?session_id=${encodeURIComponent(sessionId)}` : '';
  return apiFetch<PricingPlansResponse>(`/pricing/plans${qs}`);
}

/** 记录转化事件（无需登录，匿名也可埋点） */
export async function trackConversionEvent(
  eventType: string, planCode: string = '', sessionId: string = '', metadata: Record<string, unknown> = {},
): Promise<{ success: boolean; event_id: number }> {
  return apiFetch<{ success: boolean; event_id: number }>('/pricing/track', {
    method: 'POST',
    body: JSON.stringify({ event_type: eventType, plan_code: planCode, session_id: sessionId, metadata }),
  });
}

/** 创建沙箱支付订单（需登录） */
export async function createCheckout(planCode: string, payMethod: string = 'alipay_sandbox'): Promise<CheckoutResult> {
  return apiFetch<CheckoutResult>('/pricing/checkout', {
    method: 'POST',
    body: JSON.stringify({ plan_code: planCode, pay_method: payMethod }),
  });
}

/** 确认沙箱支付（需登录） */
export async function confirmPayment(orderNo: string, payMethod: string = 'alipay_sandbox'): Promise<PaymentConfirmResult> {
  return apiFetch<PaymentConfirmResult>('/pricing/payment-callback', {
    method: 'POST',
    body: JSON.stringify({ order_no: orderNo, pay_method: payMethod }),
  });
}

/** 获取当前用户订单列表（需登录） */
export async function fetchOrders(): Promise<{ orders: OrderRecord[] }> {
  return apiFetch<{ orders: OrderRecord[] }>('/pricing/orders');
}

/** 获取当前用户有效订阅（需登录） */
export async function fetchSubscription(): Promise<{ subscription: SubscriptionRecord | null }> {
  return apiFetch<{ subscription: SubscriptionRecord | null }>('/pricing/subscription');
}

/** 获取转化漏斗汇总（供评审展示真实数据驱动能力） */
export async function fetchFunnelSummary(hours: number = 24): Promise<FunnelSummary> {
  return apiFetch<FunnelSummary>(`/pricing/funnel?hours=${hours}`);
}
