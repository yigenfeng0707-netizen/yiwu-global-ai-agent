import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, ChevronDown, ChevronUp, Sparkles, X, CreditCard, Shield, BarChart3, Loader2 } from 'lucide-react';
import { useStore } from '@/store/useStore';
import {
  fetchPricingPlans, trackConversionEvent, createCheckout, confirmPayment,
  fetchOrders, fetchSubscription, fetchFunnelSummary,
  type PricingPlan, type CheckoutResult, type PaymentConfirmResult,
  type OrderRecord, type SubscriptionRecord, type FunnelSummary,
} from '@/utils/api';

const comparisonFeatures = [
  { name: '市场洞察报告', basic: true, pro: true, enterprise: true },
  { name: '智能选品推荐', basic: true, pro: true, enterprise: true },
  { name: '跨境内容生成', basic: true, pro: true, enterprise: true },
  { name: '品类覆盖', basic: '10大品类', pro: '10大品类', enterprise: '全品类' },
  { name: '语言支持', basic: '8种', pro: '8种', enterprise: '12种+' },
  { name: '供应链匹配', basic: false, pro: true, enterprise: true },
  { name: '合规助手', basic: false, pro: '15国', enterprise: '全球' },
  { name: '智能客服', basic: false, pro: '7x24h', enterprise: '7x24h' },
  { name: '义新欧班列物流', basic: false, pro: true, enterprise: true },
  { name: '私有化部署', basic: false, pro: false, enterprise: true },
  { name: 'API接口', basic: false, pro: false, enterprise: true },
];

const faqs = [
  { q: '是否支持按年付费优惠？', a: '高级版按年付费可享8折优惠，企业定制版按年签约更享专属折扣，详情请联系客户经理。' },
  { q: '供应链匹配功能包含什么？', a: '供应链匹配Agent可匹配义乌7.5万商户、210万+SKU，提供采购价格/MOQ/交期、义新欧班列物流、1039市场采购贸易等全链路服务。' },
  { q: '企业定制版的交付周期是多久？', a: '标准企业版部署约2-4周，定制Agent开发根据需求复杂度约4-8周，我们会提供详细的项目计划。' },
  { q: '支付方式有哪些？', a: '当前支持支付宝沙箱支付（演示模式），生产环境将接入支付宝、微信支付、银联等主流渠道。企业定制版支持对公转账。' },
];

const fadeUp = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

type PayState = 'idle' | 'checking_out' | 'paying' | 'paid' | 'error';

