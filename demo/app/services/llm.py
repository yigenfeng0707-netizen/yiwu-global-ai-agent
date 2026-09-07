"""义乌小商品出海智能体 - LLM服务"""

import json
import logging
import os
import time
import httpx
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def _parse_request_extras(raw: str) -> Dict[str, Any]:
    """解析 LLM_REQUEST_EXTRAS（JSON），用于注入网关特有请求参数（如 reasoning_effort）"""
    if not raw:
        return {}
    try:
        extras = json.loads(raw)
        return extras if isinstance(extras, dict) else {}
    except Exception:
        logger.warning("LLM_REQUEST_EXTRAS 解析失败: %s", raw[:100])
        return {}


class LLMService:
    """LLM服务 - 阿里云百炼DashScope API（OpenAI兼容模式）"""

    def __init__(self):
        self.base_url = os.getenv(
            "LLM_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "qwen-plus")
        self.daily_limit = int(os.getenv("LLM_DAILY_LIMIT", "500"))
        self.workspace_id = os.getenv("DASHSCOPE_WORKSPACE_ID", "")
        self.request_extras = _parse_request_extras(os.getenv("LLM_REQUEST_EXTRAS", ""))
        self._daily_count = 0
        self._daily_reset = time.time()

    def _get_headers(self) -> dict:
        """构建请求头，含DashScope工作空间"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.workspace_id:
            headers["X-DashScope-WorkSpace"] = self.workspace_id
        return headers

    def _check_limit(self) -> bool:
        """检查每日调用限制"""
        now = time.time()
        if now - self._daily_reset > 86400:
            self._daily_count = 0
            self._daily_reset = now
        if self.daily_limit > 0 and self._daily_count >= self.daily_limit:
            return False
        return True

    def _increment_count(self):
        """增加调用计数"""
        self._daily_count += 1

    @property
    def daily_usage(self) -> Dict[str, int]:
        """获取每日使用量"""
        return {"used": self._daily_count, "limit": self.daily_limit}

    async def chat(self, messages: list, temperature: float = 0.7, max_tokens: int = 1000) -> Optional[str]:
        """异步聊天"""
        if not self.api_key:
            return None
        if not self._check_limit():
            return None

        # 推理模型自愈：思考过程可能耗尽小 max_tokens 预算导致 content 为空，
        # 遇 finish_reason=length 且空内容时放大 token 上限重试一次
        for attempt, tokens in enumerate((max_tokens, max(max_tokens, 1600))):
            content, finish_reason = await self._request(messages, temperature, tokens)
            if content:
                self._increment_count()
                return content
            if finish_reason == "length" and attempt == 0:
                logger.warning("LLM content为空且被截断(max_tokens=%d)，放大重试", tokens)
                continue
            if content is None:
                return None  # 请求失败已记录日志
            logger.warning("LLM返回空content: finish_reason=%s", finish_reason)
            return None
        return None

    async def _request(self, messages: list, temperature: float,
                       max_tokens: int) -> tuple:
        """发赢单次请求，返回 (content, finish_reason)；请求失败返回 (None, None)"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        **self.request_extras,
                    },
                )
                if response.status_code != 200:
                    logger.warning("LLM HTTP %d: %s", response.status_code, response.text[:200])
                    return None, None
                data = response.json()
                choice = (data.get("choices") or [{}])[0]
                message = choice.get("message") or {}
                content = message.get("content") or ""
                finish = choice.get("finish_reason")
                # 非截断的空content：回退 reasoning_content（部分推理模型把答案放思考字段）
                # 截断（length）时不回退——思考文本不完整，交给上层放大重试
                if not content.strip() and finish != "length":
                    content = message.get("reasoning_content") or ""
                return (content.strip() or ""), finish
        except Exception as e:
            logger.warning("LLM调用异常: %s", e)
            return None, None

    def chat_sync(self, messages: list, temperature: float = 0.7, max_tokens: int = 1000) -> Optional[str]:
        """同步聊天"""
        if not self.api_key:
            return None
        if not self._check_limit():
            return None

        for attempt, tokens in enumerate((max_tokens, max(max_tokens, 1600))):
            content, finish_reason = self._request_sync(messages, temperature, tokens)
            if content:
                self._increment_count()
                return content
            if finish_reason == "length" and attempt == 0:
                logger.warning("LLM content为空且被截断(max_tokens=%d)，放大重试", tokens)
                continue
            if content is None:
                return None
            logger.warning("LLM返回空content: finish_reason=%s", finish_reason)
            return None
        return None

    def _request_sync(self, messages: list, temperature: float,
                      max_tokens: int) -> tuple:
        """同步单次请求，返回 (content, finish_reason)；请求失败返回 (None, None)"""
        try:
            with httpx.Client(timeout=30) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        **self.request_extras,
                    },
                )
                if response.status_code != 200:
                    logger.warning("LLM HTTP %d: %s", response.status_code, response.text[:200])
                    return None, None
                data = response.json()
                choice = (data.get("choices") or [{}])[0]
                message = choice.get("message") or {}
                content = message.get("content") or ""
                finish = choice.get("finish_reason")
                if not content.strip() and finish != "length":
                    content = message.get("reasoning_content") or ""
                return (content.strip() or ""), finish
        except Exception as e:
            logger.warning("LLM调用异常: %s", e)
            return None, None


# 全局LLM服务实例
llm_service = LLMService()
