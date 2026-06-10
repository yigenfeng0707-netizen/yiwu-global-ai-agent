"""义乌小商品出海智能体 - LLM服务"""

import os
import time
import httpx
from typing import Optional, Dict, Any


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
                    },
                )
                if response.status_code == 200:
                    self._increment_count()
                    data = response.json()
                    return data.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception:
            pass
        return None

    def chat_sync(self, messages: list, temperature: float = 0.7, max_tokens: int = 1000) -> Optional[str]:
        """同步聊天"""
        if not self.api_key:
            return None
        if not self._check_limit():
            return None

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
                    },
                )
                if response.status_code == 200:
                    self._increment_count()
                    data = response.json()
                    return data.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception:
            pass
        return None


# 全局LLM服务实例
llm_service = LLMService()
