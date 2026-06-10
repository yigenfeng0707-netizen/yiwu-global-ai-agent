"""义乌小商品出海智能体 - 认证中间件"""

import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from ..services.auth import auth_service


class AuthMiddleware(BaseHTTPMiddleware):
    """JWT认证中间件 - 保护LLM消耗接口"""

    # 需要认证的路径
    PROTECTED_PATHS = [
        "/api/v1/content/generate",
        "/api/v1/customer-service/chat",
        "/api/v1/pipeline",
    ]

    async def dispatch(self, request: Request, call_next):
        # 检查是否需要认证
        jwt_secret = os.getenv("JWT_SECRET", "")
        if not jwt_secret:
            # 未配置JWT_SECRET则跳过认证
            return await call_next(request)

        path = request.url.path
        needs_auth = any(path.startswith(p) for p in self.PROTECTED_PATHS)

        if needs_auth and request.method == "POST":
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "未提供认证令牌"},
                )

            token = auth_header[7:]
            payload = auth_service.verify(token)
            if not payload:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "认证令牌无效或已过期"},
                )

            # 将用户信息附加到请求状态
            request.state.user = payload

        return await call_next(request)
