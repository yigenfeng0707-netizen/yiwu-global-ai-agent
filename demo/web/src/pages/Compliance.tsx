import { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, Loader2, ShieldCheck, FileCheck, AlertTriangle, Calculator, CheckCircle2, XCircle, RefreshCw } from 'lucide-react';
import { categories } from '@/store/useStore';
import { fetchComplianceCheck, calculateTariff } from '@/utils/api';

const countries = ['德国', '法国', '西班牙', '荷兰', '波兰', '哈萨克斯坦', '乌兹别克斯坦', '沙特阿拉伯', '阿联酋', '伊朗', '土耳其', '印尼', '泰国', '越南', '马来西亚'];

interface Certification { name: string; required: boolean; estimated_time: string; estimated_cost: string; }
interface ClearanceDoc { name: string; required: boolean; description: string; }
interface ComplianceItem { item: string; status: 'pass' | 'fail'; risk_level: string; }
interface ComplianceView {
  category: string; target_country: string;
  certifications: Certification[];
  clearance_documents: ClearanceDoc[];
  compliance_checks: ComplianceItem[];
  special_requirements: string[];
}
interface TariffData {
  product_value: number; tariff_rate: string; tariff_amount: number;
  vat_rate: string; vat_amount: number; import_tax: number;
  total_tax: number; total_cost: number; rcep_benefits: string | null;
}

const riskColor: Record<string, string> = {
  high: 'text-red-400', medium: 'text-gold-400', low: 'text-yiwu-400',
};

