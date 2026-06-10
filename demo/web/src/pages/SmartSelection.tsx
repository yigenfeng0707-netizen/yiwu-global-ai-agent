import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, Loader2, CheckCircle2, Circle, Truck } from 'lucide-react';
import { useStore, categories } from '@/store/useStore';
import { fetchSmartSelection, type SmartSelectionData } from '@/utils/api';
import ScoreCircle from '@/components/ScoreCircle';

const budgets = ['低', '中', '高'];
const markets = ['欧洲（义新欧班列直达）', '中亚', '中东', '东南亚', '非洲', '南美'];

export default function SmartSelection() {
  const { selectedCategory, setSelectedCategory, budget, setBudget, targetMarket, setTargetMarket } = useStore();
  const [data, setData] = useState<SmartSelectionData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchSmartSelection(selectedCategory, budget, targetMarket)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [selectedCategory, budget, targetMarket]);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-yiwu-500" />
        <span className="ml-3 text-gray-400">正在分析选品数据...</span>
      </div>
    );
  }

  if (!data) {
    return <div className="flex h-96 items-center justify-center text-gray-500">暂无数据</div>;
  }

  const sortedProducts = [...data.product_recommendations].sort(
    (a, b) => (b.scores['综合评分'] || 0) - (a.scores['综合评分'] || 0)
  );

  const opportunityItems = [
    { label: '市场规模', value: data.market_opportunity.market_size },
    { label: '增长率', value: data.market_opportunity.growth_rate },
    { label: '竞争程度', value: data.market_opportunity.competition_level },
    { label: '进入难度', value: data.market_opportunity.entry_difficulty },
  ];

  const costItems = Object.entries(data.profit_analysis.cost_breakdown).map(([item, value]) => ({
    item, value,
  }));

  const revenueItems = Object.entries(data.profit_analysis.revenue).map(([item, value]) => ({
    item, value,
  }));

  const planPhases = Object.entries(data.action_plan).map(([key, phase]) => ({
    key, name: phase.name, tasks: phase.tasks,
  }));

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      {/* Selectors */}
      <div className="flex flex-wrap gap-4">
        <div className="relative">
          <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)}
            className="appearance-none rounded-lg bg-ocean-800 px-4 py-2 pr-10 text-sm text-white border border-white/10 focus:border-yiwu-500 focus:outline-none">
            {categories.map((c) => (<option key={c} value={c}>{c}</option>))}
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        </div>
        <div className="relative">
          <select value={budget} onChange={(e) => setBudget(e.target.value)}
            className="appearance-none rounded-lg bg-ocean-800 px-4 py-2 pr-10 text-sm text-white border border-white/10 focus:border-yiwu-500 focus:outline-none">
            {budgets.map((b) => (<option key={b} value={b}>预算: {b}</option>))}
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        </div>
        <div className="relative">
          <select value={targetMarket} onChange={(e) => setTargetMarket(e.target.value)}
            className="appearance-none rounded-lg bg-ocean-800 px-4 py-2 pr-10 text-sm text-white border border-white/10 focus:border-yiwu-500 focus:outline-none">
            {markets.map((m) => (<option key={m} value={m}>{m}</option>))}
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        </div>
      </div>

      {/* Overall Score + Market Opportunity */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="glass-light rounded-xl p-6 flex flex-col items-center justify-center">
          <p className="text-sm text-gray-400 mb-3">综合评分</p>
          <ScoreCircle score={data.overall_score.total} level={data.overall_score.level} size={140} />
          <p className="text-sm text-yiwu-400 mt-2">{data.overall_score.level}</p>
        </div>
        <div className="glass-light rounded-xl p-6 lg:col-span-2">
          <h3 className="text-sm font-medium text-white mb-4">市场机会概览</h3>
          <div className="grid gap-3 sm:grid-cols-2">
            {opportunityItems.map((item, i) => (
              <div key={i} className="rounded-lg bg-ocean-800/50 p-4">
                <p className="text-xs text-gray-500 mb-1">{item.label}</p>
                <span className="text-lg font-bold text-white">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Product Recommendations */}
      <div className="glass-light rounded-xl p-6">
        <h3 className="text-sm font-medium text-white mb-4">产品推荐</h3>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {sortedProducts.map((product, i) => {
            const totalScore = product.scores['综合评分'] || 0;
            return (
              <div key={i} className="rounded-lg bg-ocean-800/50 p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-medium text-white">{product.product}</span>
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    totalScore >= 70 ? 'bg-yiwu-500/10 text-yiwu-400' : totalScore >= 50 ? 'bg-gold-500/10 text-gold-400' : 'bg-red-500/10 text-red-400'
                  }`}>
                    {totalScore}分
                  </span>
                </div>
                <div className="space-y-2">
                  {Object.entries(product.scores).map(([label, value]) => (
                    <div key={label}>
                      <div className="flex items-center justify-between text-xs mb-0.5">
                        <span className="text-gray-400">{label}</span>
                        <span className="text-gray-500">{value}</span>
                      </div>
                      <div className="h-1.5 rounded-full bg-ocean-900">
                        <div className="h-1.5 rounded-full bg-yiwu-500/70" style={{ width: `${value}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
                <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
                  <span>MOQ: {product.suggested_moq}</span>
                  <span className="text-yiwu-400">ROI: {product.estimated_roi}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Profit Analysis */}
      <div className="glass-light rounded-xl p-6">
        <h3 className="text-sm font-medium text-white mb-4">利润分析</h3>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <p className="text-xs text-gray-500 mb-2">成本结构</p>
            <div className="space-y-2">
              {costItems.map((item, i) => (
                <div key={i} className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">{item.item}</span>
                  <span className="text-white">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-2">收入预估</p>
            <div className="space-y-2">
              {revenueItems.map((item, i) => (
                <div key={i} className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">{item.item}</span>
                  <span className="text-white">{item.value}</span>
                </div>
              ))}
            </div>
            <div className="mt-3 pt-3 border-t border-white/5">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">盈亏平衡</span>
                <span className="text-white">{data.profit_analysis.break_even.盈亏平衡销量}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Supply Chain */}
      <div className="glass-light rounded-xl p-6">
        <h3 className="text-sm font-medium text-white mb-4 flex items-center gap-2">
          <Truck size={16} className="text-yiwu-400" /> 供应链推荐
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-500 text-xs border-b border-white/5">
                <th className="pb-2 text-left font-medium">供应商</th>
                <th className="pb-2 text-left font-medium">地区</th>
                <th className="pb-2 text-left font-medium">MOQ</th>
                <th className="pb-2 text-left font-medium">价格</th>
                <th className="pb-2 text-left font-medium">评分</th>
                <th className="pb-2 text-left font-medium">推荐</th>
              </tr>
            </thead>
            <tbody>
              {data.supply_recommendations.map((s, i) => (
                <tr key={i} className="border-b border-white/5">
                  <td className="py-2 text-white">{s.supplier}</td>
                  <td className="py-2 text-gray-400">{s.location}</td>
                  <td className="py-2 text-gray-400">{s.moq}</td>
                  <td className="py-2 text-gray-400">{s.price_range}</td>
                  <td className="py-2 text-gray-400">{s.rating}</td>
                  <td className="py-2">{s.recommended ? <CheckCircle2 size={16} className="text-yiwu-400" /> : <Circle size={16} className="text-gray-600" />}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Action Plan */}
      <div className="glass-light rounded-xl p-6">
        <h3 className="text-sm font-medium text-white mb-4">行动计划</h3>
        <div className="space-y-4">
          {planPhases.map((phase, i) => (
            <div key={phase.key} className="relative pl-6 border-l-2 border-yiwu-500/30">
              <div className="absolute -left-[7px] top-0 h-3 w-3 rounded-full bg-yiwu-500" />
              <div className="mb-2">
                <span className="text-xs text-yiwu-400">阶段 {i + 1}</span>
                <h4 className="text-sm font-medium text-white">{phase.name}</h4>
              </div>
              <div className="space-y-1.5">
                {phase.tasks.map((task, j) => (
                  <div key={j} className="flex items-center gap-2 text-sm">
                    <Circle size={14} className="text-gray-600 shrink-0" />
                    <span className="text-gray-300">{task}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
