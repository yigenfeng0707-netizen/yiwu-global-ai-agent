import { useState, useEffect, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, Send, Loader2, MessageCircle, AlertTriangle, HelpCircle, Trash2 } from 'lucide-react';
import { categories } from '@/store/useStore';
import { sendChatMessage, fetchFAQ } from '@/utils/api';

const langOptions = [
  { value: 'zh', label: '中文' },
  { value: 'en', label: 'English' },
];

const WELCOME_MESSAGE: ChatMessage = {
  role: 'bot',
  text: '您好！我是义乌小商品出海智能客服，可以帮您解答1039市场采购贸易、义新欧班列、出口认证等问题。请问有什么可以帮助您的？',
  emotion: { type: 'positive', label: '积极', color: '#00C9A7' },
};

const SUGGESTED_QUESTIONS = [
  '什么是1039市场采购贸易？',
  '义新欧班列有哪些路线？',
  '出口欧洲需要什么认证？',
  '如何开始义乌小商品跨境出口？',
];

interface ChatMessage {
  role: 'user' | 'bot';
  text: string;
  emotion?: { type: string; label: string; color: string };
  dispute?: boolean;
}

interface FAQItem { question: string; answer: string; }

function loadMessages(sessionId: string): ChatMessage[] {
  try {
    const raw = localStorage.getItem(`cs_session_${sessionId}`);
    if (raw) return JSON.parse(raw);
  } catch { /* ignore */ }
  return [];
}

function saveMessages(sessionId: string, msgs: ChatMessage[]) {
  try {
    localStorage.setItem(`cs_session_${sessionId}`, JSON.stringify(msgs));
  } catch { /* ignore */ }
}

export default function CustomerService() {
  const [category, setCategory] = useState(categories[0]);
  const [language, setLanguage] = useState('zh');
  const [input, setInput] = useState('');
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    const saved = loadMessages(sessionId);
    return saved.length > 0 ? saved : [WELCOME_MESSAGE];
  });
  const [faqs, setFaqs] = useState<FAQItem[]>([]);
  const [sending, setSending] = useState(false);
  const [disputeAlert, setDisputeAlert] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 持久化：消息变化时保存到localStorage
  useEffect(() => {
    saveMessages(sessionId, messages);
  }, [messages, sessionId]);

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

  const handleSend = useCallback(async (text?: string) => {
    const msg = text || input.trim();
    if (!msg || sending) return;
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', text: msg }]);
    setSending(true);
    try {
      const d = await sendChatMessage({ message: msg, category, language, session_id: sessionId });
      const replyText = d?.reply?.text || '';
      const finalText = replyText || `关于"${msg}"的问题，根据义乌小商品出海经验：\n\n1. 1039市场采购贸易模式可免征增值税\n2. 义新欧班列14-21天直达欧洲\n3. 建议通过义乌国际商贸城7.5万商户进行采购\n\n如需更详细的信息，请告诉我具体的品类和目标市场。`;
      setMessages((prev) => [...prev, {
        role: 'bot',
        text: finalText,
        emotion: d?.emotion ? { type: d.emotion.type || 'neutral', label: d.emotion.label || '中性', color: d.emotion.color || '#9ca3af' } : { type: 'neutral', label: '中性', color: '#9ca3af' },
        dispute: d?.dispute?.detected || false,
      }]);
      if (d?.dispute?.detected) setDisputeAlert(true);
      if (d?.needs_human_escalation) {
        setMessages((prev) => [...prev, { role: 'bot', text: '⚠️ 已为您转接人工客服，请稍候...' }]);
      }
    } catch {
      setMessages((prev) => [...prev, {
        role: 'bot',
        text: `关于"${msg}"的问题，根据义乌小商品出海经验：\n\n1. 1039市场采购贸易模式可免征增值税\n2. 义新欧班列14-21天直达欧洲\n3. 建议通过义乌国际商贸城7.5万商户进行采购\n\n如需更详细的信息，请告诉我具体的品类和目标市场。`,
        emotion: { type: 'neutral', label: '中性', color: '#9ca3af' },
      }]);
    } finally {
      setSending(false);
    }
  }, [input, sending, category, language, sessionId]);

  const handleClear = () => {
    setMessages([WELCOME_MESSAGE]);
    setDisputeAlert(false);
  };

  // 是否只有欢迎消息（即用户尚未开始对话）
  const isEmptyChat = messages.length <= 1 && messages[0]?.role === 'bot';

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
          <button onClick={handleClear}
            className="ml-auto flex items-center gap-1 rounded-lg bg-ocean-800 px-3 py-1.5 text-xs text-gray-400 hover:text-gray-200 border border-white/10 hover:border-white/20 transition-colors"
            title="清空对话">
            <Trash2 size={12} />
            <span>清空</span>
          </button>
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
          {/* 推荐问题按钮（仅在欢迎消息后显示） */}
          {isEmptyChat && (
            <div className="flex flex-wrap gap-2 justify-center pt-2">
              {SUGGESTED_QUESTIONS.map((q, i) => (
                <button key={i} onClick={() => handleSend(q)}
                  className="rounded-full bg-yiwu-600/20 border border-yiwu-500/30 px-3 py-1.5 text-xs text-yiwu-300 hover:bg-yiwu-600/40 transition-colors">
                  {q}
                </button>
              ))}
            </div>
          )}
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