export default function Compliance() {
  const [category, setCategory] = useState('电子电器');
  const [country, setCountry] = useState('德国');
  const [productValue, setProductValue] = useState(1000);
  const [loading, setLoading] = useState(false);
  const [tariffLoading, setTariffLoading] = useState(false);
  const [complianceData, setComplianceData] = useState<ComplianceView | null>(null);
  const [tariffData, setTariffData] = useState<TariffData | null>(null);
  const [error, setError] = useState('');
  const [tariffError, setTariffError] = useState('');

  const handleCheck = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await fetchComplianceCheck(category, country);
      const items = result.compliance_check?.checks || [];
      setComplianceData({
        category: result.category,
        target_country: result.target_country,
        certifications: result.certifications,
        clearance_documents: result.clearance_documents,
        compliance_checks: items.map((it) => ({
          item: it.item,
          status: it.status as 'pass' | 'fail',
          risk_level: it.risk_level,
        })),
        special_requirements: result.special_requirements ? [result.special_requirements] : [],
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : '查询失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleCalcTariff = async () => {
    setTariffLoading(true);
    setTariffError('');
    try {
      const result = await calculateTariff({ category, target_country: country, product_value: productValue });
      setTariffData(result as TariffData);
    } catch (err) {
      setTariffError(err instanceof Error ? err.message : '计算失败，请稍后重试');
    } finally {
      setTariffLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      {/* 选择器 */}
      <div className="glass-light rounded-xl p-6 space-y-4">
        <h3 className="text-sm font-medium text-white flex items-center gap-2">
          <ShieldCheck size={16} className="text-yiwu-400" /> 合规查询
        </h3>
        <div className="flex flex-wrap gap-4 items-end">
          <div className="relative">
            <select value={category} onChange={(e) => setCategory(e.target.value)}
              className="appearance-none rounded-lg bg-ocean-800 px-4 py-2 pr-10 text-sm text-white border border-white/10 focus:border-yiwu-500 focus:outline-none">
              {categories.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
            <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          </div>
          <div className="relative">
            <select value={country} onChange={(e) => setCountry(e.target.value)}
              className="appearance-none rounded-lg bg-ocean-800 px-4 py-2 pr-10 text-sm text-white border border-white/10 focus:border-yiwu-500 focus:outline-none">
              {countries.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
            <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          </div>
          <button onClick={handleCheck} disabled={loading}
            className="rounded-lg bg-yiwu-600 px-6 py-2 text-sm font-medium text-white hover:bg-yiwu-500 disabled:opacity-50 transition-colors flex items-center gap-2">
            {loading ? <Loader2 size={16} className="animate-spin" /> : <ShieldCheck size={16} />}
            检查合规
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-4 flex items-center justify-between">
          <span className="text-sm text-red-400">{error}</span>
          <button onClick={handleCheck} disabled={loading}
            className="rounded-lg bg-red-500/20 px-3 py-1.5 text-xs text-red-400 hover:bg-red-500/30 transition-colors flex items-center gap-1">
            <RefreshCw size={12} /> 重试
          </button>
        </div>
      )}

      {loading && (
        <div className="flex h-48 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-yiwu-500" />
          <span className="ml-3 text-gray-400">正在检查合规信息...</span>
        </div>
      )}

      {complianceData && !loading && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          {/* 认证要求 */}
          <div className="glass-light rounded-xl p-6">
            <h4 className="text-sm font-medium text-white mb-3 flex items-center gap-2"><FileCheck size={14} className="text-yiwu-400" /> 所需认证</h4>
            <div className="space-y-2">
              {complianceData.certifications.map((cert, i) => (
                <div key={i} className="flex items-center justify-between rounded-lg bg-ocean-800/50 p-3">
                  <div className="flex items-center gap-2">
                    {cert.required ? <CheckCircle2 size={14} className="text-red-400" /> : <CheckCircle2 size={14} className="text-gray-500" />}
                    <span className="text-sm text-gray-300">{cert.name}</span>
                    {cert.required && <span className="text-xs text-red-400">必须</span>}
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>周期: {cert.estimated_time}</span>
                    <span>费用: {cert.estimated_cost}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 清关文件 */}
          <div className="glass-light rounded-xl p-6">
            <h4 className="text-sm font-medium text-white mb-3 flex items-center gap-2"><FileCheck size={14} className="text-gold-400" /> 清关文件</h4>
            <div className="space-y-2">
              {complianceData.clearance_documents.map((doc, i) => (
                <div key={i} className="flex items-center gap-3 rounded-lg bg-ocean-800/50 p-3">
                  {doc.required ? <CheckCircle2 size={14} className="text-yiwu-400" /> : <XCircle size={14} className="text-gray-600" />}
                  <div>
                    <span className="text-sm text-gray-300">{doc.name}</span>
                    <p className="text-xs text-gray-500">{doc.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 合规检查结果 */}
          <div className="glass-light rounded-xl p-6">
            <h4 className="text-sm font-medium text-white mb-3 flex items-center gap-2"><ShieldCheck size={14} className="text-yiwu-400" /> 合规检查</h4>
            <div className="space-y-2">
              {complianceData.compliance_checks.map((item, i) => (
                <div key={i} className="flex items-center justify-between rounded-lg bg-ocean-800/50 p-3">
                  <div className="flex items-center gap-2">
                    {item.status === 'pass' ? <CheckCircle2 size={14} className="text-yiwu-400" /> : <XCircle size={14} className="text-red-400" />}
                    <span className="text-sm text-gray-300">{item.item}</span>
                  </div>
                  <span className={`text-xs ${riskColor[item.risk_level] || 'text-gray-400'}`}>
                    {item.risk_level === 'high' ? '高风险' : item.risk_level === 'medium' ? '中风险' : '低风险'}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* 特殊要求 */}
          {complianceData.special_requirements.length > 0 && (
            <div className="rounded-lg border border-gold-500/20 bg-gold-500/5 p-4">
              <p className="text-xs text-gold-400 mb-2 flex items-center gap-1"><AlertTriangle size={12} /> 特殊要求</p>
              {complianceData.special_requirements.map((req, i) => (
                <p key={i} className="text-xs text-gray-400">• {req}</p>
              ))}
            </div>
          )}
        </motion.div>
      )}

      {/* 关税计算器 */}
      <div className="glass-light rounded-xl p-6 space-y-4">
        <h3 className="text-sm font-medium text-white flex items-center gap-2">
          <Calculator size={16} className="text-gold-400" /> 关税计算器
        </h3>
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="text-xs text-gray-500 mb-1 block">商品价值</label>
            <input type="number" value={productValue} onChange={(e) => setProductValue(Number(e.target.value))}
              className="rounded-lg bg-ocean-800 px-4 py-2 text-sm text-white border border-white/10 focus:border-yiwu-500 focus:outline-none w-32" />
          </div>
          <button onClick={handleCalcTariff} disabled={tariffLoading}
            className="rounded-lg bg-gold-600 px-6 py-2 text-sm font-medium text-white hover:bg-gold-500 disabled:opacity-50 transition-colors flex items-center gap-2">
            {tariffLoading ? <Loader2 size={16} className="animate-spin" /> : <Calculator size={16} />}
            计算关税
          </button>
        </div>
        {tariffError && (
          <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-3 flex items-center justify-between">
            <span className="text-xs text-red-400">{tariffError}</span>
            <button onClick={handleCalcTariff} disabled={tariffLoading}
              className="rounded-lg bg-red-500/20 px-2 py-1 text-xs text-red-400 hover:bg-red-500/30 transition-colors flex items-center gap-1">
              <RefreshCw size={10} /> 重试
            </button>
          </div>
        )}
        {tariffData && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 mt-2">
            {[
              { label: '商品价值', value: `¥${tariffData.product_value}` },
              { label: '关税', value: `${tariffData.tariff_rate} / ¥${tariffData.tariff_amount}` },
              { label: '增值税', value: `${tariffData.vat_rate} / ¥${tariffData.vat_amount}` },
              { label: '进口税', value: `¥${tariffData.import_tax}` },
              { label: '税费合计', value: `¥${tariffData.total_tax}`, highlight: true },
              { label: '总成本', value: `¥${tariffData.total_cost}`, highlight: true },
            ].map((item, i) => (
              <div key={i} className={`rounded-lg p-3 ${item.highlight ? 'bg-yiwu-500/10 border border-yiwu-500/20' : 'bg-ocean-800/50'}`}>
                <p className="text-xs text-gray-500">{item.label}</p>
                <p className={`text-sm font-medium ${item.highlight ? 'text-yiwu-400' : 'text-white'}`}>{item.value}</p>
              </div>
            ))}
            {tariffData.rcep_benefits && (
              <div className="sm:col-span-2 lg:col-span-4 rounded-lg bg-gold-500/5 border border-gold-500/20 p-3">
                <p className="text-xs text-gold-400">优惠: {tariffData.rcep_benefits}</p>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
