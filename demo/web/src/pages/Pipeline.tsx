import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronRight, Download, Loader2, Play, CheckCircle2, Circle, BarChart3, Target, Sparkles, ShieldCheck, HelpCircle, Truck, RefreshCw, Building2 } from 'lucide-react';
import { categories } from '@/store/useStore';
import { runPipeline, type PipelineResult } from '@/utils/api';
import { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, AlignmentType, BorderStyle, ShadingType } from 'docx';
import { saveAs } from 'file-saver';

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
  { key: 'customer_service', label: '出海FAQ包', icon: HelpCircle },
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
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());

  const toggleStep = (key: string) => {
    setExpandedSteps((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  const handleRun = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    setStepStatuses(steps.map(() => 'pending'));
    setExpandedSteps(new Set());

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

  const handleDownloadReport = async () => {
    if (!result) return;
    const date = new Date().toISOString().slice(0, 10);
    const fileName = `出海方案_${category}_${targetCountry}_${date}.docx`;

    const YIWU_RED = 'D4272C';
    const DARK = '1a1a2e';
    const GRAY = '666666';

    const heading = (text: string) => new Paragraph({
      heading: HeadingLevel.HEADING_1,
      spacing: { before: 400, after: 200 },
      children: [new TextRun({ text, bold: true, size: 28, color: YIWU_RED, font: 'Microsoft YaHei' })],
    });

    const subHeading = (text: string) => new Paragraph({
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 300, after: 100 },
      children: [new TextRun({ text, bold: true, size: 22, color: DARK, font: 'Microsoft YaHei' })],
    });

    const bodyText = (label: string, value: string) => new Paragraph({
      spacing: { before: 60, after: 60 },
      children: [
        new TextRun({ text: `${label}：`, bold: true, size: 20, color: GRAY, font: 'Microsoft YaHei' }),
        new TextRun({ text: value, size: 20, color: DARK, font: 'Microsoft YaHei' }),
      ],
    });

    const bulletText = (text: string) => new Paragraph({
      spacing: { before: 40, after: 40 },
      bullet: { level: 0 },
      children: [new TextRun({ text, size: 20, color: DARK, font: 'Microsoft YaHei' })],
    });

    const divider = () => new Paragraph({
      spacing: { before: 100, after: 100 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' } },
      children: [],
    });

    const state = result.state as Record<string, Record<string, unknown>>;
    const children: Paragraph[] = [];

    // 封面
    children.push(new Paragraph({ spacing: { before: 2000 }, children: [] }));
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 200 },
      children: [new TextRun({ text: '义乌小商品出海智能体-OPC', bold: true, size: 44, color: YIWU_RED, font: 'Microsoft YaHei' })],
    }));
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 100 },
      children: [new TextRun({ text: '全链路出海方案报告', bold: true, size: 32, color: DARK, font: 'Microsoft YaHei' })],
    }));
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 400 },
      children: [new TextRun({ text: `${category} · ${targetCountry} · ${date}`, size: 22, color: GRAY, font: 'Microsoft YaHei' })],
    }));
    children.push(divider());

    // 基本信息
    children.push(heading('基本信息'));
    children.push(bodyText('品类', category));
    children.push(bodyText('目标区域', region));
    children.push(bodyText('预算等级', budget));
    children.push(bodyText('目标国家', targetCountry));
    children.push(bodyText('目标平台', platform));
    children.push(bodyText('目标语言', targetLang));
    children.push(bodyText('完成步骤', `${result.summary.steps_completed}/${result.summary.total_steps}`));
    children.push(bodyText('执行耗时', `${result.summary.duration_seconds.toFixed(1)}秒`));
    children.push(divider());

    // 7步详情
    const stepLabels: Record<string, string> = {
      market_insight: '一、市场洞察',
      smart_selection: '二、智能选品',
      supply_chain: '三、供应链匹配',
      content_generation: '四、跨境内容生成',
      compliance: '五、合规查询',
      customer_service: '六、出海FAQ包',
      policy_replication: '七、政策复制',
    };

    for (const [key, label] of Object.entries(stepLabels)) {
      const stepData = state[key];
      if (!stepData) continue;

      children.push(heading(label));

      if (key === 'market_insight') {
        children.push(subHeading('市场概况'));
        children.push(bodyText('市场规模', String(stepData.market_size || '-')));
        children.push(bodyText('增长率', String(stepData.market_growth || '-')));
        const trends = stepData.trends as { description: string; impact: string }[] | undefined;
        if (trends?.length) {
          children.push(subHeading('趋势关键词'));
          trends.forEach(t => children.push(bulletText(`[${t.impact === 'high' ? '高' : t.impact === 'medium' ? '中' : '低'}影响] ${t.description}`)));
        }
        const competitors = stepData.competitors as { name: string; market_share: string; strength?: string }[] | undefined;
        if (competitors?.length) {
          children.push(subHeading('竞争分析'));
          competitors.forEach(c => children.push(bulletText(`${c.name} - 市场份额${c.market_share}${c.strength ? ` - ${c.strength}` : ''}`)));
        }
        const recs = stepData.recommendations as { product: string; rating: number; reason?: string }[] | undefined;
        if (recs?.length) {
          children.push(subHeading('推荐商品'));
          recs.forEach(r => children.push(bulletText(`${r.product}（评分${r.rating}）${r.reason ? ` - ${r.reason}` : ''}`)));
        }
      }

      else if (key === 'smart_selection') {
        const score = stepData.overall_score as Record<string, unknown> | undefined;
        children.push(subHeading('综合评分'));
        children.push(bodyText('总分', score ? String(score.total) : '-'));
        children.push(bodyText('等级', score ? String(score.level) : '-'));
        const opp = stepData.market_opportunity as Record<string, string> | undefined;
        if (opp) {
          children.push(subHeading('市场机会'));
          children.push(bodyText('市场规模', opp.market_size || '-'));
          children.push(bodyText('增长率', opp.growth_rate || '-'));
          children.push(bodyText('竞争程度', opp.competition_level || '-'));
        }
        const products = stepData.product_recommendations as { product: string; suggested_moq: number; estimated_roi: string }[] | undefined;
        if (products?.length) {
          children.push(subHeading('推荐商品'));
          products.forEach(p => children.push(bulletText(`${p.product} | 起订量${p.suggested_moq}件 | ROI ${p.estimated_roi}`)));
        }
      }

      else if (key === 'supply_chain') {
        const score = stepData.supply_score as Record<string, unknown> | undefined;
        children.push(subHeading('供应链评分'));
        children.push(bodyText('总分', score ? String(score.total) : '-'));
        children.push(bodyText('等级', score ? String(score.level) : '-'));
        const suppliers = stepData.suppliers as { supplier: string; unit_price?: string; moq?: number; delivery_days?: number; rating?: number; recommended?: boolean }[] | undefined;
        if (suppliers?.length) {
          children.push(subHeading('供应商列表'));
          suppliers.forEach(s => children.push(bulletText(`${s.recommended ? '★ ' : ''}${s.supplier} | 价格${s.unit_price || '-'} | MOQ ${s.moq || '-'}件 | 交期${s.delivery_days || '-'}天 | 评分${s.rating || '-'}`)));
        }
        const logistics = stepData.logistics as Record<string, unknown> | undefined;
        if (logistics) {
          children.push(subHeading('义新欧班列物流'));
          children.push(bodyText('线路数', String(logistics.total_routes || '-')));
          children.push(bodyText('覆盖国家', String(logistics.countries_covered || '-')));
          const routes = logistics.routes as { name: string; days: number; frequency: string; cost_20ft?: string }[] | undefined;
          if (routes?.length) routes.forEach(r => children.push(bulletText(`${r.name} | ${r.days}天 | ${r.frequency}${r.cost_20ft ? ` | ${r.cost_20ft}` : ''}`)));
        }
      }

      else if (key === 'content_generation') {
        const content = stepData.content as Record<string, unknown> | undefined;
        children.push(subHeading('内容概览'));
        children.push(bodyText('标题', content?.title ? String(content.title) : '-'));
        children.push(bodyText('描述', content?.description ? String(content.description) : '-'));
        if (content?.seo_keywords && Array.isArray(content.seo_keywords)) {
          children.push(bodyText('SEO关键词', (content.seo_keywords as string[]).join('、')));
        }
        const marketing = stepData.marketing as Record<string, unknown> | undefined;
        const social = marketing?.social_copy as Record<string, unknown> | undefined;
        if (social) {
          children.push(subHeading('社媒文案'));
          if (social.hook) children.push(bodyText('Hook', String(social.hook)));
          if (social.pain_point) children.push(bodyText('痛点', String(social.pain_point)));
          if (social.solution) children.push(bodyText('方案', String(social.solution)));
          if (social.cta) children.push(bodyText('CTA', String(social.cta)));
          if (social.hashtags && Array.isArray(social.hashtags)) children.push(bodyText('Hashtags', (social.hashtags as string[]).join(' ')));
        }
      }

      else if (key === 'compliance') {
        children.push(subHeading('目标国家'));
        children.push(bodyText('国家', String(stepData.target_country || '-')));
        const certs = stepData.certifications as { name: string; required: boolean; estimated_time: string; estimated_cost: string }[] | undefined;
        if (certs?.length) {
          children.push(subHeading('认证要求'));
          certs.forEach(c => children.push(bulletText(`${c.required ? '[必须]' : '[可选]'} ${c.name} | 耗时${c.estimated_time} | 费用${c.estimated_cost}`)));
        }
        if (stepData.tariff) children.push(bodyText('总税费', String((stepData.tariff as Record<string, unknown>).total_tax || '-')));
        const trade1039 = stepData.trade_1039 as Record<string, unknown> | undefined;
        if (trade1039) {
          children.push(subHeading('1039模式建议'));
          children.push(bodyText('是否适用', trade1039.applicable ? '是' : '否'));
          if (trade1039.advantages && Array.isArray(trade1039.advantages)) (trade1039.advantages as string[]).forEach(a => children.push(bulletText(a)));
        }
        const rcep = stepData.rcep_benefits as Record<string, unknown> | undefined;
        if (rcep) children.push(bodyText('RCEP优惠', String(rcep.description || '可享受关税优惠')));
      }

      else if (key === 'customer_service') {
        const faqs = stepData.faqs as { question: string; answer: string }[] | undefined;
        if (faqs?.length) {
          children.push(subHeading('出海FAQ'));
          faqs.forEach((faq, i) => {
            children.push(new Paragraph({
              spacing: { before: 120, after: 40 },
              children: [new TextRun({ text: `Q${i + 1}: ${faq.question}`, bold: true, size: 20, color: DARK, font: 'Microsoft YaHei' })],
            }));
            children.push(new Paragraph({
              spacing: { before: 40, after: 80 },
              children: [new TextRun({ text: `A: ${faq.answer}`, size: 20, color: GRAY, font: 'Microsoft YaHei' })],
            }));
          });
        }
      }

      else if (key === 'policy_replication') {
        children.push(bodyText('试点城市数', String(stepData.total_cities || 39)));
        const keyPoints = stepData.key_points as { title: string; description: string; benefit_level: string }[] | undefined;
        if (keyPoints?.length) {
          children.push(subHeading('政策要点'));
          keyPoints.forEach(p => children.push(bulletText(`[${p.benefit_level}收益] ${p.title}：${p.description}`)));
        }
        const tax = stepData.tax_benefits as Record<string, unknown> | undefined;
        if (tax) {
          children.push(subHeading('红利计算'));
          children.push(bodyText('增值税', tax.vat_exemption ? '免征' : '需缴纳'));
          children.push(bodyText('所得税', String(tax.income_tax || '-')));
          children.push(bodyText('印花税', String(tax.stamp_duty || '-')));
        }
        const cases = stepData.cases as { title: string; category: string; target_market: string; annual_export: string }[] | undefined;
        if (cases?.length) {
          children.push(subHeading('成功案例'));
          cases.forEach(c => children.push(bulletText(`${c.title} | ${c.category} | ${c.target_market} | 年出口${c.annual_export}`)));
        }
      }

      children.push(divider());
    }

    // 页脚
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 400 },
      children: [new TextRun({ text: '—— 义乌小商品出海智能体-OPC 生成 ——', size: 18, color: GRAY, font: 'Microsoft YaHei', italics: true })],
    }));

    const doc = new Document({
      sections: [{ properties: {}, children }],
    });

    const blob = await Packer.toBlob(doc);
    saveAs(blob, fileName);
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
            const isExpanded = expandedSteps.has(step.key);
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
                    <div
                      className={`flex items-center gap-2 ${status === 'completed' && stepData ? 'cursor-pointer' : ''}`}
                      onClick={() => { if (status === 'completed' && stepData) toggleStep(step.key); }}
                    >
                      <Icon size={16} className={status === 'completed' ? 'text-yiwu-400' : status === 'running' ? 'text-gold-400' : 'text-gray-600'} />
                      <span className={`text-sm font-medium ${status === 'completed' ? 'text-white' : status === 'running' ? 'text-gold-400' : 'text-gray-500'}`}>
                        {step.label}
                      </span>
                      {status === 'running' && <span className="text-xs text-gold-400">执行中...</span>}
                      {status === 'completed' && stepData && (
                        isExpanded
                          ? <ChevronDown size={14} className="text-gray-400" />
                          : <ChevronRight size={14} className="text-gray-400" />
                      )}
                    </div>
                    {status === 'completed' && stepData && (
                      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                        className="mt-2 rounded-lg bg-ocean-800/50 p-3">
                        <StepSummary stepKey={step.key} data={stepData} />
                      </motion.div>
                    )}
                    <AnimatePresence>
                      {status === 'completed' && stepData && isExpanded && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.2 }}
                          className="overflow-hidden"
                        >
                          <StepDetail stepKey={step.key} data={stepData} />
                        </motion.div>
                      )}
                    </AnimatePresence>
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
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-white">执行总览</h3>
            <button onClick={handleDownloadReport}
              className="rounded-lg bg-yiwu-600/80 px-4 py-1.5 text-xs font-medium text-white hover:bg-yiwu-500 transition-colors flex items-center gap-1.5">
              <Download size={14} /> 下载完整报告
            </button>
          </div>
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

