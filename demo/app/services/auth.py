"""义乌小商品出海智能体 - 认证服务（数据库持久化版）"""

import logging
import os
import time
import hashlib
import secrets
from typing import Optional, Dict, Any

import jwt

from ..db.database import get_db

logger = logging.getLogger(__name__)


def _hash_password(password: str, salt: str = "yiwu-chuhai") -> str:
    """密码哈希（SHA256 + salt）"""
    return hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()


class AuthService:
    """JWT认证服务 - SQLite持久化"""

    def __init__(self):
        self.secret = os.getenv("JWT_SECRET", "")
        if not self.secret:
            # 不再使用随仓库开源的固定兜底密钥（可被伪造）；改为进程级随机密钥。
            # 影响：进程重启后旧 token 失效；多 worker 间 token 不通用（当前为单 worker 内存态，可接受）。
            # 生产环境务必注入 JWT_SECRET 以获得稳定、跨进程的签名密钥。
            self.secret = secrets.token_hex(32)
            logger.warning("JWT_SECRET 未配置，已生成进程级随机密钥（重启后旧 token 失效；生产环境须注入 JWT_SECRET）")
        self.algorithm = "HS256"
        self.expire_hours = 24
        self.db = get_db()

    def register(self, email: str, password: str, company: str = "") -> Dict[str, Any]:
        """注册 - 持久化到数据库"""
        password_hash = _hash_password(password)
        user_id = self.db.create_user(email, password_hash, company)
        if user_id is None:
            return {"success": False, "detail": "邮箱已注册"}

        return {"success": True, "user_id": f"user_{user_id}", "email": email}

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """登录 - 从数据库验证"""
        user = self.db.get_user_by_email(email)
        if not user:
            return {"success": False, "detail": "邮箱或密码错误"}

        password_hash = _hash_password(password)
        if user["password_hash"] != password_hash:
            return {"success": False, "detail": "邮箱或密码错误"}

        if not user.get("is_active", 1):
            return {"success": False, "detail": "账号已被禁用"}

        self.db.update_last_login(email)

        token = self._create_token(user)
        return {
            "success": True,
            "token": token,
            "email": email,
            "user_id": f"user_{user['id']}",
            "company": user.get("company", ""),
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
            "sub": f"user_{user['id']}",
            "email": user["email"],
            "company": user.get("company", ""),
            "exp": int(time.time()) + self.expire_hours * 3600,
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def get_stats(self) -> Dict[str, Any]:
        """获取认证统计"""
        return {
            "total_users": self.db.get_user_count(),
        }


# 全局认证服务实例
auth_service = AuthService()
