import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  ChevronDown, Loader2, Building2, BookOpen, Calculator, Lightbulb,
  RefreshCw, MapPin, Calendar, Tag, FileCheck, ArrowRight, CheckCircle2,
} from 'lucide-react';
import { categories } from '@/store/useStore';
import {
  fetchPolicyCities, fetchPolicyGuide, calculatePolicyBenefit, fetchPolicyCases,
  type PolicyCityData, type PolicyGuideData, type PolicyBenefitData, type PolicyCaseData,
} from '@/utils/api';

type TabKey = 'cities' | 'guide' | 'calculator' | 'cases';

const tabs: { key: TabKey; label: string; icon: typeof Building2 }[] = [
  { key: 'cities', label: '39城试点', icon: Building2 },
  { key: 'guide', label: '政策解读', icon: BookOpen },
  { key: 'calculator', label: '红利计算', icon: Calculator },
  { key: 'cases', label: '成功案例', icon: Lightbulb },
];

export default function PolicyReplication() {
  const [activeTab, setActiveTab] = useState<TabKey>('cities');

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      {/* 页面标题 */}
      <div className="glass-light rounded-xl p-6">
        <h2 className="text-lg font-medium text-white flex items-center gap-2">
          <Building2 size={20} className="text-yiwu-400" /> 政策复制Agent
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          1039市场采购贸易政策解读 · 39城复制推广 · 政策红利计算 · 义乌成功案例本地化适配
        </p>
      </div>

      {/* Tab切换 */}
      <div className="flex gap-2 overflow-x-auto pb-1">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium whitespace-nowrap transition-colors ${
              activeTab === tab.key
                ? 'bg-yiwu-500/10 text-yiwu-400 border border-yiwu-500/20'
                : 'bg-ocean-800/50 text-gray-400 hover:bg-ocean-800 hover:text-white border border-transparent'
            }`}
          >
            <tab.icon size={16} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab内容 */}
      {activeTab === 'cities' && <CitiesTab />}
      {activeTab === 'guide' && <GuideTab />}
      {activeTab === 'calculator' && <CalculatorTab />}
      {activeTab === 'cases' && <CasesTab />}
    </motion.div>
  );
}

// ==================== 39城试点 Tab ====================
function CitiesTab() {
  const [cities, setCities] = useState<PolicyCityData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [loaded, setLoaded] = useState(false);
  const [selectedProvince, setSelectedProvince] = useState('');

  const handleLoad = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await fetchPolicyCities();
      setCities(result.cities);
      setLoaded(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : '查询失败');
    } finally {
      setLoading(false);
    }
  };

  const provinces = [...new Set(cities.map((c) => c.province))];
  const filtered = selectedProvince
    ? cities.filter((c) => c.province === selectedProvince)
    : cities;

  return (
    <div className="space-y-4">
      <div className="glass-light rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-white flex items-center gap-2">
            <MapPin size={16} className="text-yiwu-400" /> 39城市场采购贸易试点
          </h3>
          <button onClick={handleLoad} disabled={loading}
            className="rounded-lg bg-yiwu-600 px-4 py-2 text-xs font-medium text-white hover:bg-yiwu-500 disabled:opacity-50 transition-colors flex items-center gap-1">
            {loading ? <Loader2 size={14} className="animate-spin" /> : <Building2 size={14} />}
            {loaded ? '刷新' : '查询'}
          </button>
        </div>

        {error && (
          <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-3 flex items-center justify-between mb-4">
            <span className="text-xs text-red-400">{error}</span>
            <button onClick={handleLoad} disabled={loading}
              className="rounded-lg bg-red-500/20 px-2 py-1 text-xs text-red-400 hover:bg-red-500/30 transition-colors flex items-center gap-1">
              <RefreshCw size={10} /> 重试
            </button>
          </div>
        )}

        {loaded && provinces.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            <button onClick={() => setSelectedProvince('')}
              className={`rounded-md px-3 py-1 text-xs transition-colors ${
                !selectedProvince ? 'bg-yiwu-500/20 text-yiwu-400' : 'bg-ocean-800/50 text-gray-400 hover:text-white'
              }`}>
              全部 ({cities.length})
            </button>
            {provinces.map((p) => (
              <button key={p} onClick={() => setSelectedProvince(p)}
                className={`rounded-md px-3 py-1 text-xs transition-colors ${
                  selectedProvince === p ? 'bg-yiwu-500/20 text-yiwu-400' : 'bg-ocean-800/50 text-gray-400 hover:text-white'
                }`}>
                {p} ({cities.filter((c) => c.province === p).length})
              </button>
            ))}
          </div>
        )}

        {loading && (
          <div className="flex h-32 items-center justify-center">
            <Loader2 className="h-6 w-6 animate-spin text-yiwu-500" />
            <span className="ml-2 text-sm text-gray-400">加载中...</span>
          </div>
        )}

        {loaded && !loading && (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((city) => (
              <div key={city.city} className="rounded-lg bg-ocean-800/50 p-4 hover:bg-ocean-800/70 transition-colors">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-medium text-white">{city.city}</h4>
                  <span className="text-xs text-gray-500 bg-ocean-900/50 px-2 py-0.5 rounded">{city.province}</span>
                </div>
                <div className="space-y-1.5 text-xs text-gray-400">
                  <div className="flex items-center gap-1">
                    <Calendar size={10} className="text-gold-400" />
                    <span>获批: {city.approved_year}年</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Tag size={10} className="text-yiwu-400" />
                    <span className="line-clamp-1">品类: {city.main_categories}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <FileCheck size={10} className="text-green-400" />
                    <span className="line-clamp-1">{city.policy_benefits}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <MapPin size={10} className="text-blue-400" />
                    <span>海关代码: {city.customs_code}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ==================== 政策解读 Tab ====================
function GuideTab() {
  const [guide, setGuide] = useState<PolicyGuideData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLoad = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await fetchPolicyGuide();
      setGuide(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : '查询失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="glass-light rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-white flex items-center gap-2">
            <BookOpen size={16} className="text-yiwu-400" /> 1039市场采购贸易政策解读
          </h3>
          <button onClick={handleLoad} disabled={loading}
            className="rounded-lg bg-yiwu-600 px-4 py-2 text-xs font-medium text-white hover:bg-yiwu-500 disabled:opacity-50 transition-colors flex items-center gap-1">
            {loading ? <Loader2 size={14} className="animate-spin" /> : <BookOpen size={14} />}
            {guide ? '刷新' : '查看政策'}
          </button>
        </div>

        {error && (
          <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-3 mb-4">
            <span className="text-xs text-red-400">{error}</span>
          </div>
        )}

        {loading && (
          <div className="flex h-32 items-center justify-center">
            <Loader2 className="h-6 w-6 animate-spin text-yiwu-500" />
            <span className="ml-2 text-sm text-gray-400">加载中...</span>
          </div>
        )}

        {guide && !loading && (
          <div className="space-y-6">
            {/* 政策背景 */}
            <div>
              <h4 className="text-sm font-medium text-white mb-2">政策背景</h4>
              <p className="text-xs text-gray-400 leading-relaxed">{guide.background}</p>
            </div>

            {/* 政策要点 */}
            <div>
              <h4 className="text-sm font-medium text-white mb-3">政策要点</h4>
              <div className="space-y-2">
                {guide.key_points.map((point, i) => (
                  <div key={i} className="rounded-lg bg-ocean-800/50 p-4">
                    <div className="flex items-center justify-between mb-1">
                      <h5 className="text-sm font-medium text-white">{point.title}</h5>
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        point.benefit_level === '高' ? 'bg-yiwu-500/20 text-yiwu-400' : 'bg-gold-500/20 text-gold-400'
                      }`}>
                        {point.benefit_level}收益
                      </span>
                    </div>
                    <p className="text-xs text-gray-400">{point.description}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* 适用条件 */}
            <div>
              <h4 className="text-sm font-medium text-white mb-3">适用条件</h4>
              <div className="space-y-1">
                {guide.applicable_conditions.map((cond, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs text-gray-400">
                    <CheckCircle2 size={12} className="text-yiwu-400 mt-0.5 shrink-0" />
                    <span>{cond}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* 操作流程 */}
            <div>
              <h4 className="text-sm font-medium text-white mb-3">操作流程</h4>
              <div className="space-y-2">
                {guide.operation_process.map((step, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-yiwu-500/20 text-xs font-bold text-yiwu-400">
                      {step.step}
                    </div>
                    <div>
                      <h5 className="text-sm font-medium text-white">{step.title}</h5>
                      <p className="text-xs text-gray-400">{step.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 税收优惠 */}
            <div>
              <h4 className="text-sm font-medium text-white mb-3">税收优惠</h4>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="rounded-lg bg-yiwu-500/10 border border-yiwu-500/20 p-4">
                  <p className="text-xs text-gray-500 mb-1">增值税</p>
                  <p className="text-sm font-medium text-yiwu-400">{guide.tax_benefits.vat_exemption ? '免征' : '正常征收'}</p>
                  <p className="text-xs text-gray-400 mt-1">{guide.tax_benefits.vat_description}</p>
                </div>
                <div className="rounded-lg bg-ocean-800/50 p-4">
                  <p className="text-xs text-gray-500 mb-1">所得税</p>
                  <p className="text-sm font-medium text-white">{guide.tax_benefits.income_tax}</p>
                </div>
                <div className="rounded-lg bg-ocean-800/50 p-4">
                  <p className="text-xs text-gray-500 mb-1">印花税</p>
                  <p className="text-sm font-medium text-white">{guide.tax_benefits.stamp_duty}</p>
                </div>
                <div className="rounded-lg bg-gold-500/10 border border-gold-500/20 p-4">
                  <p className="text-xs text-gray-500 mb-1">成本节省</p>
                  <p className="text-sm font-medium text-gold-400">{guide.tax_benefits.compared_to_general_trade.cost_saving}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ==================== 红利计算 Tab ====================
function CalculatorTab() {
  const [annualExport, setAnnualExport] = useState(1000000);
  const [category, setCategory] = useState('日用百货');
  const [city, setCity] = useState('义乌');
  const [result, setResult] = useState<PolicyBenefitData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleCalc = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await calculatePolicyBenefit({ annual_export: annualExport, category, city });
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : '计算失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="glass-light rounded-xl p-6 space-y-4">
        <h3 className="text-sm font-medium text-white flex items-center gap-2">
          <Calculator size={16} className="text-gold-400" /> 政策红利计算器
        </h3>
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="text-xs text-gray-500 mb-1 block">年出口额 (USD)</label>
            <input type="number" value={annualExport} onChange={(e) => setAnnualExport(Number(e.target.value))}
              className="rounded-lg bg-ocean-800 px-4 py-2 text-sm text-white border border-white/10 focus:border-yiwu-500 focus:outline-none w-40" />
          </div>
          <div className="relative">
            <label className="text-xs text-gray-500 mb-1 block">品类</label>
            <select value={category} onChange={(e) => setCategory(e.target.value)}
              className="appearance-none rounded-lg bg-ocean-800 px-4 py-2 pr-10 text-sm text-white border border-white/10 focus:border-yiwu-500 focus:outline-none">
              {categories.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
            <ChevronDown className="pointer-events-none absolute right-3 top-[34px] h-4 w-4 -translate-y-1/2 text-gray-400" />
          </div>
          <div className="relative">
            <label className="text-xs text-gray-500 mb-1 block">试点城市</label>
            <input type="text" value={city} onChange={(e) => setCity(e.target.value)}
              className="rounded-lg bg-ocean-800 px-4 py-2 text-sm text-white border border-white/10 focus:border-yiwu-500 focus:outline-none w-32"
              placeholder="如: 义乌" />
          </div>
          <button onClick={handleCalc} disabled={loading}
            className="rounded-lg bg-yiwu-600 px-6 py-2 text-sm font-medium text-white hover:bg-yiwu-500 disabled:opacity-50 transition-colors flex items-center gap-2">
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Calculator size={16} />}
            计算
          </button>
        </div>

        {error && (
          <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-3">
            <span className="text-xs text-red-400">{error}</span>
          </div>
        )}
      </div>

      {result && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          {/* 总节省 */}
          <div className="glass-light rounded-xl p-6">
            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-lg bg-yiwu-500/10 border border-yiwu-500/20 p-4 text-center">
                <p className="text-xs text-gray-500 mb-1">总节省金额</p>
                <p className="text-2xl font-bold text-yiwu-400">${result.total_saving.toLocaleString()}</p>
                <p className="text-xs text-gray-400 mt-1">节省率 {result.saving_rate}</p>
              </div>
              <div className="rounded-lg bg-ocean-800/50 p-4 text-center">
                <p className="text-xs text-gray-500 mb-1">一般贸易综合成本</p>
                <p className="text-lg font-medium text-white">${result.compared_to_general_trade.general_trade_total_cost.toLocaleString()}</p>
              </div>
              <div className="rounded-lg bg-ocean-800/50 p-4 text-center">
                <p className="text-xs text-gray-500 mb-1">1039模式综合成本</p>
                <p className="text-lg font-medium text-yiwu-400">${result.compared_to_general_trade.market_purchase_total_cost.toLocaleString()}</p>
                <p className="text-xs text-gold-400 mt-1">降低 {result.compared_to_general_trade.cost_reduction}</p>
              </div>
            </div>
          </div>

          {/* 分项详情 */}
          <div className="glass-light rounded-xl p-6">
            <h4 className="text-sm font-medium text-white mb-4">分项详情</h4>
            <div className="space-y-3">
              {Object.entries(result.benefits).map(([key, benefit]) => (
                <div key={key} className="rounded-lg bg-ocean-800/50 p-4">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-white">{benefit.description}</span>
                    <span className="text-sm font-medium text-yiwu-400">
                      {typeof benefit.amount === 'number' ? `$${benefit.amount.toLocaleString()}` : `${benefit.amount}天`}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">{benefit.detail}</p>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}

// ==================== 成功案例 Tab ====================
function CasesTab() {
  const [cases, setCases] = useState<PolicyCaseData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [loaded, setLoaded] = useState(false);
  const [expandedCase, setExpandedCase] = useState<number | null>(null);

  const handleLoad = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await fetchPolicyCases();
      setCases(result.cases);
      setLoaded(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : '查询失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="glass-light rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-white flex items-center gap-2">
            <Lightbulb size={16} className="text-gold-400" /> 义乌成功出海案例
          </h3>
          <button onClick={handleLoad} disabled={loading}
            className="rounded-lg bg-yiwu-600 px-4 py-2 text-xs font-medium text-white hover:bg-yiwu-500 disabled:opacity-50 transition-colors flex items-center gap-1">
            {loading ? <Loader2 size={14} className="animate-spin" /> : <Lightbulb size={14} />}
            {loaded ? '刷新' : '查看案例'}
          </button>
        </div>

        {error && (
          <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-3 mb-4">
            <span className="text-xs text-red-400">{error}</span>
          </div>
        )}

        {loading && (
          <div className="flex h-32 items-center justify-center">
            <Loader2 className="h-6 w-6 animate-spin text-yiwu-500" />
            <span className="ml-2 text-sm text-gray-400">加载中...</span>
          </div>
        )}

        {loaded && !loading && (
          <div className="space-y-3">
            {cases.map((c) => (
              <div key={c.case_id} className="rounded-lg bg-ocean-800/50 overflow-hidden">
                <button
                  onClick={() => setExpandedCase(expandedCase === c.case_id ? null : c.case_id)}
                  className="w-full p-4 flex items-center justify-between hover:bg-ocean-800/70 transition-colors"
                >
                  <div className="flex items-center gap-3 text-left">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-yiwu-500/20 text-xs font-bold text-yiwu-400">
                      {c.case_id}
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-white">{c.title}</h4>
                      <div className="flex items-center gap-3 mt-0.5 text-xs text-gray-400">
                        <span>{c.category}</span>
                        <span className="text-gold-400">{c.target_market}</span>
                        <span className="text-yiwu-400">年出口${c.annual_export}</span>
                      </div>
                    </div>
                  </div>
                  <ArrowRight size={16} className={`text-gray-500 transition-transform ${expandedCase === c.case_id ? 'rotate-90' : ''}`} />
                </button>

                {expandedCase === c.case_id && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="px-4 pb-4 space-y-3">
                    {/* 核心策略 */}
                    <div>
                      <p className="text-xs text-gray-500 mb-1.5">核心策略</p>
                      {c.key_strategies.map((s, i) => (
                        <div key={i} className="flex items-start gap-2 text-xs text-gray-400 mb-1">
                          <CheckCircle2 size={10} className="text-yiwu-400 mt-0.5 shrink-0" />
                          <span>{s}</span>
                        </div>
                      ))}
                    </div>

                    {/* 本地化建议 */}
                    <div>
                      <p className="text-xs text-gray-500 mb-1.5">本地化建议</p>
                      {c.localization_tips.map((t, i) => (
                        <div key={i} className="flex items-start gap-2 text-xs text-gray-400 mb-1">
                          <ArrowRight size={10} className="text-gold-400 mt-0.5 shrink-0" />
                          <span>{t}</span>
                        </div>
                      ))}
                    </div>

                    {/* 可复制要点 */}
                    <div>
                      <p className="text-xs text-gray-500 mb-1.5">可复制要点</p>
                      {c.replicable_points.map((p, i) => (
                        <div key={i} className="flex items-start gap-2 text-xs text-gray-400 mb-1">
                          <Lightbulb size={10} className="text-green-400 mt-0.5 shrink-0" />
                          <span>{p}</span>
                        </div>
                      ))}
                    </div>

                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-gray-500">复制难度:</span>
                      <span className={`px-2 py-0.5 rounded ${
                        c.replication_difficulty === '较低' ? 'bg-green-500/20 text-green-400' : 'bg-gold-500/20 text-gold-400'
                      }`}>
                        {c.replication_difficulty}
                      </span>
                    </div>
                  </motion.div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
