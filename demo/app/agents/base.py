"""义乌小商品出海智能体 - Agent基类"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    """Agent基类，所有智能体继承此类"""

    name: str = "base"
    description: str = ""

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
