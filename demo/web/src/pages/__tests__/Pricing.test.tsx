// P3-5: Pricing 页测试 — 验证 SSOT 定价体系 + A/B 变体 + API 驱动渲染
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import Pricing from '../Pricing';

// Mock API: 返回 variant_a 布局（与原静态布局一致）
vi.mock('@/utils/api', () => ({
  fetchPricingPlans: vi.fn().mockResolvedValue({
    plans: [
      { code: 'yiwu_merchant', name: '义乌商户专享版', price_cny: 199, price_display: '199', period: '元/月', description: '义乌国际商贸城商户专属普惠价', features: ['高级版全部功能', '义乌专属数据', '供应链优先匹配', '1039合规指导', '义新欧班列专享运价'], highlight: true, cta: '义乌商户首选', duration_days: 30 },
      { code: 'basic', name: '基础版', price_cny: 299, price_display: '299', period: '元/月', description: '适合小微企业和个人卖家', features: ['市场洞察报告', '智能选品推荐', '跨境内容生成', '10大品类覆盖', '8种语言支持'], highlight: false, cta: '立即订阅', duration_days: 30 },
      { code: 'pro', name: '高级版', price_cny: 999, price_display: '999', period: '元/月', description: '适合成长型电商企业', features: ['基础版全部功能', '供应链匹配(7大Agent)', '合规助手(15国)', '智能客服(7x24h)', '义新欧班列物流'], highlight: false, cta: '立即订阅', duration_days: 30 },
      { code: 'enterprise', name: '企业定制', price_cny: 50000, price_display: '5万', period: '起/年', description: '适合大型企业和团队', features: ['高级版全部功能', '私有化部署', '定制Agent开发', 'API接口对接', '专属客户经理'], highlight: false, cta: '联系我们', duration_days: 365 },
    ],
    variant: 'variant_a',
    variant_label: '推荐布局A',
    layout: 'grid-3',
    experiment: 'pricing_layout',
  }),
  trackConversionEvent: vi.fn().mockResolvedValue({ success: true, event_id: 1 }),
  createCheckout: vi.fn(),
  confirmPayment: vi.fn(),
  fetchOrders: vi.fn().mockResolvedValue({ orders: [] }),
  fetchSubscription: vi.fn().mockResolvedValue({ subscription: null }),
  fetchFunnelSummary: vi.fn().mockRejectedValue(new Error('no data')),
}));

// Mock store
vi.mock('@/store/useStore', () => ({
  useStore: () => ({ isAuthenticated: false, user: null }),
}));

function renderPricing() {
  return render(
    <MemoryRouter>
      <Pricing />
    </MemoryRouter>,
  );
}

describe('Pricing page (SSOT 定价对齐 + API 驱动)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('渲染四档定价且价格与核心数字基准表一致', async () => {
    renderPricing();
    // API 异步加载后验证
    await waitFor(() => {
      expect(screen.getByText('义乌商户专享版')).toBeInTheDocument();
    }, { timeout: 3000 });

    expect(screen.getByText('¥199')).toBeInTheDocument();
    expect(screen.getAllByText('基础版').length).toBeGreaterThan(0);
    expect(screen.getByText('¥299')).toBeInTheDocument();
    expect(screen.getAllByText('高级版').length).toBeGreaterThan(0);
    expect(screen.getByText('¥999')).toBeInTheDocument();
    expect(screen.getAllByText('企业定制').length).toBeGreaterThan(0);
    expect(screen.getByText('¥5万')).toBeInTheDocument();
  });

  it('高级版功能列表提及 7大Agent（废弃6大口径）', async () => {
    renderPricing();
    await waitFor(() => {
      expect(screen.getByText(/7大Agent/)).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('义乌商户专享版标记为 highlight 首选', async () => {
    renderPricing();
    await waitFor(() => {
      expect(screen.getByText('义乌商户首选')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('A/B 测试变体标签展示', async () => {
    renderPricing();
    await waitFor(() => {
      expect(screen.getByText(/A\/B测试已激活/)).toBeInTheDocument();
    }, { timeout: 3000 });
  });
});
