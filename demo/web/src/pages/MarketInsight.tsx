import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { TrendingUp, AlertTriangle, Star, Shield, ChevronDown, Loader2 } from 'lucide-react';
import { useStore, categories } from '@/store/useStore';
import { fetchMarketInsight, type MarketInsightData } from '@/utils/api';

const regions = ['欧洲（义新欧班列直达）', '中亚', '中东', '东南亚', '非洲', '南美'];

const impactDot: Record<string, string> = { high: 'bg-red-500', medium: 'bg-gold-500', low: 'bg-gray-500' };
const riskColor: Record<string, string> = {
  high: 'border-red-500/30 bg-red-500/5',
  medium: 'border-gold-500/30 bg-gold-500/5',
  low: 'border-gray-500/30 bg-gray-500/5',
};

export default function MarketInsight() {
  const [searchParams] = useSearchParams();
  const { selectedCategory, setSelectedCategory, targetMarket, setTargetMarket } = useStore();
  const [data, setData] = useState<MarketInsightData | null>(null);
  const [loading, setLoading] = useState(true);

  const urlCategory = searchParams.get('category');
  const category = urlCategory || selectedCategory;

  useEffect(() => {
    if (urlCategory && urlCategory !== selectedCategory) {
      setSelectedCategory(urlCategory);
    }
  }, [urlCategory, selectedCategory, setSelectedCategory]);

  useEffect(() => {
    setLoading(true);
    fetchMarketInsight(category, targetMarket)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [category, targetMarket]);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-yiwu-500" />
        <span className="ml-3 text-gray-400">正在加载市场数据...</span>
      </div>
    );
  }

  if (!data) {
    return <div className="flex h-96 items-center justify-center text-gray-500">暂无数据</div>;
  }

  const chartData = data.hot_categories.map((c) => ({
    name: c.name,
    value: parseFloat(c.share),
    growth: c.growth,
  }));

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      {/* Selectors */}
      <div className="flex flex-wrap gap-4">
        <div className="relative">
          <select
            value={category}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="appearance-none rounded-lg bg-ocean-800 px-4 py-2 pr-10 text-sm text-white border border-white/10 focus:border-yiwu-500 focus:outline-none"
          >
            {categories.map((c) => (<option key={c} value={c}>{c}</option>))}
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        </div>
        <div className="relative">
          <select
            value={targetMarket}
            onChange={(e) => setTargetMarket(e.target.value)}
            className="appearance-none rounded-lg bg-ocean-800 px-4 py-2 pr-10 text-sm text-white border border-white/10 focus:border-yiwu-500 focus:outline-none"
          >
            {regions.map((r) => (<option key={r} value={r}>{r}</option>))}
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        </div>
      </div>

      {/* 义乌指数 */}
      {data.yiwu_index && (
        <div className="glass-light rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400 mb-1">义乌指数 · {data.category}</p>
              <p className="text-xl font-bold text-white">{data.yiwu_index.current}</p>
            </div>
            <div className="flex items-center gap-4">
              <span className={`rounded-full px-3 py-1 text-sm font-medium ${data.yiwu_index.change > 0 ? 'bg-yiwu-500/10 text-yiwu-400' : 'bg-red-500/10 text-red-400'}`}>
                {data.yiwu_index.change > 0 ? '+' : ''}{data.yiwu_index.change} {data.yiwu_index.trend}
              </span>
              <span className="rounded-full bg-gold-500/10 px-3 py-1 text-sm font-medium text-gold-400">
                品类指数: {data.yiwu_index.category_score}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Market Size */}
      <div className="glass-light rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-400 mb-1">市场规模 · {data.region}</p>
            <p className="text-xl font-bold text-white">{data.market_size}</p>
          </div>
          <span className="rounded-full bg-yiwu-500/10 px-3 py-1 text-sm font-medium text-yiwu-400">
            +{data.market_growth} 增长
          </span>
        </div>
      </div>

      {/* Hot Categories Chart */}
      <div className="glass-light rounded-xl p-6">
        <h3 className="text-sm font-medium text-white mb-4 flex items-center gap-2">
          <TrendingUp size={16} className="text-yiwu-400" /> 热门品类
        </h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={chartData} layout="vertical" margin={{ left: 80 }}>
            <XAxis type="number" hide />
            <YAxis dataKey="name" type="category" tick={{ fill: '#9ca3af', fontSize: 12 }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{ background: '#0A1628', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }}
              formatter={(value: number) => [`${value}%`, '市场份额']}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={20}>
              {chartData.map((_, i) => (<Cell key={i} fill={i === 0 ? '#D4272C' : '#8b1a1d'} />))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Trends */}
      <div className="glass-light rounded-xl p-6">
        <h3 className="text-sm font-medium text-white mb-4">趋势分析</h3>
        <div className="space-y-3">
          {data.trends.map((t, i) => (
            <div key={i} className="flex items-start gap-3 rounded-lg bg-ocean-800/50 p-3">
              <span className={`mt-1 h-2 w-2 shrink-0 rounded-full ${impactDot[t.impact]}`} />
              <div>
                <span className="text-xs text-gray-500">{t.impact === 'high' ? '高影响' : t.impact === 'medium' ? '中影响' : '低影响'}</span>
                <p className="text-sm text-gray-300 mt-0.5">{t.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Price Tiers */}
      <div className="glass-light rounded-xl p-6">
        <h3 className="text-sm font-medium text-white mb-4">价格区间分布</h3>
        <div className="space-y-3">
          {data.price_tiers.map((pt, i) => {
            const pct = parseFloat(pt.volume_share);
            return (
              <div key={i}>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-300">{pt.tier}</span>
                  <span className="text-gray-500">{pt.price_range} · {pt.volume_share}</span>
                </div>
                <div className="h-2 rounded-full bg-ocean-800">
                  <div className="h-2 rounded-full bg-yiwu-500 transition-all" style={{ width: `${pct}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Competitors */}
      <div className="glass-light rounded-xl p-6">
        <h3 className="text-sm font-medium text-white mb-4">竞争格局</h3>
        <div className="space-y-3">
          {data.competitors.map((c, i) => {
            const share = parseFloat(c.market_share);
            return (
              <div key={i} className="rounded-lg bg-ocean-800/50 p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-white">{c.name}</span>
                  <span className="text-xs text-gold-400">{c.market_share}</span>
                </div>
                <div className="h-1.5 rounded-full bg-ocean-900">
                  <div className="h-1.5 rounded-full bg-gold-500" style={{ width: `${share * 3}%` }} />
                </div>
                {c.strength && <p className="text-xs text-gray-500 mt-1">优势: {c.strength}</p>}
              </div>
            );
          })}
        </div>
      </div>

      {/* Recommendations */}
      <div className="glass-light rounded-xl p-6">
        <h3 className="text-sm font-medium text-white mb-4 flex items-center gap-2">
          <Star size={16} className="text-gold-400" /> 推荐产品
        </h3>
        <div className="grid gap-3 sm:grid-cols-2">
          {data.recommendations.map((r, i) => (
            <div key={i} className="rounded-lg bg-ocean-800/50 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-white">{r.product}</span>
                <span className="text-xs text-gold-400">{r.rating}</span>
              </div>
              {r.reason && <p className="text-xs text-gray-400 mb-2">{r.reason}</p>}
              <span className="text-xs text-yiwu-400">预测销量: {r.predicted_sales}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Alerts */}
      <div className="glass-light rounded-xl p-6">
        <h3 className="text-sm font-medium text-white mb-4 flex items-center gap-2">
          <AlertTriangle size={16} className="text-red-400" /> 风险预警
        </h3>
        <div className="space-y-3">
          {data.risks.map((r, i) => (
            <div key={i} className={`rounded-lg border p-4 ${riskColor[r.level]}`}>
              <div className="flex items-center gap-2 mb-1">
                <Shield size={14} className="text-gray-400" />
                <span className="text-sm font-medium text-white">{r.description}</span>
                <span className="text-xs text-gray-500">
                  {r.level === 'high' ? '高风险' : r.level === 'medium' ? '中风险' : '低风险'}
                </span>
              </div>
              {r.mitigation && <p className="text-xs text-yiwu-400 mt-1">应对建议: {r.mitigation}</p>}
            </div>
          ))}
        </div>
      </div>

      {/* Data Sources */}
      <div className="text-xs text-gray-600 text-center">
        数据来源: {data.data_sources?.join(' · ')}
      </div>
    </motion.div>
  );
}
