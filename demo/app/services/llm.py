"""义乌小商品出海智能体 - LLM服务"""

import json
import logging
import os
import time
from datetime import date
from pathlib import Path
import httpx
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def _daily_count_path() -> Path:
    """日计数状态文件：与数据库同目录（生产环境随 DATABASE_PATH 落持久卷，重启不清零）"""
    db_path = os.getenv("DATABASE_PATH", "")
    base = Path(db_path).parent if db_path else Path(__file__).resolve().parent.parent.parent / "data"
    return base / "llm_daily_count.json"


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


def _parse_fallback() -> Dict[str, Any]:
    """解析备选模型配置：LLM_FALLBACK_API_KEY 存在且 base_url/model 齐全时启用"""
    api_key = os.getenv("LLM_FALLBACK_API_KEY", "")
    base_url = os.getenv("LLM_FALLBACK_BASE_URL", "")
    model = os.getenv("LLM_FALLBACK_MODEL", "")
    if not (api_key and base_url and model):
        return {}
    return {
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
        "request_extras": _parse_request_extras(os.getenv("LLM_FALLBACK_REQUEST_EXTRAS", "")),
    }


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
        self.fallback = _parse_fallback()
        # 备选模型半开熔断：连续失败3次后冷却10分钟，避免每个请求都等备网关超时
        self._fallback_failures = 0
        self._fallback_cooldown_until = 0.0
        self._daily_count = 0
        self._daily_reset = time.time()
        self._count_file = _daily_count_path()
        self._restore_daily_count()

    def _restore_daily_count(self):
        """从磁盘恢复当日计数（容器重启不清零）"""
        try:
            state = json.loads(self._count_file.read_text(encoding="utf-8"))
            if state.get("date") == date.today().isoformat():
                self._daily_count = int(state.get("count", 0))
                if self._daily_count:
                    logger.info("恢复当日LLM计数: %d", self._daily_count)
        except FileNotFoundError:
            pass
        except Exception as e:
            logger.warning("读取LLM日计数失败: %s", e)

    def _get_headers(self, api_key: str = None) -> dict:
        """构建请求头，含DashScope工作空间"""
        headers = {
            "Authorization": f"Bearer {api_key or self.api_key}",
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
        """增加调用计数并落盘"""
        self._daily_count += 1
        try:
            self._count_file.parent.mkdir(parents=True, exist_ok=True)
            self._count_file.write_text(
                json.dumps({"date": date.today().isoformat(), "count": self._daily_count}),
                encoding="utf-8",
            )
        except Exception as e:
            logger.warning("写入LLM日计数失败: %s", e)

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
                break  # 请求失败，转备选模型
            logger.warning("LLM返回空content: finish_reason=%s", finish_reason)
            break
        return await self._chat_fallback(messages, temperature, max_tokens)

    async def _chat_fallback(self, messages: list, temperature: float, max_tokens: int) -> Optional[str]:
        """主模型失败后切备选模型（未配置或熔断冷却中则直接返回 None）"""
        fb = self.fallback
        if not fb or time.time() < self._fallback_cooldown_until:
            return None
        logger.warning("主模型失败，切换备选模型 %s", fb["model"])
        content = None
        for attempt, tokens in enumerate((max_tokens, max(max_tokens, 1600))):
            content, finish_reason = await self._request(
                messages, temperature, tokens,
                base_url=fb["base_url"], api_key=fb["api_key"],
                model=fb["model"], request_extras=fb["request_extras"],
            )
            if content:
                self._increment_count()
                self._fallback_failures = 0
                return content
            if finish_reason == "length" and attempt == 0:
                logger.warning("备选模型 content为空且被截断(max_tokens=%d)，放大重试", tokens)
                continue
            break
        self._fallback_failures += 1
        if self._fallback_failures >= 3:
            self._fallback_cooldown_until = time.time() + 600
            self._fallback_failures = 0
            logger.warning("备选模型连续失败3次，熔断冷却10分钟")
        return None

    async def _request(self, messages: list, temperature: float,
                       max_tokens: int, *, base_url: str = None, api_key: str = None,
                       model: str = None, request_extras: Dict[str, Any] = None) -> tuple:
        """发赢单次请求，返回 (content, finish_reason)；请求失败返回 (None, None)"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{base_url or self.base_url}/chat/completions",
                    headers=self._get_headers(api_key),
                    json={
                        "model": model or self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        **(request_extras if request_extras is not None else self.request_extras),
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
                break  # 请求失败，转备选模型
            logger.warning("LLM返回空content: finish_reason=%s", finish_reason)
            break
        return self._chat_fallback_sync(messages, temperature, max_tokens)

    def _chat_fallback_sync(self, messages: list, temperature: float, max_tokens: int) -> Optional[str]:
        """主模型失败后切备选模型（同步版；未配置或熔断冷却中则直接返回 None）"""
        fb = self.fallback
        if not fb or time.time() < self._fallback_cooldown_until:
            return None
        logger.warning("主模型失败，切换备选模型 %s", fb["model"])
        content = None
        for attempt, tokens in enumerate((max_tokens, max(max_tokens, 1600))):
            content, finish_reason = self._request_sync(
                messages, temperature, tokens,
                base_url=fb["base_url"], api_key=fb["api_key"],
                model=fb["model"], request_extras=fb["request_extras"],
            )
            if content:
                self._increment_count()
                self._fallback_failures = 0
                return content
            if finish_reason == "length" and attempt == 0:
                logger.warning("备选模型 content为空且被截断(max_tokens=%d)，放大重试", tokens)
                continue
            break
        self._fallback_failures += 1
        if self._fallback_failures >= 3:
            self._fallback_cooldown_until = time.time() + 600
            self._fallback_failures = 0
            logger.warning("备选模型连续失败3次，熔断冷却10分钟")
        return None

    def _request_sync(self, messages: list, temperature: float,
                      max_tokens: int, *, base_url: str = None, api_key: str = None,
                      model: str = None, request_extras: Dict[str, Any] = None) -> tuple:
        """同步单次请求，返回 (content, finish_reason)；请求失败返回 (None, None)"""
        try:
            with httpx.Client(timeout=30) as client:
                response = client.post(
                    f"{base_url or self.base_url}/chat/completions",
                    headers=self._get_headers(api_key),
                    json={
                        "model": model or self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        **(request_extras if request_extras is not None else self.request_extras),
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
