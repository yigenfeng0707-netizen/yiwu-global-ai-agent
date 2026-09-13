"""义乌小商品出海智能体 - 智能客服Agent"""

import re
from typing import Any, Dict, List, Optional

from .base import BaseAgent
from ..data.market_data import CATEGORY_LIST
from ..data.customer_service_data import (
    FAQ_DATABASE,
    EMOTION_TYPES,
    DISPUTE_KEYWORDS,
    AUTO_REPLY_TEMPLATES,
)
from ..services.llm import llm_service
from ..services.rag import rag_service


class CustomerServiceAgent(BaseAgent):
    """智能客服Agent - 情绪识别、FAQ匹配、纠纷检测、RAG增强智能回复"""

    name = "customer_service"
    description = "智能客服Agent - 情绪识别、FAQ匹配、纠纷检测、RAG增强智能回复"

    LLM_SYSTEM_PROMPT = (
        "你是义乌小商品出海智能客服，专精1039市场采购贸易、义新欧班列、"
        "义乌国际商贸城、出口认证等领域的咨询。回答要专业、简洁、实用。"
        "如果提供了知识库资料，请优先依据资料回答；资料中没有的信息可以"
        "结合专业知识补充，但不得编造具体数字、电话、政策条款。"
    )

    # FAQ 直答阈值：bigram Dice 相似度，只有高度近似预设问题才直接给固定答案，
    # 避免旧版字符集相似度（阈值0.3）误命中、拦截 LLM/RAG 链路
    FAQ_DIRECT_THRESHOLD = 0.55

    def __init__(self):
        super().__init__()
        self.sessions: Dict[str, List[Dict]] = {}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        message = kwargs.get("message", "")
        category = kwargs.get("category", CATEGORY_LIST[0])
        language = kwargs.get("language", "zh")
        session_id = kwargs.get("session_id", "default")

        # 情绪检测
        emotion = self._detect_emotion(message)

        # FAQ匹配
        faq_match = self._match_faq(message, category, language)

        # 纠纷检测
        dispute = self._detect_dispute(message)

        # 生成回复
        reply = await self._generate_reply(
            message, category, language, faq_match, emotion, dispute, session_id
        )

        # 是否需要转人工
        needs_human = (
            dispute.get("detected", False) and emotion.get("type") == "negative"
        )

        # 记录会话到数据库
        try:
            self._db.save_chat_message(
                session_id=session_id,
                role="user",
                content=message,
                emotion=emotion.get("type", ""),
                category=category,
                language=language,
            )
            self._db.save_chat_message(
                session_id=session_id,
                role="bot",
                content=reply.get("text", ""),
                category=category,
                language=language,
            )
        except Exception:
            pass  # 数据库记录失败不影响主流程

        # 内存会话也保留（向后兼容）
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append({"role": "user", "text": message})
        self.sessions[session_id].append({"role": "bot", "text": reply.get("text", "")})

        return self._wrap_response(
            {
                "reply": reply,
                "emotion": emotion,
                "dispute": dispute,
                "faq_match": faq_match,
                "needs_human_escalation": needs_human,
                "session_id": session_id,
            }
        )

    async def get_faq(self, category: str, language: str = "zh") -> Dict[str, Any]:
        """获取FAQ列表"""
        faqs = FAQ_DATABASE.get(category, []) + FAQ_DATABASE.get("出海咨询", [])
        return {"faqs": faqs, "category": category}

    def _detect_emotion(self, message: str) -> Dict[str, Any]:
        """情绪检测"""
        negative_words = [
            "不满",
            "差评",
            "失望",
            "愤怒",
            "投诉",
            "退款",
            "赔偿",
            "差",
            "烂",
            "骗",
        ]
        positive_words = ["满意", "好", "棒", "赞", "感谢", "喜欢", "优秀"]

        msg_lower = message.lower()
        if any(w in msg_lower for w in negative_words):
            return {"type": "negative", "label": "消极", "color": "#ef4444"}
        elif any(w in msg_lower for w in positive_words):
            return {"type": "positive", "label": "积极", "color": "#00C9A7"}
        else:
            return {"type": "neutral", "label": "中性", "color": "#9ca3af"}

    def _match_faq(
        self, message: str, category: str, language: str
    ) -> Optional[Dict[str, Any]]:
        """FAQ匹配"""
        faqs = FAQ_DATABASE.get(category, []) + FAQ_DATABASE.get("出海咨询", [])
        best_match = None
        best_score = 0

        for faq in faqs:
            q = faq.get("q_zh" if language == "zh" else "q_en", "")
            score = self._calculate_similarity(message, q)
            if score > best_score and score >= self.FAQ_DIRECT_THRESHOLD:
                best_score = score
                best_match = faq

        return best_match

    @staticmethod
    def _bigrams(text: str) -> set:
        text = text.lower()
        grams = {text[i:i + 2] for i in range(len(text) - 1)}
        return grams or set(text)

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """字符 bigram Dice 相似度：比单字集合交并比更能区分语序与真实语义重合"""
        b1 = self._bigrams(text1)
        b2 = self._bigrams(text2)
        if not b1 or not b2:
            return 0.0
        return 2.0 * len(b1 & b2) / (len(b1) + len(b2))

    def _detect_dispute(self, message: str) -> Dict[str, Any]:
        """纠纷检测"""
        detected = any(kw in message for kw in DISPUTE_KEYWORDS)
        dispute_type = None
        if detected:
            if any(kw in message for kw in ["破损", "损坏", "质量"]):
                dispute_type = "质量问题"
            elif any(kw in message for kw in ["延误", "延迟", "未收到"]):
                dispute_type = "物流延误"
            elif any(kw in message for kw in ["认证", "清关", "被扣"]):
                dispute_type = "清关问题"
            else:
                dispute_type = "其他纠纷"

        return {"detected": detected, "type": dispute_type}

    async def _llm_chat(
        self,
        message: str,
        session_id: str = "default",
        contexts: Optional[List[Dict[str, Any]]] = None,
        language: str = "zh",
    ) -> Optional[str]:
        """调用LLM生成回复（RAG 上下文注入 + 超时保护）"""
        import asyncio

        system_prompt = self.LLM_SYSTEM_PROMPT
        if contexts:
            refs = "\n\n".join(
                f"[资料{i + 1}] {c['title']}\n{c['text'] if language == 'zh' else c['text_en']}"
                for i, c in enumerate(contexts)
            )
            system_prompt += f"\n\n以下是从知识库检索到的相关资料：\n{refs}"

        # 构建对话历史
        history = self.sessions.get(session_id, [])
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-10:]:  # 最近10轮对话
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["text"]})
        messages.append({"role": "user", "content": message})

        try:
            # 25s：兼容推理模型截断重试（最多两次 LLM 调用）
            # max_tokens=1600：推理模型思考占用预算，太小会截断空返回
            return await asyncio.wait_for(
                llm_service.chat(messages, temperature=0.7, max_tokens=1600),
                timeout=25.0,
            )
        except (asyncio.TimeoutError, Exception):
            return None

    async def _generate_reply(
        self,
        message: str,
        category: str,
        language: str,
        faq_match: Optional[Dict],
        emotion: Dict,
        dispute: Dict,
        session_id: str = "default",
    ) -> Dict[str, Any]:
        """生成回复（FAQ 直答 → RAG 检索增强 LLM → 知识库摘录 → 兜底模板）

        reply.source 标记回复来源，前端可据此展示"FAQ / 知识库 / AI"徽标：
        - faq：高置信命中预设 FAQ，直接返回标准答案
        - rag：LLM 基于知识库检索资料生成
        - llm：LLM 直接生成（知识库无命中）
        - kb：LLM 不可用，直接摘录知识库最相关资料
        - template：LLM 与知识库均不可用时的关键词模板
        - fallback：无任何可用信息
        """
        # 1) FAQ 高置信直答（阈值 0.55，仅近似预设问题时触发）
        if faq_match:
            answer_key = "a_zh" if language == "zh" else "a_en"
            question_key = "q_zh" if language == "zh" else "q_en"
            return {
                "text": faq_match.get(answer_key, ""),
                "source": "faq",
                "references": [faq_match.get(question_key, "")],
            }

        # 2) RAG 检索（LLM 可用与否都先检索，作为生成上下文或降级答案）
        contexts = await rag_service.retrieve(message, top_k=3, language=language)
        references = [c["title"] for c in contexts]

        # 3) 纠纷处理：先用模板安抚，再调用 LLM（带知识库上下文）给出详细建议
        if dispute.get("detected"):
            template_reply = AUTO_REPLY_TEMPLATES["dispute_detected"]
            llm_reply = await self._llm_chat(
                f"用户遇到纠纷：{message}，纠纷类型：{dispute.get('type', '未知')}。请给出详细的处理建议。",
                session_id,
                contexts=contexts,
                language=language,
            )
            if llm_reply:
                return {
                    "text": f"{template_reply}\n\n📋 详细建议：\n{llm_reply}",
                    "source": "rag" if contexts else "llm",
                    "references": references,
                }
            return {"text": template_reply, "source": "template", "references": references}

        # 4) 常规问题：RAG 检索增强 LLM 生成
        llm_reply = await self._llm_chat(message, session_id, contexts=contexts, language=language)
        if llm_reply:
            return {
                "text": llm_reply,
                "source": "rag" if contexts else "llm",
                "references": references,
            }

        # 5) LLM 不可用但知识库有命中：摘录最相关资料，明确标注来源，不冒充智能回答
        if contexts:
            top = contexts[0]
            top_text = top["text"] if language == "zh" else top["text_en"]
            note = "（当前智能生成服务暂不可用，以下为知识库中最相关的资料摘录）" if language == "zh" \
                else "(AI generation is temporarily unavailable; below is the most relevant knowledge base entry)"
            return {
                "text": f"{note}\n\n【{top['title']}】\n{top_text}",
                "source": "kb",
                "references": references,
            }

        # 6) 关键词模板兜底
        if any(kw in message for kw in ["物流", "运输", "发货", "班列", "快递"]):
            return {"text": AUTO_REPLY_TEMPLATES["logistics_inquiry"], "source": "template", "references": []}

        if any(kw in message for kw in ["认证", "CE", "EAC", "SABER", "检测"]):
            return {"text": AUTO_REPLY_TEMPLATES["certification_inquiry"], "source": "template", "references": []}

        return {"text": AUTO_REPLY_TEMPLATES["unknown"], "source": "fallback", "references": []}
