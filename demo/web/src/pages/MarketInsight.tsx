import { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { TrendingUp, AlertTriangle, Star, Shield, ChevronDown, Loader2, RefreshCw, Sparkles, BadgeCheck, ExternalLink, Coins } from 'lucide-react';
import { useStore, categories } from '@/store/useStore';
import { fetchMarketInsight, type MarketInsightData } from '@/utils/api';
import { useApi } from '@/hooks/useApi';

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

  const urlCategory = searchParams.get('category');
  const category = urlCategory || selectedCategory;

  useEffect(() => {
    if (urlCategory && urlCategory !== selectedCategory) {
      setSelectedCategory(urlCategory);
    }
  }, [urlCategory, selectedCategory, setSelectedCategory]);

  const { data, loading, error, retry } = useApi<MarketInsightData>(
    () => fetchMarketInsight(category, targetMarket),
    [category, targetMarket],
  );

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-yiwu-500" />
        <span className="ml-3 text-gray-400">正在加载市场数据...</span>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="flex h-96 flex-col items-center justify-center gap-4">
        <AlertTriangle className="h-10 w-10 text-red-400" />
        <p className="text-gray-400">加载失败: {error}</p>
        <button onClick={retry} className="flex items-center gap-2 rounded-lg bg-yiwu-500/20 px-4 py-2 text-sm text-yiwu-400 hover:bg-yiwu-500/30 transition">
          <RefreshCw size={14} /> 重试
        </button>
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

      {/* 义乌指数（P1-1：官方发布真实值 + 实时汇率 + 演示基准，三态诚实标注） */}
      {data.yiwu_index && (
        <div className="glass-light rounded-xl p-6 space-y-4">
          {/* 标题 + 真伪徽章 */}
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-400">义乌指数 · {data.category}</p>
            {data.yiwu_index.is_real ? (
              <span className="flex items-center gap-1 rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400">
                <BadgeCheck size={14} /> 官方发布值 · 真实数据
              </span>
            ) : (
              <span className="flex items-center gap-1 rounded-full bg-gray-500/10 px-3 py-1 text-xs font-medium text-gray-400">
                演示基准值
              </span>
            )}
          </div>

          {/* 官方发布真实值 */}
          {data.yiwu_index.official?.is_real && data.yiwu_index.official.index_value != null && (
            <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-4">
              <div className="flex flex-wrap items-end justify-between gap-3">
                <div>
                  <p className="text-xs text-gray-400 mb-1">
                    官方发布值 · {data.yiwu_index.official.category_matched || data.category}
                    {data.yiwu_index.official.as_of ? ` · ${data.yiwu_index.official.as_of}` : ''}
                  </p>
                  <div className="flex items-end gap-3">
                    <span className="text-3xl font-bold text-white">{data.yiwu_index.official.index_value}</span>
                    <span className="rounded bg-white/5 px-2 py-0.5 text-xs text-gray-400">
                      {data.yiwu_index.official.scale || '官方千点基准'}
                    </span>
                    {data.yiwu_index.official.change_pct != null && (
                      <span className="text-sm font-medium text-yiwu-400">
                        环比 +{data.yiwu_index.official.change_pct}%
                      </span>
                    )}
                  </div>
                </div>
                {data.yiwu_index.official.source_url && (
                  <a
                    href={data.yiwu_index.official.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-xs text-yiwu-400 hover:text-yiwu-300 transition"
                  >
                    <ExternalLink size={12} /> 来源核验
                  </a>
                )}
              </div>
              {data.yiwu_index.official.fetched_at_iso && (
                <p className="mt-2 text-xs text-gray-500">
                  抓取时间：{data.yiwu_index.official.fetched_at_iso}
                  {data.yiwu_index.official.note ? ` · ${data.yiwu_index.official.note}` : ''}
                </p>
              )}
              {data.yiwu_index.official.excerpt && (
                <p className="mt-1 text-xs text-gray-600 italic">原文摘录：{data.yiwu_index.official.excerpt}</p>
              )}
            </div>
          )}

          {/* 实时汇率 */}
          {data.yiwu_index.exchange_rate?.is_real && data.yiwu_index.exchange_rate.rate != null && (
            <div className="flex flex-wrap items-center justify-between gap-2 rounded-lg bg-ocean-800/50 p-3">
              <span className="flex items-center gap-2 text-sm text-gray-300">
                <Coins size={16} className="text-gold-400" />
                USD/CNY 参考汇率
                <span className="font-bold text-white">{data.yiwu_index.exchange_rate.rate}</span>
              </span>
              <span className="text-xs text-gray-500">
                {data.yiwu_index.exchange_rate.as_of || ''}
                {data.yiwu_index.exchange_rate.provider ? ` · ${data.yiwu_index.exchange_rate.provider}` : ''}
              </span>
            </div>
          )}

          {/* 真实源不可用时的诚实提示 */}
          {data.yiwu_index.official && !data.yiwu_index.official.is_real && (
            <p className="text-xs text-gold-400/80">
              {data.yiwu_index.official.note || '义乌指数真实源暂不可用，以下显示演示基准值'}
            </p>
          )}

          {/* 演示基准（弱化标注，向后兼容，避免与真实值混淆） */}
          <div className="flex items-center justify-between border-t border-white/5 pt-3">
            <span className="text-xs text-gray-500">
              演示基准(98-110)·非实时：{data.yiwu_index.current}
            </span>
            <div className="flex items-center gap-3">
              <span className={`text-xs ${data.yiwu_index.change > 0 ? 'text-yiwu-400' : 'text-red-400'}`}>
                {data.yiwu_index.change > 0 ? '+' : ''}{data.yiwu_index.change} {data.yiwu_index.trend}
              </span>
              <span className="text-xs text-gray-500">品类指数: {data.yiwu_index.category_score}</span>
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
      <div className="text-xs text-gray-600 text-center leading-relaxed">
        数据来源: {data.data_sources?.join(' · ')}
        <br />
        义乌指数 / 汇率为真实接入（官方发布值 · 每日参考汇率，带时间戳可核验）；品类 / 竞争 / 价格等为演示静态值
      </div>

      {/* AI Insight */}
      {(data as MarketInsightData & { ai_insight?: string }).ai_insight && (
        <div className="glass-light rounded-xl p-6 border border-yiwu-500/20">
          <h3 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
            <Sparkles size={16} className="text-yiwu-400" /> AI 商业洞察
          </h3>
          <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-line">
            {(data as MarketInsightData & { ai_insight?: string }).ai_insight}
          </p>
        </div>
      )}
    </motion.div>
  );
}
