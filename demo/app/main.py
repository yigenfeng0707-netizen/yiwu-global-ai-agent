"""义乌小商品出海智能体 - FastAPI主应用"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .middleware.auth import AuthMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.signature import SignatureMiddleware

app = FastAPI(
    title="义乌小商品出海智能体 API",
    description="基于义乌小商品城数据，为跨境电商提供市场洞察、智能选品、供应链匹配、内容生成、合规查询、智能客服等一站式AI服务",
    version="2.0.0",
)

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


@app.get("/")
async def root():
    return {
        "service": "义乌小商品出海智能体",
        "version": "2.0.0",
        "description": "基于义乌小商品城7.5万商户、210万+SKU，为跨境电商提供一站式AI智能服务",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "yiwu-chuhai-api"}
