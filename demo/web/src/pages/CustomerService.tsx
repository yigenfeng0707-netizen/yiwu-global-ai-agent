import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, Send, Loader2, MessageCircle, AlertTriangle, HelpCircle } from 'lucide-react';
import { categories } from '@/store/useStore';
import { sendChatMessage, fetchFAQ } from '@/utils/api';

const langOptions = [
  { value: 'zh', label: '中文' },
  { value: 'en', label: 'English' },
];

interface ChatMessage {
  role: 'user' | 'bot';
  text: string;
  emotion?: { type: string; label: string; color: string };
  dispute?: boolean;
}

interface FAQItem { question: string; answer: string; }

export default function CustomerService() {
  const [category, setCategory] = useState(categories[0]);
  const [language, setLanguage] = useState('zh');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [faqs, setFaqs] = useState<FAQItem[]>([]);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [sending, setSending] = useState(false);
  const [disputeAlert, setDisputeAlert] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchFAQ(category, language)
      .then((data) => {
        const mapped = (data.faqs || []).map((f) => ({
          question: language === 'zh' ? f.q_zh : f.q_en,
          answer: language === 'zh' ? f.a_zh : f.a_en,
        }));
        setFaqs(mapped);
      })
      .catch(() => setFaqs([]));
  }, [category, language]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (text?: string) => {
    const msg = text || input.trim();
    if (!msg || sending) return;
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', text: msg }]);
    setSending(true);
    try {
      const d = await sendChatMessage({ message: msg, category, language, session_id: sessionId });
      setMessages((prev) => [...prev, {
        role: 'bot',
        text: d.reply?.text || '',
        emotion: d.emotion ? { type: d.emotion.type, label: d.emotion.label, color: d.emotion.color } : undefined,
        dispute: d.dispute?.detected || false,
      }]);
      if (d.dispute?.detected) setDisputeAlert(true);
      if (d.needs_human_escalation) {
        setMessages((prev) => [...prev, { role: 'bot', text: '⚠️ 已为您转接人工客服，请稍候...' }]);
      }
    } catch {
      setMessages((prev) => [...prev, { role: 'bot', text: '抱歉，服务暂时不可用，请稍后重试。' }]);
    } finally {
      setSending(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-6 h-[calc(100vh-8rem)]">
      {/* 主聊天区 */}
      <div className="flex flex-1 flex-col glass-light rounded-xl overflow-hidden">
        {/* 顶部栏 */}
        <div className="flex items-center gap-4 border-b border-white/5 px-4 py-3">
          <MessageCircle size={16} className="text-yiwu-400" />
          <div className="relative">
            <select value={category} onChange={(e) => setCategory(e.target.value)}
              className="appearance-none rounded-lg bg-ocean-800 px-3 py-1.5 pr-8 text-xs text-white border border-white/10 focus:border-yiwu-500 focus:outline-none">
              {categories.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
            <ChevronDown className="pointer-events-none absolute right-2 top-1/2 h-3 w-3 -translate-y-1/2 text-gray-400" />
          </div>
          <div className="relative">
            <select value={language} onChange={(e) => setLanguage(e.target.value)}
              className="appearance-none rounded-lg bg-ocean-800 px-3 py-1.5 pr-8 text-xs text-white border border-white/10 focus:border-yiwu-500 focus:outline-none">
              {langOptions.map((l) => <option key={l.value} value={l.value}>{l.label}</option>)}
            </select>
            <ChevronDown className="pointer-events-none absolute right-2 top-1/2 h-3 w-3 -translate-y-1/2 text-gray-400" />
          </div>
        </div>

        {/* 纠纷预警 */}
        {disputeAlert && (
          <div className="flex items-center gap-2 bg-red-500/10 border-b border-red-500/20 px-4 py-2">
            <AlertTriangle size={14} className="text-red-400" />
            <span className="text-xs text-red-400">检测到纠纷风险，已触发预警机制</span>
            <button onClick={() => setDisputeAlert(false)} className="ml-auto text-xs text-gray-500 hover:text-gray-300">关闭</button>
          </div>
        )}

        {/* 消息列表 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="flex h-full items-center justify-center text-gray-500 text-sm">
              请输入您的问题，AI 客服将为您解答
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[75%] rounded-xl px-4 py-2.5 ${
                msg.role === 'user' ? 'bg-yiwu-600/80 text-white' : 'bg-ocean-800/80 text-gray-300'
              }`}>
                <div className="flex items-center gap-2 mb-1">
                  {msg.emotion && (
                    <span className="h-2 w-2 rounded-full shrink-0" style={{ backgroundColor: msg.emotion.color }} title={msg.emotion.label} />
                  )}
                  {msg.dispute && <AlertTriangle size={12} className="text-red-400" />}
                  <span className="text-xs text-gray-500">{msg.role === 'user' ? '我' : 'AI 客服'}</span>
                </div>
                <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
              </div>
            </div>
          ))}
          {sending && (
            <div className="flex justify-start">
              <div className="rounded-xl bg-ocean-800/80 px-4 py-2.5 text-gray-400 text-sm flex items-center gap-2">
                <Loader2 size={14} className="animate-spin" /> 思考中...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 输入框 */}
        <div className="border-t border-white/5 px-4 py-3 flex gap-2">
          <input value={input} onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
            placeholder="输入您的问题..."
            className="flex-1 rounded-lg bg-ocean-800 px-4 py-2 text-sm text-white placeholder-gray-500 border border-white/10 focus:border-yiwu-500 focus:outline-none" />
          <button onClick={() => handleSend()} disabled={sending || !input.trim()}
            className="rounded-lg bg-yiwu-600 px-4 py-2 text-sm text-white hover:bg-yiwu-500 disabled:opacity-50 transition-colors">
            <Send size={16} />
          </button>
        </div>
      </div>

      {/* FAQ 侧栏 */}
      <div className="hidden lg:flex w-72 flex-col glass-light rounded-xl overflow-hidden">
        <div className="px-4 py-3 border-b border-white/5 flex items-center gap-2">
          <HelpCircle size={14} className="text-gold-400" />
          <span className="text-sm font-medium text-white">常见问题</span>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {faqs.length === 0 && <p className="text-xs text-gray-500 text-center py-8">暂无常见问题</p>}
          {faqs.map((faq, i) => (
            <button key={i} onClick={() => handleSend(faq.question)}
              className="w-full text-left rounded-lg bg-ocean-800/50 p-3 hover:bg-ocean-800 transition-colors">
              <p className="text-xs text-gray-300 line-clamp-2">{faq.question}</p>
              <p className="text-xs text-gray-500 mt-1 line-clamp-1">{faq.answer}</p>
            </button>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
