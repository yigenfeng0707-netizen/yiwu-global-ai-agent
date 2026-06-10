"""义乌小商品出海智能体 - 签名验证中间件"""

import os
import hmac
import hashlib
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class SignatureMiddleware(BaseHTTPMiddleware):
    """API请求签名验证中间件"""

    async def dispatch(self, request: Request, call_next):
        api_secret = os.getenv("API_SECRET", "")
        if not api_secret:
            # 未配置API_SECRET则跳过签名验证
            return await call_next(request)

        # 只验证POST请求
        if request.method != "POST":
            return await call_next(request)

        # 读取签名头
        timestamp = request.headers.get("X-Timestamp", "")
        signature = request.headers.get("X-Signature", "")

        if not timestamp or not signature:
            return JSONResponse(
                status_code=401,
                content={"detail": "缺少签名信息"},
            )

        # 验证时间戳（5分钟有效期）
        try:
            if abs(time.time() - int(timestamp)) > 300:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "请求已过期"},
                )
        except ValueError:
            return JSONResponse(
                status_code=401,
                content={"detail": "时间戳格式错误"},
            )

        # 验证签名
        body = await request.body()
        message = f"{timestamp}:{body.decode('utf-8', errors='ignore')}"
        expected = hmac.new(
            api_secret.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(signature, expected):
            return JSONResponse(
                status_code=401,
                content={"detail": "签名验证失败"},
            )

        return await call_next(request)
