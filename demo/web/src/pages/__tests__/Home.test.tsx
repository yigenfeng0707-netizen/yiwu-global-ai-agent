// P2-1: Home 页关键测试 —— 品类导航渲染 + 10大核心品类覆盖
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import Home from '../Home';

function renderHome() {
  return render(
    <MemoryRouter>
      <Home />
    </MemoryRouter>,
  );
}

describe('Home page (品类导航)', () => {
  it('渲染品类导航区块', () => {
    renderHome();
    expect(screen.getByText('品类导航')).toBeInTheDocument();
  });

  it('展示义乌10大核心品类中的代表性品类', () => {
    renderHome();
    // 抽查 CATEGORY_LIST 权威名单中的品类（与后端 market_data.py 一致）
    expect(screen.getByText('日用百货')).toBeInTheDocument();
    expect(screen.getByText('饰品配件')).toBeInTheDocument();
    expect(screen.getByText('玩具')).toBeInTheDocument();
  });

  it('品类卡片带无障碍 aria-label（P2-6 a11y 补齐验证）', () => {
    renderHome();
    // 10 个品类卡片均带 aria-label，用 getAllByLabelText 断言全覆盖
    const cards = screen.getAllByLabelText(/查看.+品类的市场洞察/);
    expect(cards.length).toBe(10);
  });
});
