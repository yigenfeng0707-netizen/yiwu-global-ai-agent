"""义乌小商品出海智能体 - API 使用记录中间件（P2-9 接线 record_api_usage）"""

import time
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from ..db.database import get_db

logger = logging.getLogger(__name__)


class ApiUsageMiddleware(BaseHTTPMiddleware):
    """记录 /api/ 请求的调用情况到 api_usage 表，供 /stats/usage 统计。

    设计要点：
    - 置于中间件链最内层（在 Auth 之后执行），因此能读到 request.state.user；
    - 仅记录到达路由的 /api/ 请求（被限流/鉴权拦截的不计，符合"实际调用"语义）；
    - 轻量单次 INSERT（SQLite WAL），写入失败静默降级（debug 日志），绝不影响主流程；
    - 非 /api/ 路径（如 /health、静态资源）直接放行不记录。
    """

    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        start = time.time()
        response = await call_next(request)
        try:
            user = getattr(request.state, "user", None)
            email = user.get("email", "") if user else ""
            get_db().record_api_usage(
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                duration_ms=round((time.time() - start) * 1000, 2),
                user_email=email,
            )
        except Exception as e:
            logger.debug("api_usage 记录失败(%s): %s", request.url.path, e)
        return response
