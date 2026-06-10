"""义乌小商品出海智能体 - 智能客服Agent"""

import random
import re
from typing import Any, Dict, List, Optional

from .base import BaseAgent
from ..data.market_data import CATEGORY_LIST
from ..data.customer_service_data import (
    FAQ_DATABASE, EMOTION_TYPES, DISPUTE_KEYWORDS, AUTO_REPLY_TEMPLATES,
)


class CustomerServiceAgent(BaseAgent):
    """智能客服Agent - 情绪识别、FAQ匹配、纠纷检测、智能回复"""

    name = "customer_service"
    description = "智能客服Agent - 情绪识别、FAQ匹配、纠纷检测、智能回复"

    def __init__(self):
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
        reply = self._generate_reply(message, category, language, faq_match, emotion, dispute)

        # 是否需要转人工
        needs_human = dispute.get("detected", False) and emotion.get("type") == "negative"

        # 记录会话
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append({"role": "user", "text": message})
        self.sessions[session_id].append({"role": "bot", "text": reply.get("text", "")})

        return self._wrap_response({
            "reply": reply,
            "emotion": emotion,
            "dispute": dispute,
            "faq_match": faq_match,
            "needs_human_escalation": needs_human,
            "session_id": session_id,
        })

    async def get_faq(self, category: str, language: str = "zh") -> Dict[str, Any]:
        """获取FAQ列表"""
        faqs = FAQ_DATABASE.get(category, []) + FAQ_DATABASE.get("出海咨询", [])
        return {"faqs": faqs, "category": category}

    def _detect_emotion(self, message: str) -> Dict[str, Any]:
        """情绪检测"""
        negative_words = ["不满", "差评", "失望", "愤怒", "投诉", "退款", "赔偿", "差", "烂", "骗"]
        positive_words = ["满意", "好", "棒", "赞", "感谢", "喜欢", "优秀"]

        msg_lower = message.lower()
        if any(w in msg_lower for w in negative_words):
            return {"type": "negative", "label": "消极", "color": "#ef4444"}
        elif any(w in msg_lower for w in positive_words):
            return {"type": "positive", "label": "积极", "color": "#00C9A7"}
        else:
            return {"type": "neutral", "label": "中性", "color": "#9ca3af"}

    def _match_faq(self, message: str, category: str, language: str) -> Optional[Dict[str, Any]]:
        """FAQ匹配"""
        faqs = FAQ_DATABASE.get(category, []) + FAQ_DATABASE.get("出海咨询", [])
        best_match = None
        best_score = 0

        for faq in faqs:
            q = faq.get("q_zh" if language == "zh" else "q_en", "")
            score = self._calculate_similarity(message, q)
            if score > best_score and score > 0.3:
                best_score = score
                best_match = faq

        return best_match

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """简单相似度计算"""
        words1 = set(text1)
        words2 = set(text2)
        if not words1 or not words2:
            return 0
        intersection = words1 & words2
        return len(intersection) / max(len(words1), len(words2))

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

    def _generate_reply(self, message: str, category: str, language: str,
                        faq_match: Optional[Dict], emotion: Dict, dispute: Dict) -> Dict[str, Any]:
        """生成回复"""
        # 纠纷优先处理
        if dispute.get("detected"):
            return {"text": AUTO_REPLY_TEMPLATES["dispute_detected"]}

        # FAQ匹配回复
        if faq_match:
            answer_key = "a_zh" if language == "zh" else "a_en"
            return {"text": faq_match.get(answer_key, "")}

        # 物流相关
        if any(kw in message for kw in ["物流", "运输", "发货", "班列", "快递"]):
            return {"text": AUTO_REPLY_TEMPLATES["logistics_inquiry"]}

        # 认证相关
        if any(kw in message for kw in ["认证", "CE", "EAC", "SABER", "检测"]):
            return {"text": AUTO_REPLY_TEMPLATES["certification_inquiry"]}

        # 默认回复
        return {"text": AUTO_REPLY_TEMPLATES["unknown"]}
