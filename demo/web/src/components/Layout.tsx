import { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import {
  BarChart3, Target, FileText, Shield, Headphones, Truck,
  Home, Layers, CreditCard, LogIn, LogOut, Menu, X,
  Train, Database, Building2,
} from 'lucide-react';
import { useStore } from '@/store/useStore';

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

const dataSourceStatus = [
  { name: '义乌小商品城', status: 'online' },
  { name: '义新欧班列', status: 'online' },
  { name: 'Amazon', status: 'online' },
  { name: 'Alibaba.com', status: 'online' },
  { name: '行业报告', status: 'online' },
];

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { isAuthenticated, user, logout } = useStore();

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

          {/* Data Source Status */}
          <div className="border-t border-white/5 px-4 py-3">
            <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
              <Database size={12} /> 数据源状态
            </p>
            <div className="space-y-1">
              {dataSourceStatus.map((ds) => (
                <div key={ds.name} className="flex items-center gap-2 text-xs">
                  <span className={`h-1.5 w-1.5 rounded-full ${ds.status === 'online' ? 'bg-yiwu-500' : 'bg-gold-500'}`} />
                  <span className="text-gray-500">{ds.name}</span>
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
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span className="hidden sm:inline">7 Agents 在线</span>
            <span className="h-2 w-2 rounded-full bg-yiwu-500" />
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
