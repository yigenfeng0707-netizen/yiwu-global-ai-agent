// P2-1: Pricing 页关键测试 —— 验证 SSOT 定价体系（¥199/¥299/¥999/¥5万）与 7大Agent 口径
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import Pricing from '../Pricing';

function renderPricing() {
  return render(
    <MemoryRouter>
      <Pricing />
    </MemoryRouter>,
  );
}

describe('Pricing page (SSOT 定价对齐)', () => {
  it('渲染四档定价且价格与核心数字基准表一致', () => {
    renderPricing();
    // JSX 渲染为 ¥{plan.price}，故断言带 ¥ 前缀
    // plan 名称在卡片/feature/对比表中多处出现，用 getAllByText 断言存在性
    expect(screen.getByText('义乌商户专享版')).toBeInTheDocument();
    expect(screen.getByText('¥199')).toBeInTheDocument();
    expect(screen.getAllByText('基础版').length).toBeGreaterThan(0);
    expect(screen.getByText('¥299')).toBeInTheDocument();
    expect(screen.getAllByText('高级版').length).toBeGreaterThan(0);
    expect(screen.getByText('¥999')).toBeInTheDocument();
    expect(screen.getAllByText('企业定制').length).toBeGreaterThan(0);
    expect(screen.getByText('¥5万')).toBeInTheDocument();
  });

  it('高级版功能列表提及 7大Agent（废弃6大口径）', () => {
    renderPricing();
    expect(screen.getByText(/7大Agent/)).toBeInTheDocument();
  });

  it('义乌商户专享版标记为 highlight 首选', () => {
    renderPricing();
    expect(screen.getByText('义乌商户首选')).toBeInTheDocument();
  });
});
