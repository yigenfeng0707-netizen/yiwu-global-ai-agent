"""义乌小商品出海智能体 - Agent基类（LLM增强版）"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..services.llm import llm_service
from ..db.database import get_db

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Agent基类 - 所有智能体继承此类，内置LLM调用与查询记录"""

    name: str = "base"
    description: str = ""

    # 子类可覆盖的LLM系统提示
    LLM_SYSTEM_PROMPT: str = "你是义乌小商品出海智能助手，回答要专业、简洁、实用。"

    def __init__(self):
        self._db = get_db()

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """执行Agent任务"""
        pass

    def _wrap_response(self, data: Dict[str, Any], agent_name: str = "") -> Dict[str, Any]:
        """包装Agent响应"""
        return {
            "agent": agent_name or self.name,
            "status": "success",
            **data,
        }

    def info(self) -> Dict[str, str]:
        """获取Agent信息"""
        return {
            "name": self.name,
            "description": self.description,
        }

    async def llm_chat(self, messages: list, temperature: float = 0.7,
                       max_tokens: int = 1000) -> Optional[str]:
        """调用LLM - 封装超时保护和错误处理"""
        import asyncio
        try:
            # 25s：兼容推理模型截断重试（最多两次 LLM 调用）
            return await asyncio.wait_for(
                llm_service.chat(messages, temperature=temperature, max_tokens=max_tokens),
                timeout=25.0,
            )
        except Exception:
            return None

    async def llm_generate(self, prompt: str, system_prompt: str = "",
                           temperature: float = 0.7, max_tokens: int = 800) -> Optional[str]:
        """便捷方法 - 单轮LLM生成"""
        sys = system_prompt or self.LLM_SYSTEM_PROMPT
        messages = [
            {"role": "system", "content": sys},
            {"role": "user", "content": prompt},
        ]
        return await self.llm_chat(messages, temperature=temperature, max_tokens=max_tokens)

    async def llm_enhance(self, base_result: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """LLM增强 - 为基础结果添加AI洞察摘要"""
        if not llm_service.api_key:
            return base_result

        prompt = f"基于以下数据，给出2-3条简洁的商业洞察建议（每条不超过50字）：\n{context}\n\n数据摘要：{str(base_result)[:500]}"
        insight = await self.llm_generate(prompt, temperature=0.5, max_tokens=300)
        if insight:
            base_result["ai_insight"] = insight.strip()
        return base_result

    def record_query(self, params: Dict[str, Any], result_summary: str = ""):
        """记录查询到数据库"""
        try:
            self._db.record_query(self.name, params, result_summary)
        except Exception as e:
            # 记录失败不影响主流程，但保留调试日志（不再静默吞异常）
            logger.debug("record_query 写入失败(%s): %s", self.name, e)
