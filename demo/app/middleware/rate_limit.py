"""义乌小商品出海智能体 - 限流中间件"""

import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """请求限流中间件"""

    def __init__(self, app, anonymous_limit: int = 30, authenticated_limit: int = 100):
        super().__init__(app)
        self.anonymous_limit = anonymous_limit  # 匿名用户每分钟限制
        self.authenticated_limit = authenticated_limit  # 认证用户每分钟限制
        self._requests: dict = defaultdict(list)

    def _cleanup(self, key: str):
        """清理过期记录"""
        now = time.time()
        self._requests[key] = [t for t in self._requests[key] if now - t < 60]

    async def dispatch(self, request: Request, call_next):
        # 只限制API请求
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        # 获取客户端标识
        user = getattr(request.state, "user", None)
        if user:
            key = f"user:{user.get('email', 'unknown')}"
            limit = self.authenticated_limit
        else:
            key = f"ip:{request.client.host if request.client else 'unknown'}"
            limit = self.anonymous_limit

        self._cleanup(key)

        if len(self._requests[key]) >= limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "请求过于频繁，请稍后再试"},
            )

        self._requests[key].append(time.time())
        return await call_next(request)
