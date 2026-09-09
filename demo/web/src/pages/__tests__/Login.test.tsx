// P2-1: Login 页关键测试 —— 表单元素渲染 + Tab 切换改变表单内容 + 密码切换 a11y
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import Login from '../Login';

function renderLogin() {
  return render(
    <MemoryRouter>
      <Login />
    </MemoryRouter>,
  );
}

describe('Login page (认证表单)', () => {
  it('渲染邮箱与密码输入框', () => {
    renderLogin();
    expect(screen.getByPlaceholderText(/邮箱/)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/密码/)).toBeInTheDocument();
  });

  it('切换到注册 Tab 后出现确认密码字段（表单内容随 Tab 变化）', async () => {
    const user = userEvent.setup();
    renderLogin();
    // 登录模式下无确认密码字段
    expect(screen.queryByPlaceholderText(/确认密码/)).not.toBeInTheDocument();
    // 点击注册 Tab（tab 按钮文本为"注册"，与 submit 按钮区分：submit 初始为"登录"）
    const registerTabs = screen.getAllByText('注册');
    // 第一个是 Tab 按钮（在 Tabs 区域），点击它
    await user.click(registerTabs[0]);
    // 注册模式下应出现确认密码字段
    expect(screen.getByPlaceholderText(/确认密码/)).toBeInTheDocument();
  });

  it('密码字段有显示/隐藏切换且带 aria-label（P2-6 a11y 补齐验证）', () => {
    renderLogin();
    // 初始状态为"显示密码"（showPwd=false）
    const toggle = screen.getByLabelText('显示密码');
    expect(toggle).toBeInTheDocument();
  });
});
