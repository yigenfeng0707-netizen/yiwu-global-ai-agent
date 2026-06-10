import { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, Loader2, Play, CheckCircle2, Circle, BarChart3, Target, Sparkles, ShieldCheck, MessageCircle, Truck, RefreshCw, Building2 } from 'lucide-react';
import { categories } from '@/store/useStore';
import { runPipeline, type PipelineResult } from '@/utils/api';

const regions = ['欧洲（义新欧班列直达）', '中亚', '中东', '东南亚', '非洲', '南美'];
const budgets = ['低', '中', '高'];
const countries = ['德国', '法国', '西班牙', '哈萨克斯坦', '沙特阿拉伯', '阿联酋', '印尼', '泰国'];
const platforms = ['amazon', 'alibaba', 'tiktok', 'temu'];
const langs = ['en', 'de', 'fr', 'es', 'ar', 'ru'];

interface StepInfo { key: string; label: string; icon: typeof BarChart3 }
const steps: StepInfo[] = [
  { key: 'market_insight', label: '市场洞察', icon: BarChart3 },
  { key: 'smart_selection', label: '智能选品', icon: Target },
  { key: 'supply_chain', label: '供应链匹配', icon: Truck },
  { key: 'content_generation', label: '内容生成', icon: Sparkles },
  { key: 'compliance', label: '合规查询', icon: ShieldCheck },
  { key: 'customer_service', label: '智能客服', icon: MessageCircle },
  { key: 'policy_replication', label: '政策复制', icon: Building2 },
];

type StepStatus = 'pending' | 'running' | 'completed';

