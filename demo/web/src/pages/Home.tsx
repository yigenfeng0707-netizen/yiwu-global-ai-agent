import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  BarChart3,
  Target,
  FileText,
  Shield,
  Headphones,
  Truck,
  ShoppingBag,
  Cpu,
  Shirt,
  Gem,
  Puzzle,
  PenTool,
  Palette,
  Wrench,
  Home as HomeIcon,
  Globe,
  Languages,
  X,
  Store,
  Building2,
} from 'lucide-react';
import CategoryCard from '@/components/CategoryCard';
import { useStore } from '@/store/useStore';

const agents = [
  { name: '市场洞察', icon: BarChart3, online: true, route: '/market-insight' },
  { name: '智能选品', icon: Target, online: true, route: '/smart-selection' },
  { name: '供应链匹配', icon: Truck, online: true, route: '/supply-chain' },
  { name: '跨境内容生成', icon: FileText, online: true, route: '/content-generation' },
  { name: '合规助手', icon: Shield, online: true, route: '/compliance' },
  { name: '智能客服', icon: Headphones, online: true, route: '/customer-service' },
  { name: '政策复制', icon: Building2, online: true, route: '/policy-replication' },
];

const categoryData = [
  { icon: ShoppingBag, name: '日用百货', description: '厨房用品、清洁工具、收纳整理', growthRate: 12.5 },
  { icon: Gem, name: '饰品配件', description: '时尚首饰、发饰、纽扣拉链', growthRate: 15.8 },
  { icon: Puzzle, name: '玩具', description: '益智玩具、毛绒玩具、遥控玩具', growthRate: 8.6 },
  { icon: PenTool, name: '文具办公用品', description: '笔类、本册、办公收纳', growthRate: 6.8 },
  { icon: Palette, name: '针织品', description: '袜子、围巾、帽子、手套', growthRate: 10.2 },
  { icon: Palette, name: '工艺品', description: '装饰画、仿真花、节日用品', growthRate: 9.5 },
  { icon: Cpu, name: '电子电器', description: '小家电、LED灯饰、手机配件', growthRate: 14.3 },
  { icon: Wrench, name: '五金工具', description: '手动工具、锁具、门窗五金', growthRate: 7.5 },
  { icon: Shirt, name: '服装服饰', description: '女装、童装、运动服', growthRate: 11.2 },
  { icon: HomeIcon, name: '家居装饰', description: '墙贴壁纸、窗帘、灯饰', growthRate: 13.6 },
];

const platformStats = [
  { icon: Store, value: '7.5万', label: '商户' },
  { icon: Globe, value: '210万+', label: 'SKU' },
  { icon: Languages, value: '8', label: '支持语言' },
  { icon: Truck, value: '19', label: '义新欧线路' },
];

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.08 } },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

