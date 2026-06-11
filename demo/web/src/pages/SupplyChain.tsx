import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ChevronDown, Loader2, Building2, Package, FileCheck,
  Train, ShieldCheck, CheckCircle2, Circle, Star,
} from 'lucide-react';
import { categories } from '@/store/useStore';
import { fetchSupplyChain, fetchYixinouLogistics, type SupplyChainData, type LogisticsData } from '@/utils/api';

const regions = ['欧洲（义新欧班列直达）', '中亚', '中东', '东南亚', '非洲', '南美'];
const budgets = ['低', '中', '高'];

export default function SupplyChain() {
  const [category, setCategory] = useState(categories[0]);
  const [region, setRegion] = useState(regions[0]);
  const [budget, setBudget] = useState('中');
  const [data, setData] = useState<SupplyChainData | null>(null);
  const [logistics, setLogistics] = useState<LogisticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [logisticsLoading, setLogisticsLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetchSupplyChain(category, region, budget)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [category, region, budget]);

  const handleLoadLogistics = async () => {
    setLogisticsLoading(true);
    try {
      const result = await fetchYixinouLogistics(region);
      setLogistics(result as LogisticsData);
    } catch {
      setLogistics(null);
    } finally {
      setLogisticsLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-yiwu-500" />
        <span className="ml-3 text-gray-400">正在匹配供应链...</span>
      </div>
    );
  }

  if (!data) {
    return <div className="flex h-96 items-center justify-center text-gray-500">暂无数据</div>;
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      {/* 选择器 */}
      <div className="flex flex-wrap gap-4">
        <div className="relative">
          <select value={category} onChange={(e) => setCategory(e.target.value)}
            className="appearance-none rounded-lg bg-ocean-800 px-4 py-2 pr-10 text-sm text-white border border-white/10 focus:border-yiwu-500 focus:outline-none">
            {categories.map((c) => (<option key={c} value={c}>{c}</option>))}
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        </div>
        <div className="relative">
          <select value={region} onChange={(e) => setRegion(e.target.value)}
            className="appearance-none rounded-lg bg-ocean-800 px-4 py-2 pr-10 text-sm text-white border border-white/10 focus:border-yiwu-500 focus:outline-none">
            {regions.map((r) => (<option key={r} value={r}>{r}</option>))}
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
      </div>

      {/* 供应链评分 + 义乌商贸城信息 */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="glass-light rounded-xl p-6 flex flex-col items-center justify-center">
          <p className="text-sm text-gray-400 mb-3">供应链评分</p>
          <div className="relative inline-flex items-center justify-center">
            <svg width={120} height={120} className="-rotate-90">
              <circle cx={60} cy={60} r={50} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={8} />
              <circle cx={60} cy={60} r={50} fill="none" stroke="#D4272C" strokeWidth={8} strokeLinecap="round"
                strokeDasharray={`${(data.supply_score?.total || 0) * 3.14} ${314 - (data.supply_score?.total || 0) * 3.14}`} />
            </svg>
            <div className="absolute flex flex-col items-center">
              <span className="text-2xl font-bold text-yiwu-400">{data.supply_score?.total || '-'}</span>
              <span className="text-xs text-gray-400">{data.supply_score?.level || '-'}</span>
            </div>
          </div>
        </div>
        <div className="glass-light rounded-xl p-6 lg:col-span-2">
          <h3 className="text-sm font-medium text-white mb-4 flex items-center gap-2">
            <Building2 size={16} className="text-yiwu-400" /> 义乌国际商贸城
          </h3>
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-lg bg-ocean-800/50 p-4">
              <p className="text-xs text-gray-500 mb-1">商户总数</p>
              <span className="text-lg font-bold text-white">{data.yiwu_trade_city?.total_shops?.toLocaleString() || '75,000'}</span>
            </div>
            <div className="rounded-lg bg-ocean-800/50 p-4">
              <p className="text-xs text-gray-500 mb-1">SKU总数</p>
              <span className="text-lg font-bold text-white">{data.yiwu_trade_city?.total_skus?.toLocaleString() || '2,100,000'}</span>
            </div>
            <div className="rounded-lg bg-ocean-800/50 p-4">
              <p className="text-xs text-gray-500 mb-1">所在区域</p>
              <span className="text-lg font-bold text-yiwu-400">{data.yiwu_trade_city?.district || '-'}</span>
            </div>
          </div>
          {data.supply_score?.dimensions && (
            <div className="mt-4 space-y-2">
              {Object.entries(data.supply_score.dimensions).map(([key, value]) => (
                <div key={key}>
                  <div className="flex items-center justify-between text-xs mb-0.5">
                    <span className="text-gray-400">{key}</span>
                    <span className="text-gray-500">{value as number}</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-ocean-900">
                    <div className="h-1.5 rounded-full bg-yiwu-500/70" style={{ width: `${value}%` }} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 供应商匹配 */}
      <div className="glass-light rounded-xl p-6">
        <h3 className="text-sm font-medium text-white mb-4 flex items-center gap-2">
          <Package size={16} className="text-yiwu-400" /> 供应商匹配
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-500 text-xs border-b border-white/5">
                <th className="pb-2 text-left font-medium">供应商</th>
                <th className="pb-2 text-left font-medium">产品</th>
                <th className="pb-2 text-left font-medium">区域</th>
                <th className="pb-2 text-left font-medium">MOQ</th>
                <th className="pb-2 text-left font-medium">单价</th>
                <th className="pb-2 text-left font-medium">交期</th>
                <th className="pb-2 text-left font-medium">评分</th>
                <th className="pb-2 text-left font-medium">推荐</th>
              </tr>
            </thead>
            <tbody>
              {data.suppliers?.map((s, i) => (
                <tr key={i} className="border-b border-white/5">
                  <td className="py-2 text-white">{s.supplier}</td>
                  <td className="py-2 text-gray-300">{s.product}</td>
                  <td className="py-2 text-gray-400">{s.district}</td>
                  <td className="py-2 text-gray-400">{s.moq}</td>
                  <td className="py-2 text-gray-400">{s.unit_price}</td>
                  <td className="py-2 text-gray-400">{s.delivery_days}天</td>
                  <td className="py-2 text-gray-400">{s.rating}</td>
                  <td className="py-2">{s.recommended ? <CheckCircle2 size={16} className="text-yiwu-400" /> : <Circle size={16} className="text-gray-600" />}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 采购信息 */}
      <div className="glass-light rounded-xl p-6">
        <h3 className="text-sm font-medium text-white mb-4 flex items-center gap-2">
          <Star size={16} className="text-gold-400" /> 采购信息
        </h3>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-lg bg-ocean-800/50 p-3">
            <p className="text-xs text-gray-500">价格区间</p>
            <p className="text-sm font-medium text-white">{data.purchase_info?.avg_price_range || '-'}</p>
          </div>
          <div className="rounded-lg bg-ocean-800/50 p-3">
            <p className="text-xs text-gray-500">样品交期</p>
            <p className="text-sm font-medium text-white">{data.purchase_info?.sample_lead_time || '-'}</p>
          </div>
          <div className="rounded-lg bg-ocean-800/50 p-3">
            <p className="text-xs text-gray-500">批量交期</p>
            <p className="text-sm font-medium text-white">{data.purchase_info?.bulk_lead_time || '-'}</p>
          </div>
          <div className="rounded-lg bg-ocean-800/50 p-3">
            <p className="text-xs text-gray-500">义乌优势</p>
            <p className="text-sm font-medium text-yiwu-400 line-clamp-2">{data.purchase_info?.yiwu_advantage || '-'}</p>
          </div>
        </div>
      </div>

      {/* 义新欧班列物流 */}
      <div className="glass-light rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-white flex items-center gap-2">
            <Train size={16} className="text-yiwu-400" /> 义新欧班列物流
          </h3>
          <button onClick={handleLoadLogistics} disabled={logisticsLoading}
            className="rounded-lg bg-yiwu-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-yiwu-500 disabled:opacity-50 transition-colors flex items-center gap-1">
            {logisticsLoading ? <Loader2 size={12} className="animate-spin" /> : <Train size={12} />}
            查看物流详情
          </button>
        </div>
        {logistics ? (
          <div className="space-y-4">
            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-lg bg-ocean-800/50 p-3">
                <p className="text-xs text-gray-500">线路总数</p>
                <p className="text-lg font-bold text-white">{logistics.total_routes}</p>
              </div>
              <div className="rounded-lg bg-ocean-800/50 p-3">
                <p className="text-xs text-gray-500">覆盖国家</p>
                <p className="text-lg font-bold text-white">{logistics.countries_covered}</p>
              </div>
              <div className="rounded-lg bg-ocean-800/50 p-3">
                <p className="text-xs text-gray-500">覆盖城市</p>
                <p className="text-lg font-bold text-white">{logistics.cities_connected}</p>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-gray-500 text-xs border-b border-white/5">
                    <th className="pb-2 text-left font-medium">线路</th>
                    <th className="pb-2 text-left font-medium">运输天数</th>
                    <th className="pb-2 text-left font-medium">班次</th>
                    <th className="pb-2 text-left font-medium">20尺柜</th>
                    <th className="pb-2 text-left font-medium">40尺柜</th>
                  </tr>
                </thead>
                <tbody>
                  {logistics.routes?.map((r, i) => (
                    <tr key={i} className="border-b border-white/5">
                      <td className="py-2 text-white">{r.name}</td>
                      <td className="py-2 text-yiwu-400">{r.days}天</td>
                      <td className="py-2 text-gray-400">{r.frequency}</td>
                      <td className="py-2 text-gray-400">{r.cost_20ft}</td>
                      <td className="py-2 text-gray-400">{r.cost_40ft}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-lg bg-ocean-800/50 p-3">
              <p className="text-xs text-gray-500">线路总数</p>
              <p className="text-lg font-bold text-white">19</p>
            </div>
            <div className="rounded-lg bg-ocean-800/50 p-3">
              <p className="text-xs text-gray-500">覆盖国家</p>
              <p className="text-lg font-bold text-white">50+</p>
            </div>
            <div className="rounded-lg bg-ocean-800/50 p-3">
              <p className="text-xs text-gray-500">覆盖城市</p>
              <p className="text-lg font-bold text-white">160+</p>
            </div>
          </div>
        )}
      </div>

      {/* 1039市场采购贸易 */}
      <div className="glass-light rounded-xl p-6">
        <h3 className="text-sm font-medium text-white mb-4 flex items-center gap-2">
          <FileCheck size={16} className="text-gold-400" /> 1039市场采购贸易
        </h3>
        <div className="rounded-lg bg-yiwu-500/5 border border-yiwu-500/20 p-4 mb-4">
          <p className="text-sm text-yiwu-400 font-medium mb-1">{data.trade_1039?.name || '市场采购贸易方式（1039）'}</p>
          <p className="text-xs text-gray-400">{data.trade_1039?.description || ''}</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <p className="text-xs text-gray-500 mb-2">核心优势</p>
            <div className="space-y-1.5">
              {(data.trade_1039?.advantages || []).map((a, i) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                  <CheckCircle2 size={14} className="text-yiwu-400 shrink-0" />
                  <span className="text-gray-300">{a}</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-2">适用条件</p>
            <div className="space-y-1.5">
              {(data.trade_1039?.conditions || []).map((c, i) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                  <ShieldCheck size={14} className="text-gold-400 shrink-0" />
                  <span className="text-gray-300">{c}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