/* ==================== 步骤详情面板 ==================== */

function DetailSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-3">
      <h5 className="text-xs font-medium text-gold-400 mb-1.5">{title}</h5>
      {children}
    </div>
  );
}

function DetailRow({ label, value, valueClass }: { label: string; value: string; valueClass?: string }) {
  return (
    <div className="flex items-start gap-2 text-xs">
      <span className="text-gray-500 shrink-0">{label}:</span>
      <span className={valueClass || 'text-white'}>{value}</span>
    </div>
  );
}

function StepDetail({ stepKey, data }: { stepKey: string; data: unknown }) {
  const d = data as Record<string, unknown>;

  switch (stepKey) {
    case 'market_insight':
      return <MarketInsightDetail d={d} />;
    case 'smart_selection':
      return <SmartSelectionDetail d={d} />;
    case 'supply_chain':
      return <SupplyChainDetail d={d} />;
    case 'content_generation':
      return <ContentGenerationDetail d={d} />;
    case 'compliance':
      return <ComplianceDetail d={d} />;
    case 'customer_service':
      return <CustomerServiceDetail d={d} />;
    case 'policy_replication':
      return <PolicyReplicationDetail d={d} />;
    default:
      return null;
  }
}

function MarketInsightDetail({ d }: { d: Record<string, unknown> }) {
  const trends = Array.isArray(d.trends) ? d.trends as { description: string; impact: string }[] : [];
  const competitors = Array.isArray(d.competitors) ? d.competitors as { name: string; market_share: string; strength?: string }[] : [];
  const recommendations = Array.isArray(d.recommendations) ? d.recommendations as { product: string; rating: number; reason?: string }[] : [];

  return (
    <div className="mt-2 rounded-lg bg-ocean-900/60 p-3 space-y-0">
      <DetailSection title="市场概况">
        <div className="space-y-1">
          <DetailRow label="市场规模" value={String(d.market_size || '-')} valueClass="text-white font-medium" />
          <DetailRow label="增长率" value={String(d.market_growth || '-')} valueClass="text-yiwu-400" />
        </div>
      </DetailSection>

      {trends.length > 0 && (
        <DetailSection title="趋势关键词">
          <div className="space-y-1">
            {trends.map((t, i) => (
              <div key={i} className="flex items-start gap-2 text-xs">
                <span className={`shrink-0 mt-0.5 w-1.5 h-1.5 rounded-full ${t.impact === 'high' ? 'bg-red-400' : t.impact === 'medium' ? 'bg-gold-400' : 'bg-green-400'}`} />
                <span className="text-gray-300">{t.description}</span>
              </div>
            ))}
          </div>
        </DetailSection>
      )}

      {competitors.length > 0 && (
        <DetailSection title="竞争分析">
          <div className="space-y-1">
            {competitors.map((c, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <span className="text-white">{c.name}</span>
                <span className="text-yiwu-400">{c.market_share}</span>
                {c.strength && <span className="text-gray-500">- {c.strength}</span>}
              </div>
            ))}
          </div>
        </DetailSection>
      )}

      {recommendations.length > 0 && (
        <DetailSection title="推荐理由">
          <div className="space-y-1">
            {recommendations.map((r, i) => (
              <div key={i} className="flex items-start gap-2 text-xs">
                <span className="text-yiwu-400 font-medium">{r.product}</span>
                <span className="text-gray-400">评分{r.rating}</span>
                {r.reason && <span className="text-gray-300">- {r.reason}</span>}
              </div>
            ))}
          </div>
        </DetailSection>
      )}
    </div>
  );
}