export default function Home() {
  const navigate = useNavigate();
  const { setSelectedCategory } = useStore();
  const [showGuide, setShowGuide] = useState(() => !localStorage.getItem('yiwu-guide-seen'));

  const handleCloseGuide = () => {
    setShowGuide(false);
    localStorage.setItem('yiwu-guide-seen', '1');
  };

  const handleCategoryClick = (name: string) => {
    setSelectedCategory(name);
    navigate(`/market-insight?category=${encodeURIComponent(name)}`);
  };

  const guideSteps = [
    { num: 1, title: '选择品类', desc: '从义乌10大核心品类中选择' },
    { num: 2, title: '启动Agent', desc: '点击任意智能体卡片进入功能页面' },
    { num: 3, title: '一键出海', desc: '使用全链路工作流，7步完成出海全流程' },
  ];

  return (
    <div className="space-y-8">
      {/* First-visit Guide Overlay */}
      <AnimatePresence>
        {showGuide && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
            onClick={handleCloseGuide}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.35, ease: 'easeOut' }}
              onClick={(e) => e.stopPropagation()}
              className="glass-light relative mx-4 w-full max-w-md rounded-2xl p-8 text-center"
            >
              <button
                onClick={handleCloseGuide}
                className="absolute right-4 top-4 text-gray-500 hover:text-white transition-colors"
              >
                <X size={18} />
              </button>
              <h2 className="font-display text-2xl text-white mb-2">
                欢迎使用<span className="text-yiwu-500">义乌小商品出海</span> <span className="text-gold-500">智能体</span>
              </h2>
              <p className="text-sm text-gray-400 mb-6">3步快速上手，开启跨境出海之旅</p>
              <div className="space-y-4 mb-8">
                {guideSteps.map((step) => (
                  <div key={step.num} className="flex items-start gap-4 rounded-xl bg-ocean-800/50 p-4 text-left">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-yiwu-500 to-gold-500 text-sm font-bold text-white">
                      {step.num}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">{step.title}</p>
                      <p className="text-xs text-gray-400 mt-0.5">{step.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
              <button
                onClick={handleCloseGuide}
                className="w-full rounded-lg bg-gradient-to-r from-yiwu-500 to-gold-500 px-6 py-3 text-sm font-bold text-white transition-opacity hover:opacity-90"
              >
                开始体验
              </button>
              <p className="mt-4 text-xs text-gray-500">义乌国际商贸城 · AI驱动的跨境电商智能助手</p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-ocean-900 via-ocean-800 to-ocean-900 p-8 lg:p-12">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(212,39,44,0.1),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,rgba(212,168,83,0.08),transparent_50%)]" />
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="relative z-10"
        >
          <h1 className="font-display text-4xl lg:text-5xl mb-3">
            <span className="text-yiwu-500">义乌小商品出海</span>{' '}
            <span className="text-gold-500">智能体</span>
          </h1>
          <p className="text-lg text-gray-300 max-w-2xl mb-6">
            基于义乌国际商贸城7.5万商户、210万+SKU，义新欧班列直达欧洲，1039市场采购贸易，为跨境电商提供一站式AI服务
          </p>
          <button
            onClick={() => navigate('/market-insight')}
            className="inline-flex items-center gap-2 rounded-lg bg-yiwu-500 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-yiwu-400"
          >
            开始探索 <ArrowRight size={16} />
          </button>
        </motion.div>
      </section>

      {/* Platform Stats Overview */}
      <section>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {platformStats.map((stat) => (
            <motion.div
              key={stat.label}
              variants={item}
              initial="hidden"
              animate="show"
              className="glass-light rounded-xl p-5 flex flex-col items-center justify-center text-center"
            >
              <stat.icon size={24} className="text-yiwu-400 mb-2" />
              <div className="text-3xl font-bold text-white">{stat.value}</div>
              <div className="text-xs text-gray-400 mt-1">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Agent Status */}
      <section>
        <h2 className="text-lg font-medium text-white mb-4">智能体状态</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-3">
          {agents.map((agent) => (
            <motion.div
              key={agent.name}
              variants={item}
              initial="hidden"
              animate="show"
              onClick={() => navigate(agent.route)}
              className="glass-light rounded-xl p-4 flex items-center gap-3 cursor-pointer hover:border-yiwu-500/30 hover:bg-white/[0.04] transition-colors"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-ocean-800">
                <agent.icon size={20} className="text-yiwu-400" />
              </div>
              <div>
                <div className="text-sm font-medium text-white">{agent.name}</div>
                <div className="flex items-center gap-1 mt-0.5">
                  <span
                    className={`h-2 w-2 rounded-full ${
                      agent.online ? 'bg-yiwu-500' : 'bg-gold-500'
                    }`}
                  />
                  <span className="text-xs text-gray-500">
                    {agent.online ? '在线' : '开发中'}
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Category Navigation */}
      <section>
        <h2 className="text-lg font-medium text-white mb-4">品类导航</h2>
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3"
        >
          {categoryData.map((cat) => (
            <motion.div key={cat.name} variants={item}>
              <div onClick={() => handleCategoryClick(cat.name)}>
                <CategoryCard
                  icon={cat.icon}
                  name={cat.name}
                  description={cat.description}
                  growthRate={cat.growthRate}
                />
              </div>
            </motion.div>
          ))}
        </motion.div>
      </section>
    </div>
  );
}
