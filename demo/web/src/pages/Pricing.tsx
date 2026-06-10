import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, ChevronDown, ChevronUp, Sparkles, X } from 'lucide-react';

interface Plan {
  name: string;
  price: string;
  period: string;
  description: string;
  features: string[];
  highlight: boolean;
  cta: string;
}

const plans: Plan[] = [
  {
    name: '基础版',
    price: '299',
    period: '元/月',
    description: '适合小微企业和个人卖家',
    features: ['市场洞察报告', '智能选品推荐', '跨境内容生成', '10大品类覆盖', '8种语言支持'],
    highlight: false,
    cta: '立即订阅',
  },
  {
    name: '高级版',
    price: '999',
    period: '元/月',
    description: '适合成长型电商企业',
    features: ['基础版全部功能', '供应链匹配(6大Agent)', '合规助手(15国)', '智能客服(7x24h)', '义新欧班列物流'],
    highlight: true,
    cta: '最受欢迎',
  },
  {
    name: '企业定制',
    price: '5万',
    period: '起/年',
    description: '适合大型企业和团队',
    features: ['高级版全部功能', '私有化部署', '定制Agent开发', 'API接口对接', '专属客户经理'],
    highlight: false,
    cta: '联系我们',
  },
];

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
];

const fadeUp = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

export default function Pricing() {
  const navigate = useNavigate();
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [showContactModal, setShowContactModal] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [contactForm, setContactForm] = useState({
    company: '',
    email: '',
    phone: '',
  });

  const handleCtaClick = (planName: string) => {
    if (planName === '企业定制') {
      setShowContactModal(true);
      setSubmitSuccess(false);
    } else {
      navigate('/login');
    }
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

  return (
    <div className="space-y-12">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center">
        <h1 className="font-display text-3xl text-white mb-2">套餐价格</h1>
        <p className="text-gray-400">选择适合您的方案，开启义乌小商品跨境出海智能之旅</p>
      </motion.div>

      {/* Pricing Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
        {plans.map((plan, i) => (
          <motion.div
            key={plan.name}
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
              <span className="text-4xl font-bold text-white">¥{plan.price}</span>
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
                  : plan.name === '企业定制'
                  ? 'bg-ocean-800 text-white hover:bg-ocean-700'
                  : 'bg-yiwu-500 text-white hover:bg-yiwu-400'
              }`}
              onClick={() => handleCtaClick(plan.name)}
            >
              {plan.highlight && <Sparkles size={14} className="inline mr-1" />}
              {plan.cta}
            </button>
          </motion.div>
        ))}
      </div>

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