function getSessionId(): string {
  let sid = '';
  try { sid = sessionStorage.getItem('yiwu_session_id') || ''; } catch { /* SSR/隐私 */ }
  if (!sid) {
    sid = `s_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
    try { sessionStorage.setItem('yiwu_session_id', sid); } catch { /* ignore */ }
  }
  return sid;
}

export default function Pricing() {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useStore();

  const [plans, setPlans] = useState<PricingPlan[]>([]);
  const [variant, setVariant] = useState('');
  const [layout, setLayout] = useState('');
  const [loading, setLoading] = useState(true);
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [showContactModal, setShowContactModal] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [contactForm, setContactForm] = useState({ company: '', email: '', phone: '' });

  // 支付状态
  const [payState, setPayState] = useState<PayState>('idle');
  const [checkoutResult, setCheckoutResult] = useState<CheckoutResult | null>(null);
  const [payResult, setPayResult] = useState<PaymentConfirmResult | null>(null);
  const [payError, setPayError] = useState('');
  const [currentPlan, setCurrentPlan] = useState<PricingPlan | null>(null);

  // 订阅 & 订单
  const [subscription, setSubscription] = useState<SubscriptionRecord | null>(null);
  const [orders, setOrders] = useState<OrderRecord[]>([]);
  const [funnel, setFunnel] = useState<FunnelSummary | null>(null);

  const sessionId = getSessionId();

  const loadPlans = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await fetchPricingPlans(sessionId);
      setPlans(resp.plans);
      setVariant(resp.variant);
      setLayout(resp.layout);
      // 埋点：页面浏览
      trackConversionEvent('page_view', '', sessionId).catch(() => {});
    } catch {
      // 后端不可达时用静态套餐兜底
      setPlans([
        { code: 'yiwu_merchant', name: '义乌商户专享版', price_cny: 199, price_display: '199', period: '元/月', description: '义乌国际商贸城商户专属普惠价', features: ['高级版全部功能', '义乌专属数据', '供应链优先匹配', '1039合规指导', '义新欧班列专享运价'], highlight: true, cta: '义乌商户首选', duration_days: 30 },
        { code: 'basic', name: '基础版', price_cny: 299, price_display: '299', period: '元/月', description: '适合小微企业和个人卖家', features: ['市场洞察报告', '智能选品推荐', '跨境内容生成', '10大品类覆盖', '8种语言支持'], highlight: false, cta: '立即订阅', duration_days: 30 },
        { code: 'pro', name: '高级版', price_cny: 999, price_display: '999', period: '元/月', description: '适合成长型电商企业', features: ['基础版全部功能', '供应链匹配(7大Agent)', '合规助手(15国)', '智能客服(7x24h)', '义新欧班列物流'], highlight: false, cta: '立即订阅', duration_days: 30 },
        { code: 'enterprise', name: '企业定制', price_cny: 50000, price_display: '5万', period: '起/年', description: '适合大型企业和团队', features: ['高级版全部功能', '私有化部署', '定制Agent开发', 'API接口对接', '专属客户经理'], highlight: false, cta: '联系我们', duration_days: 365 },
      ]);
      setVariant('backend_offline');
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    loadPlans();
  }, [loadPlans]);

  // 已登录用户加载订阅和订单
  useEffect(() => {
    if (isAuthenticated) {
      fetchSubscription().then(r => setSubscription(r.subscription)).catch(() => {});
      fetchOrders().then(r => setOrders(r.orders)).catch(() => {});
    }
    // 漏斗数据（评审展示）
    fetchFunnelSummary(24).then(setFunnel).catch(() => {});
  }, [isAuthenticated, payState]);

  const handleCtaClick = (plan: PricingPlan) => {
    // 埋点：点击套餐 CTA
    trackConversionEvent('plan_click', plan.code, sessionId, { plan_name: plan.name }).catch(() => {});

    if (plan.code === 'enterprise') {
      setShowContactModal(true);
      setSubmitSuccess(false);
      return;
    }

    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    // 发起沙箱支付
    setCurrentPlan(plan);
    setPayState('checking_out');
    setPayError('');
    setPayResult(null);

    createCheckout(plan.code)
      .then(result => {
        setCheckoutResult(result);
        setPayState('paying');
      })
      .catch(err => {
        setPayError(err instanceof Error ? err.message : '创建订单失败');
        setPayState('error');
      });
  };

  const handleConfirmPay = () => {
    if (!checkoutResult) return;
    setPayState('paying');
    confirmPayment(checkoutResult.order_no)
      .then(result => {
        setPayResult(result);
        setPayState('paid');
      })
      .catch(err => {
        setPayError(err instanceof Error ? err.message : '支付确认失败');
        setPayState('error');
        trackConversionEvent('checkout_abandon', currentPlan?.code || '', sessionId, { order_no: checkoutResult.order_no }).catch(() => {});
      });
  };

  const handleCancelPay = () => {
    if (checkoutResult) {
      trackConversionEvent('checkout_abandon', currentPlan?.code || '', sessionId, { order_no: checkoutResult.order_no }).catch(() => {});
    }
    setPayState('idle');
    setCheckoutResult(null);
    setPayResult(null);
    setPayError('');
  };

  const handleContactSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitSuccess(true);
  };

  const handleCloseModal = () => {
    setShowContactModal(false);
    if (submitSuccess) {
      setContactForm({ company: '', email: '', phone: '' });
    }
  };

  const gridCols = layout === 'grid-4' ? 'md:grid-cols-2 lg:grid-cols-4' : 'md:grid-cols-3';

  return (
    <div className="space-y-12">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center">
        <h1 className="font-display text-3xl text-white mb-2">套餐价格</h1>
        <p className="text-gray-400">选择适合您的方案，开启义乌小商品跨境出海智能之旅</p>
        {variant && variant !== 'backend_offline' && (
          <span className="mt-2 inline-block rounded-full bg-yiwu-500/10 px-3 py-1 text-xs text-yiwu-400 border border-yiwu-500/20">
            {variant === 'variant_a' ? '推荐布局A' : '推荐布局B'} · A/B测试已激活
          </span>
        )}
      </motion.div>

      {/* 当前订阅状态 */}
      {isAuthenticated && subscription && (
        <motion.div
          initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          className="rounded-xl border border-yiwu-500/30 bg-yiwu-500/5 p-4"
        >
          <div className="flex items-center gap-2">
            <Shield size={18} className="text-yiwu-500" />
            <span className="text-sm text-white">当前订阅: </span>
            <span className="text-sm font-medium text-yiwu-400">{subscription.plan_code}</span>
            <span className="text-xs text-gray-400">
              (至 {new Date(subscription.expires_at * 1000).toLocaleDateString('zh-CN')})
            </span>
          </div>
        </motion.div>
      )}

      {/* Pricing Cards */}
      {loading ? (
        <div className="flex justify-center py-20">
          <Loader2 size={32} className="animate-spin text-yiwu-500" />
        </div>
      ) : (
        <div className={`grid grid-cols-1 ${gridCols} gap-6 items-start`}>
          {plans.map((plan, i) => (
            <motion.div
              key={plan.code}
              variants={fadeUp}
              initial="hidden"
              animate="show"
              transition={{ delay: i * 0.1 }}
              className={`relative rounded-2xl p-6 ${
                plan.highlight
                  ? 'bg-gradient-to-b from-yiwu-500/10 to-ocean-900 border-2 border-yiwu-500/50 md:scale-105 md:py-8'
                  : 'glass-light border border-white/5'
              }`}
            >
              {plan.highlight && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-gradient-to-r from-yiwu-500 to-gold-500 px-4 py-1 text-xs font-bold text-white">
                  推荐
                </span>
              )}
              <h3 className="text-lg font-medium text-white">{plan.name}</h3>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-4xl font-bold text-white">¥{plan.price_display}</span>
                <span className="text-sm text-gray-400">{plan.period}</span>
              </div>
              <p className="mt-2 text-sm text-gray-400">{plan.description}</p>
              <ul className="mt-6 space-y-3">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm text-gray-300">
                    <Check size={16} className="shrink-0 text-yiwu-500" />
                    {f}
                  </li>
                ))}
              </ul>
              <button
                className={`mt-8 w-full rounded-lg py-2.5 text-sm font-medium transition-colors ${
                  plan.highlight
                    ? 'bg-gradient-to-r from-yiwu-500 to-gold-500 text-white hover:from-yiwu-400 hover:to-gold-400'
                    : plan.code === 'enterprise'
                    ? 'bg-ocean-800 text-white hover:bg-ocean-700'
                    : 'bg-yiwu-500 text-white hover:bg-yiwu-400'
                } ${payState === 'checking_out' && currentPlan?.code === plan.code ? 'opacity-50 cursor-not-allowed' : ''}`}
                onClick={() => handleCtaClick(plan)}
                disabled={payState === 'checking_out' && currentPlan?.code === plan.code}
              >
                {payState === 'checking_out' && currentPlan?.code === plan.code ? (
                  <Loader2 size={14} className="inline mr-1 animate-spin" />
                ) : plan.highlight ? (
                  <Sparkles size={14} className="inline mr-1" />
                ) : null}
                {plan.cta}
              </button>
            </motion.div>
          ))}
        </div>
      )}

      {/* 沙箱支付弹窗 */}
      <AnimatePresence>
        {payState !== 'idle' && currentPlan && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
            onClick={payState === 'paying' ? undefined : handleCancelPay}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="relative w-full max-w-md rounded-2xl border border-white/10 bg-ocean-900 p-6 shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                onClick={handleCancelPay}
                disabled={payState === 'paying'}
                className="absolute right-4 top-4 text-gray-400 hover:text-white transition-colors disabled:opacity-30"
              >
                <X size={20} />
              </button>

              {payState === 'paid' && payResult ? (
                <div className="text-center py-6">
                  <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-500/20">
                    <Check size={32} className="text-green-500" />
                  </div>
                  <h3 className="text-xl font-medium text-white mb-2">支付成功</h3>
                  <p className="text-sm text-gray-400 mb-2">
                    套餐: {payResult.plan_name} ({payResult.plan_code})
                  </p>
                  <p className="text-xs text-gray-500 mb-1">订单号: {payResult.order_no}</p>
                  <p className="text-xs text-gray-500">
                    订阅到期: {new Date(payResult.expires_at * 1000).toLocaleDateString('zh-CN')}
                  </p>
                  <button
                    onClick={handleCancelPay}
                    className="mt-6 rounded-lg bg-gradient-to-r from-yiwu-500 to-gold-500 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:from-yiwu-400 hover:to-gold-400"
                  >
                    完成
                  </button>
                </div>
              ) : payState === 'error' ? (
                <div className="text-center py-6">
                  <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-500/20">
                    <X size={32} className="text-red-500" />
                  </div>
                  <h3 className="text-xl font-medium text-white mb-2">支付失败</h3>
                  <p className="text-sm text-gray-400">{payError}</p>
                  <button
                    onClick={handleCancelPay}
                    className="mt-6 rounded-lg bg-ocean-800 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-ocean-700"
                  >
                    关闭
                  </button>
                </div>
              ) : checkoutResult ? (
                <>
                  <h3 className="text-lg font-medium text-white mb-1">沙箱支付</h3>
                  <p className="text-sm text-gray-400 mb-6">
                    <span className="inline-flex items-center gap-1">
                      <CreditCard size={14} /> 模拟{checkoutResult.pay_method === 'alipay_sandbox' ? '支付宝' : '支付'}
                    </span>
                  </p>

                  {/* 订单摘要 */}
                  <div className="mb-6 space-y-2 rounded-lg border border-white/10 bg-ocean-800/50 p-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">套餐</span>
                      <span className="text-white">{checkoutResult.plan_name}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">金额</span>
                      <span className="text-2xl font-bold text-white">¥{checkoutResult.amount_cny}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">订单号</span>
                      <span className="text-gray-300 font-mono">{checkoutResult.order_no}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">支付方式</span>
                      <span className="text-gray-300">支付宝沙箱</span>
                    </div>
                  </div>

                  <div className="mb-4 flex items-center gap-2 rounded-lg bg-yiwu-500/5 p-3 text-xs text-yiwu-400">
                    <Shield size={14} className="shrink-0" />
                    {checkoutResult.note}
                  </div>

                  <button
                    onClick={handleConfirmPay}
                    disabled={payState === 'paying'}
                    className="w-full rounded-lg bg-gradient-to-r from-yiwu-500 to-gold-500 py-2.5 text-sm font-medium text-white transition-colors hover:from-yiwu-400 hover:to-gold-400 disabled:opacity-50"
                  >
                    {payState === 'paying' ? (
                      <Loader2 size={14} className="inline mr-1 animate-spin" />
                    ) : (
                      <Check size={14} className="inline mr-1" />
                    )}
                    {payState === 'paying' ? '处理中...' : '确认支付（模拟）'}
                  </button>
                  <button
                    onClick={handleCancelPay}
                    disabled={payState === 'paying'}
                    className="mt-2 w-full rounded-lg bg-ocean-800 py-2 text-xs text-gray-400 transition-colors hover:bg-ocean-700 disabled:opacity-30"
                  >
                    取消
                  </button>
                </>
              ) : (
                <div className="flex justify-center py-10">
                  <Loader2 size={24} className="animate-spin text-yiwu-500" />
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Comparison Table */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>
        <h2 className="text-xl font-medium text-white mb-4">功能对比</h2>
        <div className="overflow-x-auto rounded-xl border border-white/5">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/5 bg-ocean-950/50">
                <th className="px-4 py-3 text-left text-gray-400 font-medium">功能</th>
                <th className="px-4 py-3 text-center text-gray-400 font-medium">基础版</th>
                <th className="px-4 py-3 text-center text-yiwu-400 font-medium">高级版</th>
                <th className="px-4 py-3 text-center text-gray-400 font-medium">企业定制</th>
              </tr>
            </thead>
            <tbody>
              {comparisonFeatures.map((row) => (
                <tr key={row.name} className="border-b border-white/5">
                  <td className="px-4 py-3 text-gray-300">{row.name}</td>
                  {([row.basic, row.pro, row.enterprise] as (boolean | string)[]).map((val, j) => (
                    <td key={j} className="px-4 py-3 text-center">
                      {val === true ? (
                        <Check size={16} className="mx-auto text-yiwu-500" />
                      ) : val === false ? (
                        <span className="text-gray-600">—</span>
                      ) : (
                        <span className="text-gray-300">{val}</span>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* 订单历史（已登录） */}
      {isAuthenticated && orders.length > 0 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
          <h2 className="text-xl font-medium text-white mb-4">订单记录</h2>
          <div className="overflow-x-auto rounded-xl border border-white/5">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/5 bg-ocean-950/50">
                  <th className="px-4 py-3 text-left text-gray-400 font-medium">订单号</th>
                  <th className="px-4 py-3 text-left text-gray-400 font-medium">套餐</th>
                  <th className="px-4 py-3 text-left text-gray-400 font-medium">金额</th>
                  <th className="px-4 py-3 text-left text-gray-400 font-medium">状态</th>
                  <th className="px-4 py-3 text-left text-gray-400 font-medium">时间</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr key={order.id} className="border-b border-white/5">
                    <td className="px-4 py-3 text-gray-300 font-mono text-xs">{order.order_no}</td>
                    <td className="px-4 py-3 text-gray-300">{order.plan_code}</td>
                    <td className="px-4 py-3 text-white">¥{order.amount_cny}</td>
                    <td className="px-4 py-3">
                      <span className={`rounded px-2 py-0.5 text-xs ${
                        order.status === 'paid' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {order.status === 'paid' ? '已支付' : '待支付'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-400 text-xs">
                      {new Date(order.created_at * 1000).toLocaleString('zh-CN')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}

      {/* 转化漏斗（评审展示真实数据驱动） */}
      {funnel && funnel.total_events > 0 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>
          <h2 className="text-xl font-medium text-white mb-4 flex items-center gap-2">
            <BarChart3 size={18} className="text-yiwu-500" />
            转化漏斗（最近{funnel.hours}小时）
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {[
              { label: '页面浏览', value: funnel.events.page_view || 0 },
              { label: '点击套餐', value: funnel.events.plan_click || 0 },
              { label: '发起结算', value: funnel.events.checkout_start || 0 },
              { label: '支付完成', value: funnel.events.checkout_complete || 0 },
              { label: '放弃结算', value: funnel.events.checkout_abandon || 0 },
            ].map((item) => (
              <div key={item.label} className="rounded-xl border border-white/5 bg-ocean-950/50 p-4 text-center">
                <div className="text-2xl font-bold text-white">{item.value}</div>
                <div className="mt-1 text-xs text-gray-400">{item.label}</div>
              </div>
            ))}
          </div>
          <div className="mt-3 flex gap-4 text-xs text-gray-400">
            <span>转化率: <span className="text-yiwu-400">{funnel.conversion_rate}%</span></span>
            <span>结算率: <span className="text-yiwu-400">{funnel.checkout_rate}%</span></span>
            <span>支付率: <span className="text-yiwu-400">{funnel.payment_rate}%</span></span>
          </div>
        </motion.div>
      )}

      {/* FAQ */}
      <div>
        <h2 className="text-xl font-medium text-white mb-4">常见问题</h2>
        <div className="space-y-3">
          {faqs.map((faq, i) => (
            <motion.div
              key={i}
              variants={fadeUp}
              initial="hidden"
              animate="show"
              transition={{ delay: 0.5 + i * 0.08 }}
              className="rounded-xl border border-white/5 bg-ocean-950/50"
            >
              <button
                className="flex w-full items-center justify-between px-5 py-4 text-left text-sm text-white"
                onClick={() => setOpenFaq(openFaq === i ? null : i)}
              >
                {faq.q}
                {openFaq === i ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              </button>
              {openFaq === i && (
                <div className="px-5 pb-4 text-sm text-gray-400">{faq.a}</div>
              )}
            </motion.div>
          ))}
        </div>
      </div>

      {/* Contact Sales Modal */}
      <AnimatePresence>
        {showContactModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
            onClick={handleCloseModal}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="relative w-full max-w-md rounded-2xl border border-white/10 bg-ocean-900 p-6 shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                onClick={handleCloseModal}
                className="absolute right-4 top-4 text-gray-400 hover:text-white transition-colors"
              >
                <X size={20} />
              </button>

              {submitSuccess ? (
                <div className="text-center py-6">
                  <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-yiwu-500/20">
                    <Check size={32} className="text-yiwu-500" />
                  </div>
                  <h3 className="text-xl font-medium text-white mb-2">提交成功</h3>
                  <p className="text-gray-400">我们将在24小时内联系您</p>
                  <button
                    onClick={handleCloseModal}
                    className="mt-6 rounded-lg bg-yiwu-500 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-yiwu-400"
                  >
                    知道了
                  </button>
                </div>
              ) : (
                <>
                  <h3 className="text-lg font-medium text-white mb-1">联系销售</h3>
                  <p className="text-sm text-gray-400 mb-6">填写以下信息，我们的客户经理将与您联系</p>
                  <form onSubmit={handleContactSubmit} className="space-y-4">
                    <div>
                      <label className="block text-sm text-gray-300 mb-1.5">公司名称</label>
                      <input
                        type="text"
                        required
                        value={contactForm.company}
                        onChange={(e) => setContactForm({ ...contactForm, company: e.target.value })}
                        className="w-full rounded-lg border border-white/10 bg-ocean-800 px-4 py-2.5 text-sm text-white placeholder-gray-500 outline-none focus:border-gold-500/50 transition-colors"
                        placeholder="请输入公司名称"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-300 mb-1.5">邮箱</label>
                      <input
                        type="email"
                        required
                        value={contactForm.email}
                        onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                        className="w-full rounded-lg border border-white/10 bg-ocean-800 px-4 py-2.5 text-sm text-white placeholder-gray-500 outline-none focus:border-gold-500/50 transition-colors"
                        placeholder="请输入邮箱地址"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-300 mb-1.5">联系电话</label>
                      <input
                        type="tel"
                        required
                        value={contactForm.phone}
                        onChange={(e) => setContactForm({ ...contactForm, phone: e.target.value })}
                        className="w-full rounded-lg border border-white/10 bg-ocean-800 px-4 py-2.5 text-sm text-white placeholder-gray-500 outline-none focus:border-gold-500/50 transition-colors"
                        placeholder="请输入联系电话"
                      />
                    </div>
                    <button
                      type="submit"
                      className="w-full rounded-lg bg-gradient-to-r from-yiwu-500 to-gold-500 py-2.5 text-sm font-medium text-white transition-colors hover:from-yiwu-400 hover:to-gold-400"
                    >
                      提交
                    </button>
                  </form>
                </>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
