import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, Building, Eye, EyeOff, Train, Globe, ShieldCheck } from 'lucide-react';
import { useStore } from '@/store/useStore';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

type Tab = 'login' | 'register';

const inputCls =
  'w-full rounded-lg border border-white/10 bg-ocean-800 px-4 py-2.5 text-sm text-white placeholder-gray-500 outline-none transition focus:border-yiwu-500 focus:ring-1 focus:ring-yiwu-500/30';

function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export default function Login() {
  const [tab, setTab] = useState<Tab>('login');
  const [showPwd, setShowPwd] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [company, setCompany] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [registerSuccess, setRegisterSuccess] = useState(false);
  const navigate = useNavigate();
  const login = useStore((s) => s.login);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setRegisterSuccess(false);

    if (!validateEmail(email)) {
      setError('请输入有效的邮箱地址');
      return;
    }
    if (password.length < 6) {
      setError('密码长度不能少于6位');
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (data.token) {
        localStorage.setItem('yiwu_token', data.token);
        login({
          id: 'user_' + Date.now(),
          email: data.email || email,
          company: company || '',
          plan: 'free',
        });
        navigate('/');
      } else {
        setError(data.detail || data.message || '邮箱或密码错误');
      }
    } catch {
      const users = JSON.parse(localStorage.getItem('yiwu_users') || '[]');
      const user = users.find((u: { email: string; password: string }) => u.email === email && u.password === password);
      if (user) {
        login({ id: user.id, email: user.email, company: user.company, plan: user.plan });
        navigate('/');
      } else {
        setError('邮箱或密码错误');
      }
    }
    setLoading(false);
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!company.trim()) {
      setError('请输入公司名称');
      return;
    }
    if (!validateEmail(email)) {
      setError('请输入有效的邮箱地址');
      return;
    }
    if (password.length < 6) {
      setError('密码长度不能少于6位');
      return;
    }
    if (password !== confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (data.success) {
        // 后端注册成功
      } else {
        setError(data.detail || data.message || '注册失败');
        setLoading(false);
        return;
      }
    } catch {
      const users = JSON.parse(localStorage.getItem('yiwu_users') || '[]');
      if (users.some((u: { email: string }) => u.email === email)) {
        setError('该邮箱已注册，请直接登录');
        setLoading(false);
        return;
      }
      users.push({
        email,
        password,
        company: company.trim(),
        id: 'user_' + Date.now(),
        plan: 'free',
        createdAt: new Date().toISOString(),
      });
      localStorage.setItem('yiwu_users', JSON.stringify(users));
    }

    setLoading(false);
    setTab('login');
    setError('');
    setPassword('');
    setCompany('');
    setConfirmPassword('');
    setRegisterSuccess(true);
  };

  const switchTab = (t: Tab) => {
    setTab(t);
    setError('');
    setRegisterSuccess(false);
    setEmail('');
    setPassword('');
    setCompany('');
    setConfirmPassword('');
  };

  return (
    <div className="flex min-h-[calc(100vh-8rem)] items-center justify-center">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex w-full max-w-4xl overflow-hidden rounded-2xl border border-white/5"
      >
        {/* Decorative Side Panel */}
        <div className="hidden lg:flex w-80 flex-col justify-between bg-gradient-to-br from-ocean-800 to-ocean-950 p-8">
          <div>
            <div className="flex items-baseline gap-1 mb-6">
              <span className="font-display text-2xl text-yiwu-500">义乌小商品出海</span>
            </div>
            <p className="text-sm text-gray-400 leading-relaxed">
              基于义乌国际商贸城7.5万商户、210万+SKU，义新欧班列直达欧洲，为跨境电商提供一站式AI智能服务
            </p>
          </div>
          <div className="space-y-4">
            {[
              { icon: Globe, text: '7.5万商户 210万+SKU' },
              { icon: ShieldCheck, text: '1039市场采购贸易' },
              { icon: Train, text: '义新欧班列直达欧洲' },
            ].map((item) => (
              <div key={item.text} className="flex items-center gap-3 text-sm text-gray-400">
                <item.icon size={18} className="text-yiwu-500" />
                <span>{item.text}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Form Area */}
        <div className="flex-1 glass-light p-8">
          {/* Tabs */}
          <div className="mb-6 flex gap-1 rounded-lg bg-ocean-800 p-1">
            {(['login', 'register'] as Tab[]).map((t) => (
              <button
                key={t}
                onClick={() => switchTab(t)}
                className={`flex-1 rounded-md py-2 text-sm font-medium transition ${
                  tab === t ? 'bg-yiwu-500/20 text-yiwu-400' : 'text-gray-400 hover:text-white'
                }`}
              >
                {t === 'login' ? '登录' : '注册'}
              </button>
            ))}
          </div>

          {/* Register Success Message */}
          {registerSuccess && (
            <div className="mb-4 rounded-lg bg-yiwu-500/10 border border-yiwu-500/20 px-4 py-2 text-sm text-yiwu-400">
              注册成功！请使用注册的账号登录
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-4 rounded-lg bg-red-500/10 border border-red-500/20 px-4 py-2 text-sm text-red-400">
              {error}
            </div>
          )}

          {tab === 'login' ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="relative">
                <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={`${inputCls} pl-10`}
                  placeholder="邮箱"
                  required
                />
              </div>
              <div className="relative">
                <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type={showPwd ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={`${inputCls} pl-10 pr-10`}
                  placeholder="密码"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPwd(!showPwd)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                >
                  {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              <div className="flex items-center justify-between text-xs">
                <label className="flex items-center gap-2 text-gray-400">
                  <input type="checkbox" className="rounded border-white/20 bg-ocean-800 text-yiwu-500" />
                  记住我
                </label>
                <button type="button" className="text-yiwu-400 hover:text-yiwu-300">
                  忘记密码？
                </button>
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-lg bg-gradient-to-r from-yiwu-500 to-yiwu-400 py-2.5 text-sm font-medium text-white transition hover:from-yiwu-400 hover:to-yiwu-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? '登录中...' : '登录'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="space-y-4">
              <div className="relative">
                <Building size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className={`${inputCls} pl-10`}
                  placeholder="公司名称"
                  required
                />
              </div>
              <div className="relative">
                <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={`${inputCls} pl-10`}
                  placeholder="邮箱"
                  required
                />
              </div>
              <div className="relative">
                <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type={showPwd ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={`${inputCls} pl-10 pr-10`}
                  placeholder="密码"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPwd(!showPwd)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                >
                  {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              <div className="relative">
                <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className={`${inputCls} pl-10`}
                  placeholder="确认密码"
                  required
                />
              </div>
              <label className="flex items-start gap-2 text-xs text-gray-400">
                <input type="checkbox" className="mt-0.5 rounded border-white/20 bg-ocean-800 text-yiwu-500" />
                我已阅读并同意《服务协议》和《隐私政策》
              </label>
              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-lg bg-gradient-to-r from-yiwu-500 to-yiwu-400 py-2.5 text-sm font-medium text-white transition hover:from-yiwu-400 hover:to-yiwu-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? '注册中...' : '注册'}
              </button>
            </form>
          )}

          <div className="mt-6 text-center">
            <button
              onClick={() => navigate('/pricing')}
              className="text-xs text-gold-400 hover:text-gold-300 transition"
            >
              免费体验 →
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
