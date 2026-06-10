"""义乌小商品出海智能体 - 认证服务"""

import os
import time
import secrets
from typing import Optional, Dict, Any

import jwt


class AuthService:
    """JWT认证服务"""

    def __init__(self):
        self.secret = os.getenv("JWT_SECRET", "yiwu-chuhai-dev-secret-key")
        self.algorithm = "HS256"
        self.expire_hours = 24
        # 内存用户存储
        self._users: Dict[str, Dict[str, Any]] = {}

    def register(self, email: str, password: str, company: str = "") -> Dict[str, Any]:
        """注册"""
        if email in self._users:
            return {"success": False, "detail": "邮箱已注册"}

        user_id = f"user_{secrets.token_hex(8)}"
        self._users[email] = {
            "id": user_id,
            "email": email,
            "password": password,
            "company": company,
            "plan": "free",
            "created_at": time.time(),
        }

        return {"success": True, "user_id": user_id}

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """登录"""
        user = self._users.get(email)
        if not user or user["password"] != password:
            return {"success": False, "detail": "邮箱或密码错误"}

        token = self._create_token(user)
        return {
            "success": True,
            "token": token,
            "email": email,
            "user_id": user["id"],
        }

    def verify(self, token: str) -> Optional[Dict[str, Any]]:
        """验证Token"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def _create_token(self, user: Dict[str, Any]) -> str:
        """创建JWT Token"""
        payload = {
            "sub": user["id"],
            "email": user["email"],
            "plan": user.get("plan", "free"),
            "exp": int(time.time()) + self.expire_hours * 3600,
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)


# 全局认证服务实例
auth_service = AuthService()
