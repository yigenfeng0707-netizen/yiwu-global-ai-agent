import { useState, useEffect } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import {
  BarChart3, Target, FileText, Shield, Headphones, Truck,
  Home, Layers, CreditCard, LogIn, LogOut, Menu, X,
  Train, Database, Building2,
} from 'lucide-react';
import { useStore } from '@/store/useStore';
import DataSourceBadge from '@/components/DataSourceBadge';
import { fetchSystemStatus, type SystemStatus } from '@/utils/api';

const navItems = [
  { label: '首页', icon: Home, path: '/' },
  { label: '市场洞察', icon: BarChart3, path: '/market-insight' },
  { label: '智能选品', icon: Target, path: '/smart-selection' },
  { label: '供应链匹配', icon: Truck, path: '/supply-chain' },
  { label: '内容生成', icon: FileText, path: '/content-generation' },
  { label: '合规助手', icon: Shield, path: '/compliance' },
  { label: '智能客服', icon: Headphones, path: '/customer-service' },
  { label: '政策复制', icon: Building2, path: '/policy-replication' },
  { label: '全链路', icon: Layers, path: '/pipeline' },
  { label: '套餐价格', icon: CreditCard, path: '/pricing' },
];

// 数据源名称（真实在线状态由后端 /status 决定，不再前端硬编码 online）
const dataSourceNames = ['义乌小商品城', '义新欧班列', 'Amazon', 'Alibaba.com', '行业报告'];

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { isAuthenticated, user, logout } = useStore();
  const [sysStatus, setSysStatus] = useState<SystemStatus | null>(null);

  useEffect(() => {
    let mounted = true;
    fetchSystemStatus().then((s) => { if (mounted) setSysStatus(s); });
    return () => { mounted = false; };
  }, []);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 transform bg-ocean-900 border-r border-white/5 transition-transform duration-200 lg:relative lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex items-center gap-3 px-6 py-5 border-b border-white/5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-yiwu-500/20">
              <Train size={20} className="text-yiwu-500" />
            </div>
            <div>
              <h1 className="font-display text-base text-white leading-tight">义乌小商品出海</h1>
              <p className="text-xs text-gray-500">AI Agent</p>
            </div>
            <button
              className="ml-auto lg:hidden text-gray-400 hover:text-white"
              onClick={() => setSidebarOpen(false)}
            >
              <X size={18} />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
                    isActive
                      ? 'bg-yiwu-500/10 text-yiwu-400'
                      : 'text-gray-400 hover:bg-white/5 hover:text-white'
                  }`
                }
              >
                <item.icon size={18} />
                {item.label}
              </NavLink>
            ))}
          </nav>

          {/* Data Source Status（真实状态来自后端 /status，不再硬编码 online） */}
          <div className="border-t border-white/5 px-4 py-3">
            <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
              <Database size={12} /> 数据源
              {sysStatus ? (
                <span
                  className="ml-auto text-[10px] text-gold-400/80"
                  title="当前为静态演示数据，非实时接入的外部数据管道"
                >
                  {sysStatus.data_mode === 'static-demo' ? '演示数据' : sysStatus.data_mode}
                </span>
              ) : (
                <span className="ml-auto text-[10px] text-gray-600">待检测</span>
              )}
            </p>
            <div className="space-y-1">
              {dataSourceNames.map((name) => (
                <div key={name} className="flex items-center gap-2 text-xs">
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${sysStatus ? 'bg-gold-500' : 'bg-gray-600'}`}
                    title={sysStatus ? '演示数据（后端可达）' : '后端状态待检测'}
                  />
                  <span className="text-gray-500">{name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* User */}
          <div className="border-t border-white/5 px-4 py-3">
            {isAuthenticated ? (
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">{user?.email}</span>
                <button onClick={logout} className="ml-auto text-gray-500 hover:text-white">
                  <LogOut size={14} />
                </button>
              </div>
            ) : (
              <NavLink
                to="/login"
                className="flex items-center gap-2 text-xs text-gray-400 hover:text-white"
              >
                <LogIn size={14} /> 登录
              </NavLink>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="flex items-center justify-between border-b border-white/5 px-6 py-3 bg-ocean-900/50">
          <div className="flex items-center gap-3">
            <button
              className="lg:hidden text-gray-400 hover:text-white"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu size={20} />
            </button>
            <span className="text-sm text-gray-400">义乌国际商贸城 · 小商品跨境出海智能助手</span>
          </div>
          <div className="flex items-center gap-3 text-xs text-gray-500">
            <DataSourceBadge />
            {sysStatus ? (
              <span
                className="hidden sm:inline"
                title="7 个 Agent 中真正接入大模型（LLM）的数量，以及 AI 增强是否已启用"
              >
                {sysStatus.ai_enhanced_count}/7 Agent · AI增强{sysStatus.llm_configured ? '已启用' : '未启用'}
              </span>
            ) : (
              <span className="hidden sm:inline text-gray-600">状态检测中…</span>
            )}
            <span className={`h-2 w-2 rounded-full ${sysStatus ? 'bg-yiwu-500' : 'bg-gray-600'}`} />
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