export default function Pipeline() {
  const [category, setCategory] = useState(categories[0]);
  const [region, setRegion] = useState(regions[0]);
  const [budget, setBudget] = useState('中');
  const [targetCountry, setTargetCountry] = useState(countries[0]);
  const [platform, setPlatform] = useState('amazon');
  const [targetLang, setTargetLang] = useState('en');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<PipelineResult | null>(null);
  const [stepStatuses, setStepStatuses] = useState<StepStatus[]>(
    steps.map(() => 'pending')
  );

  const handleRun = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    setStepStatuses(steps.map(() => 'pending'));

    const timers: ReturnType<typeof setTimeout>[] = [];
    steps.forEach((_, i) => {
      timers.push(setTimeout(() => {
        setStepStatuses((prev) => {
          const next = [...prev];
          next[i] = 'running';
          if (i > 0) next[i - 1] = 'completed';
          return next;
        });
      }, i * 800));
    });

    try {
      const res = await runPipeline({
        category, region, budget,
        target_country: targetCountry,
        platform, target_language: targetLang,
      });
      setResult(res);
      setStepStatuses(steps.map(() => 'completed'));
    } catch (err) {
      setError(err instanceof Error ? err.message : '全链路执行失败，请稍后重试');
      setStepStatuses(steps.map(() => 'pending'));
    } finally {
      timers.forEach(clearTimeout);
      setLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      {/* 表单 */}
      <div className="glass-light rounded-xl p-6 space-y-4">
        <h3 className="text-sm font-medium text-white flex items-center gap-2">
          <Play size={16} className="text-gold-400" /> 全链路工作流（7步）
        </h3>
        <div className="flex flex-wrap gap-4">
          {[
            { label: '品类', value: category, setter: setCategory, options: categories },
            { label: '区域', value: region, setter: setRegion, options: regions },
            { label: '预算', value: budget, setter: setBudget, options: budgets },
            { label: '目标国家', value: targetCountry, setter: setTargetCountry, options: countries },
            { label: '平台', value: platform, setter: setPlatform, options: platforms },
            { label: '语言', value: targetLang, setter: setTargetLang, options: langs },
          ].map((field) => (
            <div key={field.label}>
              <label className="text-xs text-gray-500 mb-1 block">{field.label}</label>
              <div className="relative">
                <select value={field.value} onChange={(e) => field.setter(e.target.value)}
                  className="appearance-none rounded-lg bg-ocean-800 px-3 py-2 pr-8 text-sm text-white border border-white/10 focus:border-yiwu-500 focus:outline-none">
                  {field.options.map((o) => <option key={o} value={o}>{o}</option>)}
                </select>
                <ChevronDown className="pointer-events-none absolute right-2 top-1/2 h-3 w-3 -translate-y-1/2 text-gray-400" />
              </div>
            </div>
          ))}
        </div>
        <button onClick={handleRun} disabled={loading}
          className="rounded-lg bg-yiwu-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-yiwu-500 disabled:opacity-50 transition-colors flex items-center gap-2">
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
          {loading ? '执行中...' : '运行全链路'}
        </button>
      </div>

      {error && (
        <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-4 flex items-center justify-between">
          <span className="text-sm text-red-400">{error}</span>
          <button onClick={handleRun} disabled={loading}
            className="rounded-lg bg-red-500/20 px-3 py-1.5 text-xs text-red-400 hover:bg-red-500/30 transition-colors flex items-center gap-1">
            <RefreshCw size={12} /> 重试
          </button>
        </div>
      )}

      {/* 时间线 */}
      <div className="glass-light rounded-xl p-6">
        <div className="space-y-0">
          {steps.map((step, i) => {
            const status = stepStatuses[i];
            const Icon = step.icon;
            const isLast = i === steps.length - 1;
            const stepData = result?.state?.[step.key as keyof typeof result.state];
            return (
              <div key={step.key}>
                <div className="flex items-start gap-4">
                  <div className="flex flex-col items-center">
                    <div className={`rounded-full p-2 transition-colors ${
                      status === 'completed' ? 'bg-yiwu-500/20 text-yiwu-400' :
                      status === 'running' ? 'bg-gold-500/20 text-gold-400' :
                      'bg-ocean-800 text-gray-600'
                    }`}>
                      {status === 'completed' ? <CheckCircle2 size={20} /> :
                       status === 'running' ? <Loader2 size={20} className="animate-spin" /> :
                       <Circle size={20} />}
                    </div>
                    {!isLast && (
                      <div className={`w-0.5 h-8 transition-colors ${
                        status === 'completed' ? 'bg-yiwu-500/30' : 'bg-ocean-800'
                      }`} />
                    )}
                  </div>
                  <div className="flex-1 pb-4">
                    <div className="flex items-center gap-2">
                      <Icon size={16} className={status === 'completed' ? 'text-yiwu-400' : status === 'running' ? 'text-gold-400' : 'text-gray-600'} />
                      <span className={`text-sm font-medium ${status === 'completed' ? 'text-white' : status === 'running' ? 'text-gold-400' : 'text-gray-500'}`}>
                        {step.label}
                      </span>
                      {status === 'running' && <span className="text-xs text-gold-400">执行中...</span>}
                    </div>
                    {status === 'completed' && stepData && (
                      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                        className="mt-2 rounded-lg bg-ocean-800/50 p-3">
                        <StepSummary stepKey={step.key} data={stepData} />
                      </motion.div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 总览 */}
      {result && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          className="glass-light rounded-xl p-6">
          <h3 className="text-sm font-medium text-white mb-4">执行总览</h3>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <SummaryCard label="完成步骤" value={`${result.summary.steps_completed}/${result.summary.total_steps}`} />
            <SummaryCard label="耗时" value={`${result.summary.duration_seconds.toFixed(1)}秒`} />
            <SummaryCard label="错误数" value={`${result.summary.errors}`} highlight={result.summary.errors > 0} />
            <SummaryCard label="推荐产品" value={result.summary.product || '-'} highlight />
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

function SummaryCard({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className={`rounded-lg p-3 ${highlight ? 'bg-yiwu-500/10 border border-yiwu-500/20' : 'bg-ocean-800/50'}`}>
      <p className="text-xs text-gray-500">{label}</p>
      <p className={`text-sm font-medium ${highlight ? 'text-yiwu-400' : 'text-white'}`}>{value}</p>
    </div>
  );
}

function StepSummary({ stepKey, data }: { stepKey: string; data: unknown }) {
  const d = data as Record<string, unknown>;
  switch (stepKey) {
    case 'market_insight':
      return (
        <div className="text-xs text-gray-400 space-y-1">
          <p>市场规模: <span className="text-white">{(d as Record<string, string>).market_size || '-'}</span></p>
          <p>增长率: <span className="text-yiwu-400">{(d as Record<string, string>).market_growth || '-'}</span></p>
        </div>
      );
    case 'smart_selection':
      return (
        <div className="text-xs text-gray-400 space-y-1">
          <p>综合评分: <span className="text-yiwu-400">{(d as Record<string, Record<string, unknown>>).overall_score ? String((d.overall_score as Record<string, unknown>).total) : '-'}</span></p>
          <p>市场机会: <span className="text-white">{(d as Record<string, Record<string, string>>).market_opportunity?.market_size || '-'}</span></p>
        </div>
      );
    case 'supply_chain':
      return (
        <div className="text-xs text-gray-400 space-y-1">
          <p>供应链评分: <span className="text-yiwu-400">{(d as Record<string, Record<string, unknown>>).supply_score ? String((d.supply_score as Record<string, unknown>).total) : '-'}</span></p>
          <p>供应商数: <span className="text-white">{Array.isArray((d as Record<string, unknown>).suppliers) ? (d.suppliers as unknown[]).length : 0}</span></p>
        </div>
      );
    case 'content_generation':
      return (
        <div className="text-xs text-gray-400 space-y-1">
          <p>标题: <span className="text-white line-clamp-1">{(d as Record<string, Record<string, string>>).content?.title || '-'}</span></p>
          <p>平台: <span className="text-gold-400">{(d as Record<string, string>).platform || '-'}</span></p>
        </div>
      );
    case 'compliance':
      return (
        <div className="text-xs text-gray-400 space-y-1">
          <p>目标国家: <span className="text-white">{(d as Record<string, string>).target_country || '-'}</span></p>
          <p>总税费: <span className="text-gold-400">{(d as Record<string, Record<string, string>>).tariff?.total_tax || '-'}</span></p>
        </div>
      );
    case 'customer_service':
      return (
        <div className="text-xs text-gray-400 space-y-1">
          <p>FAQ 数量: <span className="text-white">{Array.isArray((d as Record<string, unknown>).faqs) ? (d.faqs as unknown[]).length : 0}</span></p>
        </div>
      );
    case 'policy_replication':
      return (
        <div className="text-xs text-gray-400 space-y-1">
          <p>试点城市: <span className="text-yiwu-400">{(d as Record<string, number>).total_cities || 39}</span></p>
          <p>政策: <span className="text-white">1039市场采购贸易</span></p>
        </div>
      );
    default:
      return null;
  }
}