function SmartSelectionDetail({ d }: { d: Record<string, unknown> }) {
  const overallScore = d.overall_score as Record<string, unknown> | undefined;
  const marketOpp = d.market_opportunity as Record<string, string> | undefined;
  const products = Array.isArray(d.product_recommendations) ? d.product_recommendations as { product: string; scores: Record<string, number>; suggested_moq: number; estimated_roi: string }[] : [];

  return (
    <div className="mt-2 rounded-lg bg-ocean-900/60 p-3 space-y-0">
      <DetailSection title="综合评分">
        <div className="space-y-1">
          <DetailRow label="总分" value={overallScore ? String(overallScore.total) : '-'} valueClass="text-yiwu-400 font-medium" />
          <DetailRow label="等级" value={overallScore ? String(overallScore.level) : '-'} valueClass="text-white" />
          {products.length > 0 && products[0].scores && (
            <div className="mt-1 space-y-0.5">
              {Object.entries(products[0].scores).map(([k, v]) => (
                <div key={k} className="flex items-center gap-2 text-xs">
                  <span className="text-gray-500">{k}:</span>
                  <div className="flex-1 h-1.5 bg-ocean-800 rounded-full overflow-hidden">
                    <div className="h-full bg-yiwu-500 rounded-full" style={{ width: `${Math.min(Number(v), 100)}%` }} />
                  </div>
                  <span className="text-white w-6 text-right">{v}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </DetailSection>

      {marketOpp && (
        <DetailSection title="市场机会">
          <div className="space-y-1">
            <DetailRow label="市场规模" value={marketOpp.market_size || '-'} valueClass="text-white" />
            <DetailRow label="增长率" value={marketOpp.growth_rate || '-'} valueClass="text-yiwu-400" />
            <DetailRow label="竞争程度" value={marketOpp.competition_level || '-'} valueClass="text-white" />
            <DetailRow label="进入难度" value={marketOpp.entry_difficulty || '-'} valueClass="text-white" />
          </div>
        </DetailSection>
      )}

      {products.length > 0 && (
        <DetailSection title="推荐商品">
          <div className="space-y-2">
            {products.map((p, i) => (
              <div key={i} className="rounded bg-ocean-800/60 p-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-white font-medium">{p.product}</span>
                  <span className="text-yiwu-400">ROI {p.estimated_roi}</span>
                </div>
                <div className="text-xs text-gray-500 mt-0.5">建议起订量: {p.suggested_moq}件</div>
              </div>
            ))}
          </div>
        </DetailSection>
      )}
    </div>
  );
}

function SupplyChainDetail({ d }: { d: Record<string, unknown> }) {
  const supplyScore = d.supply_score as Record<string, unknown> | undefined;
  const suppliers = Array.isArray(d.suppliers) ? d.suppliers as { supplier: string; product?: string; moq?: number; unit_price?: string; delivery_days?: number; rating?: number; recommended?: boolean }[] : [];
  const logistics = d.logistics as Record<string, unknown> | undefined;
  const logisticsRoutes = logistics && Array.isArray(logistics.routes) ? logistics.routes as { name: string; days: number; frequency: string; cost_20ft?: string }[] : [];

  return (
    <div className="mt-2 rounded-lg bg-ocean-900/60 p-3 space-y-0">
      <DetailSection title="供应链评分">
        <div className="space-y-1">
          <DetailRow label="总分" value={supplyScore ? String(supplyScore.total) : '-'} valueClass="text-yiwu-400 font-medium" />
          <DetailRow label="等级" value={supplyScore ? String(supplyScore.level) : '-'} valueClass="text-white" />
          {supplyScore?.dimensions && (
            <div className="mt-1 space-y-0.5">
              {Object.entries(supplyScore.dimensions as Record<string, number>).map(([k, v]) => (
                <div key={k} className="flex items-center gap-2 text-xs">
                  <span className="text-gray-500 w-20 shrink-0">{k}:</span>
                  <div className="flex-1 h-1.5 bg-ocean-800 rounded-full overflow-hidden">
                    <div className="h-full bg-yiwu-500 rounded-full" style={{ width: `${Math.min(v, 100)}%` }} />
                  </div>
                  <span className="text-white w-6 text-right">{v}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </DetailSection>

      {suppliers.length > 0 && (
        <DetailSection title="供应商列表">
          <div className="space-y-1.5">
            {suppliers.map((s, i) => (
              <div key={i} className="rounded bg-ocean-800/60 p-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-white font-medium">{s.supplier}</span>
                  {s.recommended && <span className="text-yiwu-400 text-[10px]">推荐</span>}
                </div>
                <div className="flex flex-wrap gap-x-3 gap-y-0.5 mt-0.5 text-gray-400">
                  {s.unit_price && <span>价格: <span className="text-white">{s.unit_price}</span></span>}
                  {s.moq && <span>MOQ: <span className="text-white">{s.moq}件</span></span>}
                  {s.delivery_days && <span>交期: <span className="text-white">{s.delivery_days}天</span></span>}
                  {s.rating && <span>评分: <span className="text-yiwu-400">{s.rating}</span></span>}
                </div>
              </div>
            ))}
          </div>
        </DetailSection>
      )}

      {logistics && (
        <DetailSection title="物流方案（义新欧班列）">
          <div className="space-y-1">
            <DetailRow label="线路数" value={String(logistics.total_routes || '-')} valueClass="text-white" />
            <DetailRow label="覆盖国家" value={String(logistics.countries_covered || '-')} valueClass="text-white" />
            {logisticsRoutes.length > 0 && (
              <div className="mt-1 space-y-1">
                {logisticsRoutes.map((r, i) => (
                  <div key={i} className="rounded bg-ocean-800/60 p-1.5 text-xs flex items-center justify-between">
                    <span className="text-white">{r.name}</span>
                    <div className="flex gap-3 text-gray-400">
                      <span>{r.days}天</span>
                      <span>{r.frequency}</span>
                      {r.cost_20ft && <span className="text-yiwu-400">{r.cost_20ft}</span>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </DetailSection>
      )}
    </div>
  );
}

function ContentGenerationDetail({ d }: { d: Record<string, unknown> }) {
  const content = d.content as Record<string, unknown> | undefined;
  const marketing = d.marketing as Record<string, unknown> | undefined;
  const socialCopy = marketing?.social_copy as Record<string, unknown> | undefined;
  const platformCompliance = d.platform_compliance as Record<string, unknown> | undefined;

  return (
    <div className="mt-2 rounded-lg bg-ocean-900/60 p-3 space-y-0">
      <DetailSection title="内容概览">
        <div className="space-y-1">
          <DetailRow label="标题" value={content?.title ? String(content.title) : '-'} valueClass="text-white" />
          <DetailRow label="描述" value={content?.description ? String(content.description) : '-'} valueClass="text-gray-300" />
        </div>
      </DetailSection>

      {content?.seo_keywords && Array.isArray(content.seo_keywords) && (
        <DetailSection title="关键词">
          <div className="flex flex-wrap gap-1.5">
            {(content.seo_keywords as string[]).map((kw, i) => (
              <span key={i} className="rounded bg-ocean-800 px-2 py-0.5 text-[10px] text-yiwu-400">{kw}</span>
            ))}
          </div>
        </DetailSection>
      )}

      {socialCopy && (
        <DetailSection title="平台适配内容">
          <div className="space-y-1 text-xs">
            {socialCopy.hook && <DetailRow label="Hook" value={String(socialCopy.hook)} valueClass="text-white" />}
            {socialCopy.pain_point && <DetailRow label="痛点" value={String(socialCopy.pain_point)} valueClass="text-gray-300" />}
            {socialCopy.solution && <DetailRow label="方案" value={String(socialCopy.solution)} valueClass="text-gray-300" />}
            {socialCopy.cta && <DetailRow label="CTA" value={String(socialCopy.cta)} valueClass="text-yiwu-400" />}
            {socialCopy.hashtags && Array.isArray(socialCopy.hashtags) && (
              <div className="flex flex-wrap gap-1 mt-1">
                {(socialCopy.hashtags as string[]).map((tag, i) => (
                  <span key={i} className="text-gold-400 text-[10px]">{tag}</span>
                ))}
              </div>
            )}
          </div>
        </DetailSection>
      )}

      {platformCompliance?.warnings && Array.isArray(platformCompliance.warnings) && (
        <DetailSection title="平台合规提示">
          <div className="space-y-0.5">
            {(platformCompliance.warnings as string[]).map((w, i) => (
              <div key={i} className="text-xs text-gold-400 flex items-start gap-1">
                <span className="shrink-0 mt-0.5">!</span>
                <span>{w}</span>
              </div>
            ))}
          </div>
        </DetailSection>
      )}
    </div>
  );
}

function ComplianceDetail({ d }: { d: Record<string, unknown> }) {
  const certifications = Array.isArray(d.certifications) ? d.certifications as { name: string; required: boolean; estimated_time: string; estimated_cost: string }[] : [];
  const tariffBenefits = d.tariff_benefits as Record<string, unknown> | undefined;
  const trade1039 = d.trade_1039 as Record<string, unknown> | undefined;
  const rcepBenefits = d.rcep_benefits as Record<string, unknown> | undefined;

  return (
    <div className="mt-2 rounded-lg bg-ocean-900/60 p-3 space-y-0">
      <DetailSection title="目标国家">
        <DetailRow label="国家" value={String(d.target_country || '-')} valueClass="text-white font-medium" />
      </DetailSection>

      {certifications.length > 0 && (
        <DetailSection title="认证要求清单">
          <div className="space-y-1">
            {certifications.map((c, i) => (
              <div key={i} className="rounded bg-ocean-800/60 p-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-white font-medium">{c.name}</span>
                  <span className={c.required ? 'text-red-400' : 'text-gray-500'}>{c.required ? '必须' : '可选'}</span>
                </div>
                <div className="flex gap-3 mt-0.5 text-gray-400">
                  <span>耗时: <span className="text-white">{c.estimated_time}</span></span>
                  <span>费用: <span className="text-white">{c.estimated_cost}</span></span>
                </div>
              </div>
            ))}
          </div>
        </DetailSection>
      )}

      {d.tariff && (
        <DetailSection title="关税">
          <div className="space-y-1">
            <DetailRow label="总税费" value={String((d.tariff as Record<string, unknown>).total_tax || '-')} valueClass="text-gold-400" />
          </div>
        </DetailSection>
      )}

      {trade1039 && (
        <DetailSection title="1039模式建议">
          <div className="space-y-1 text-xs">
            <DetailRow label="适用" value={trade1039.applicable ? '是' : '否'} valueClass={trade1039.applicable ? 'text-yiwu-400' : 'text-gray-500'} />
            {trade1039.advantages && Array.isArray(trade1039.advantages) && (
              <div className="mt-1 space-y-0.5">
                {(trade1039.advantages as string[]).map((a, i) => (
                  <div key={i} className="text-gray-300 flex items-start gap-1">
                    <span className="text-yiwu-400 shrink-0">+</span>
                    <span>{a}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </DetailSection>
      )}

      {rcepBenefits && (
        <DetailSection title="RCEP优惠">
          <div className="text-xs text-gray-300">{String(rcepBenefits.description || 'RCEP协定下可享受关税优惠')}</div>
        </DetailSection>
      )}

      {tariffBenefits && (
        <DetailSection title="通关便利化">
          <div className="space-y-0.5 text-xs">
            <div className="text-gray-300">{String(tariffBenefits.description || '')}</div>
            {tariffBenefits.benefits && Array.isArray(tariffBenefits.benefits) && (
              <div className="space-y-0.5 mt-1">
                {(tariffBenefits.benefits as string[]).map((b, i) => (
                  <div key={i} className="text-gray-300 flex items-start gap-1">
                    <span className="text-yiwu-400 shrink-0">+</span>
                    <span>{b}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </DetailSection>
      )}
    </div>
  );
}

function CustomerServiceDetail({ d }: { d: Record<string, unknown> }) {
  const faqs = Array.isArray(d.faqs) ? d.faqs as { question: string; answer: string }[] : [];

  return (
    <div className="mt-2 rounded-lg bg-ocean-900/60 p-3 space-y-0">
      <DetailSection title="出海FAQ包">
        {faqs.length > 0 ? (
          <div className="space-y-2">
            {faqs.map((faq, i) => (
              <div key={i} className="rounded bg-ocean-800/60 p-2">
                <div className="text-xs text-white font-medium flex items-start gap-1.5">
                  <HelpCircle size={12} className="shrink-0 mt-0.5 text-yiwu-400" />
                  <span>{faq.question}</span>
                </div>
                <div className="text-xs text-gray-400 mt-1 pl-[18px]">{faq.answer}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-xs text-gray-500">暂无FAQ数据</div>
        )}
      </DetailSection>
    </div>
  );
}

function PolicyReplicationDetail({ d }: { d: Record<string, unknown> }) {
  const keyPoints = Array.isArray(d.key_points) ? d.key_points as { title: string; description: string; benefit_level: string }[] : [];
  const cases = Array.isArray(d.cases) ? d.cases as { title: string; category: string; target_market: string; annual_export: string }[] : [];
  const taxBenefits = d.tax_benefits as Record<string, unknown> | undefined;

  return (
    <div className="mt-2 rounded-lg bg-ocean-900/60 p-3 space-y-0">
      <DetailSection title="试点城市">
        <DetailRow label="试点城市数" value={String(d.total_cities || 39)} valueClass="text-yiwu-400 font-medium" />
      </DetailSection>

      {keyPoints.length > 0 && (
        <DetailSection title="政策要点">
          <div className="space-y-1">
            {keyPoints.map((p, i) => (
              <div key={i} className="rounded bg-ocean-800/60 p-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-white font-medium">{p.title}</span>
                  <span className={`text-[10px] ${p.benefit_level === '高' ? 'text-red-400' : p.benefit_level === '中' ? 'text-gold-400' : 'text-gray-500'}`}>{p.benefit_level}</span>
                </div>
                <div className="text-gray-400 mt-0.5">{p.description}</div>
              </div>
            ))}
          </div>
        </DetailSection>
      )}

      {taxBenefits && (
        <DetailSection title="红利计算">
          <div className="space-y-1 text-xs">
            <DetailRow label="增值税" value={taxBenefits.vat_exemption ? '免征' : '需缴纳'} valueClass={taxBenefits.vat_exemption ? 'text-yiwu-400' : 'text-gray-400'} />
            <DetailRow label="所得税" value={String(taxBenefits.income_tax || '-')} valueClass="text-white" />
            <DetailRow label="印花税" value={String(taxBenefits.stamp_duty || '-')} valueClass="text-white" />
          </div>
        </DetailSection>
      )}

      {cases.length > 0 && (
        <DetailSection title="成功案例">
          <div className="space-y-1.5">
            {cases.map((c, i) => (
              <div key={i} className="rounded bg-ocean-800/60 p-2 text-xs">
                <div className="text-white font-medium">{c.title}</div>
                <div className="flex gap-3 mt-0.5 text-gray-400">
                  <span>品类: <span className="text-white">{c.category}</span></span>
                  <span>市场: <span className="text-white">{c.target_market}</span></span>
                  <span>年出口: <span className="text-yiwu-400">{c.annual_export}</span></span>
                </div>
              </div>
            ))}
          </div>
        </DetailSection>
      )}
    </div>
  );
}
