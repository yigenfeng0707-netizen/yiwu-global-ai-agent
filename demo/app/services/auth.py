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


# bcrypt 优先；未安装时降级为 SHA256 + per-user 随机盐（均优于原静态盐）
try:
    import bcrypt as _bcrypt
    _BCRYPT = True
except ImportError:
    _BCRYPT = False


def _hash_password(password: str) -> str:
    """密码哈希：bcrypt（自带随机盐）优先；降级 SHA256+per-user随机盐。输出带算法前缀。"""
    if _BCRYPT:
        return "bcrypt$" + _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()
    salt = secrets.token_hex(8)
    h = hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()
    return f"sha256${salt}${h}"


def _verify_password(password: str, stored: str) -> bool:
    """校验密码，兼容 bcrypt / sha256$随机盐 / legacy静态盐SHA256 三种历史格式。"""
    if not stored:
        return False
    if stored.startswith("bcrypt$"):
        return bool(_BCRYPT) and _bcrypt.checkpw(password.encode(), stored[7:].encode())
    if stored.startswith("sha256$"):
        try:
            _, salt, h = stored.split("$", 2)
        except ValueError:
            return False
        return hashlib.sha256(f"{salt}:{password}".encode()).hexdigest() == h
    # legacy：静态盐 SHA256（P2 之前注册的老用户）
    return hashlib.sha256(f"yiwu-chuhai:{password}".encode()).hexdigest() == stored


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

        if not _verify_password(password, user["password_hash"]):
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
