import { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, Loader2, Copy, Check, Sparkles, Hash, Megaphone, FileText, RefreshCw } from 'lucide-react';
import { categories } from '@/store/useStore';
import { generateContent, type ContentGenerationData } from '@/utils/api';

const platforms = [
  { value: 'amazon', label: 'Amazon' },
  { value: 'alibaba', label: 'Alibaba.com' },
  { value: 'tiktok', label: 'TikTok Shop' },
  { value: 'temu', label: 'Temu' },
];

const languages = [
  { value: 'en', label: '英语' },
  { value: 'de', label: '德语' },
  { value: 'fr', label: '法语' },
  { value: 'es', label: '西班牙语' },
  { value: 'ar', label: '阿拉伯语' },
  { value: 'ru', label: '俄语' },
  { value: 'kk', label: '哈萨克语' },
  { value: 'ja', label: '日语' },
];

function CopyBtn({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  return (
    <button onClick={handleCopy} className="rounded p-1 text-gray-500 hover:text-yiwu-400 transition-colors">
      {copied ? <Check size={14} className="text-yiwu-400" /> : <Copy size={14} />}
    </button>
  );
}

export default function ContentGeneration() {
  const [productName, setProductName] = useState('厨房收纳架');
  const [category, setCategory] = useState('日用百货');
  const [platform, setPlatform] = useState('amazon');
  const [targetLang, setTargetLang] = useState('en');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<ContentGenerationData | null>(null);
  const [error, setError] = useState('');

  const handleGenerate = async () => {
    if (!productName.trim()) return;
    setLoading(true);
    setError('');
    try {
      const result = await generateContent({
        product_name: productName,
        category,
        platform,
        target_language: targetLang,
      });
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : '生成失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      {/* 输入区域 */}
      <div className="glass-light rounded-xl p-6 space-y-4">
        <h3 className="text-sm font-medium text-white flex items-center gap-2">
          <Sparkles size={16} className="text-gold-400" /> 内容生成
        </h3>
        <input
          value={productName} onChange={(e) => setProductName(e.target.value)}
          placeholder="请输入产品名称"
          className="w-full rounded-lg bg-ocean-800 px-4 py-2.5 text-sm text-white placeholder-gray-500 border border-white/10 focus:border-yiwu-500 focus:outline-none"
        />
        <div className="flex flex-wrap gap-4">
          <div className="relative">
            <select value={category} onChange={(e) => setCategory(e.target.value)}
              className="appearance-none rounded-lg bg-ocean-800 px-4 py-2 pr-10 text-sm text-white border border-white/10 focus:border-yiwu-500 focus:outline-none">
              {categories.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
            <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          </div>
          <div className="relative">
            <select value={platform} onChange={(e) => setPlatform(e.target.value)}
              className="appearance-none rounded-lg bg-ocean-800 px-4 py-2 pr-10 text-sm text-white border border-white/10 focus:border-yiwu-500 focus:outline-none">
              {platforms.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
            </select>
            <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          </div>
          <div className="relative">
            <select value={targetLang} onChange={(e) => setTargetLang(e.target.value)}
              className="appearance-none rounded-lg bg-ocean-800 px-4 py-2 pr-10 text-sm text-white border border-white/10 focus:border-yiwu-500 focus:outline-none">
              {languages.map((l) => <option key={l.value} value={l.value}>{l.label}</option>)}
            </select>
            <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          </div>
        </div>
        <button onClick={handleGenerate} disabled={loading || !productName.trim()}
          className="rounded-lg bg-yiwu-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-yiwu-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2">
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
          {loading ? '生成中...' : '生成内容'}
        </button>
      </div>

      {error && (
        <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-4 flex items-center justify-between">
          <span className="text-sm text-red-400">{error}</span>
          <button onClick={handleGenerate} disabled={loading}
            className="rounded-lg bg-red-500/20 px-3 py-1.5 text-xs text-red-400 hover:bg-red-500/30 transition-colors flex items-center gap-1">
            <RefreshCw size={12} /> 重试
          </button>
        </div>
      )}

      {loading && (
        <div className="flex h-48 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-yiwu-500" />
          <span className="ml-3 text-gray-400">AI 正在生成内容...</span>
        </div>
      )}

      {data && !loading && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          {/* 产品标题 */}
          <div className="glass-light rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-white flex items-center gap-2"><FileText size={14} className="text-yiwu-400" /> 产品标题</h4>
              <CopyBtn text={data.content.title} />
            </div>
            <p className="text-sm text-gray-300">{data.content.title}</p>
          </div>

          {/* 产品描述 */}
          <div className="glass-light rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-white flex items-center gap-2"><FileText size={14} className="text-yiwu-400" /> 产品描述</h4>
              <CopyBtn text={data.content.description} />
            </div>
            <p className="text-sm text-gray-300 whitespace-pre-wrap">{data.content.description}</p>
          </div>

          {/* 卖点 */}
          <div className="glass-light rounded-xl p-6">
            <h4 className="text-sm font-medium text-white mb-3">核心卖点</h4>
            <div className="space-y-2">
              {data.content.highlights.map((h, i) => (
                <div key={i} className="flex items-center gap-2 rounded-lg bg-ocean-800/50 p-3">
                  <span className="text-sm">{h.icon}</span>
                  <span className="text-sm text-gray-300">{h.text}</span>
                </div>
              ))}
            </div>
          </div>

          {/* SEO 关键词 */}
          <div className="glass-light rounded-xl p-6">
            <h4 className="text-sm font-medium text-white mb-3 flex items-center gap-2"><Hash size={14} className="text-gold-400" /> SEO 关键词</h4>
            <div className="flex flex-wrap gap-2">
              {data.content.seo_keywords.map((kw, i) => (
                <span key={i} className="rounded-full bg-gold-500/10 px-3 py-1 text-xs text-gold-400">{kw}</span>
              ))}
            </div>
          </div>

          {/* 社媒文案 & 广告文案 */}
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="glass-light rounded-xl p-6">
              <h4 className="text-sm font-medium text-white mb-3 flex items-center gap-2"><Megaphone size={14} className="text-yiwu-400" /> 社媒文案</h4>
              <div className="space-y-2 text-sm">
                <p className="text-gray-400">钩子: <span className="text-gray-300">{data.marketing.social_copy.hook}</span></p>
                <p className="text-gray-400">痛点: <span className="text-gray-300">{data.marketing.social_copy.pain_point}</span></p>
                <p className="text-gray-400">方案: <span className="text-gray-300">{data.marketing.social_copy.solution}</span></p>
                <p className="text-gray-400">行动: <span className="text-gray-300">{data.marketing.social_copy.cta}</span></p>
                <div className="flex flex-wrap gap-1 pt-1">
                  {data.marketing.social_copy.hashtags.map((tag, i) => (
                    <span key={i} className="text-xs text-yiwu-400">{tag}</span>
                  ))}
                </div>
              </div>
            </div>
            <div className="glass-light rounded-xl p-6">
              <h4 className="text-sm font-medium text-white mb-3 flex items-center gap-2"><Megaphone size={14} className="text-gold-400" /> 广告文案</h4>
              <div className="space-y-2 text-sm">
                <p className="text-gray-400">标题: <span className="text-white font-medium">{data.marketing.ad_copy.headline}</span></p>
                <p className="text-gray-400">正文: <span className="text-gray-300">{data.marketing.ad_copy.body}</span></p>
                <p className="text-gray-400">按钮: <span className="rounded bg-gold-500/20 px-2 py-0.5 text-gold-400">{data.marketing.ad_copy.cta_button}</span></p>
              </div>
            </div>
          </div>

          {/* 合规提示 */}
          {data.platform_compliance.warnings.length > 0 && (
            <div className="rounded-lg border border-gold-500/20 bg-gold-500/5 p-4">
              <p className="text-xs text-gold-400 mb-1">平台合规提示</p>
              {data.platform_compliance.warnings.map((w, i) => (
                <p key={i} className="text-xs text-gray-400">• {w}</p>
              ))}
            </div>
          )}
        </motion.div>
      )}
    </motion.div>
  );
}
