"""义乌小商品出海智能体 - FastAPI主应用"""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .api.routes import router
from .middleware.auth import AuthMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.signature import SignatureMiddleware

app = FastAPI(
    title="义乌小商品出海智能体 API",
    description="基于义乌小商品城数据，为跨境电商提供市场洞察、智能选品、供应链匹配、内容生成、合规查询、智能客服等一站式AI服务",
    version="2.0.0",
)

# 前端静态资源目录（魔搭创空间等单容器部署时由 CI 注入 web_dist）
WEB_DIST = Path(os.getenv("WEB_DIST") or Path(__file__).resolve().parent.parent / "web_dist")

# CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins:
    origins = [o.strip() for o in allowed_origins.split(",") if o.strip()]
else:
    origins = ["*"]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(SignatureMiddleware)

# 注册路由
app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "yiwu-chuhai-api"}


if WEB_DIST.is_dir():
    # 单容器模式：前端静态资源 + SPA 路由回退（显式路由已注册，兜底路由必须最后定义）
    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str):
        target = WEB_DIST / full_path
        if full_path and target.is_file():
            return FileResponse(target)
        return FileResponse(WEB_DIST / "index.html")

else:
    # 纯 API 模式（Render 等前后端分离部署）
    @app.get("/")
    async def root():
        return {
            "service": "义乌小商品出海智能体",
            "version": "2.0.0",
            "description": "基于义乌小商品城7.5万商户、210万+SKU，为跨境电商提供一站式AI智能服务",
        }
