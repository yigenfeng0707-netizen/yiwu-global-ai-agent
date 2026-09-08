"""中间件测试 - 补齐 auth / rate_limit / signature 的覆盖盲区（P2-5）

每个测试用独立的小 FastAPI app + 单个中间件，隔离验证各分支，
不依赖整个主应用，也不受其他中间件顺序影响。
"""

import time
import hmac
import json
import hashlib

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.auth import AuthMiddleware
from app.middleware.signature import SignatureMiddleware
from app.services.auth import auth_service


# ==================== RateLimitMiddleware ====================

@pytest.mark.asyncio
async def test_rate_limit_anonymous_triggers_429():
    """匿名用户超过 anonymous_limit 后返回 429"""
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, anonymous_limit=3, authenticated_limit=100)

    @app.get("/api/test")
    async def ep():
        return {"ok": True}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        codes = [(await c.get("/api/test")).status_code for _ in range(5)]
    assert codes[:3] == [200, 200, 200]
    assert codes[3] == 429
    assert codes[4] == 429


@pytest.mark.asyncio
async def test_rate_limit_non_api_not_limited():
    """非 /api/ 路径（如 /health）不限流"""
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, anonymous_limit=2, authenticated_limit=100)

    @app.get("/health")
    async def ep():
        return {"ok": True}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        codes = [(await c.get("/health")).status_code for _ in range(6)]
    assert all(x == 200 for x in codes)


@pytest.mark.asyncio
async def test_rate_limit_authenticated_higher_limit():
    """认证用户（request.state.user 存在）走更高的 authenticated_limit（验证 P2-1 顺序修复后该分支可用）"""
    from starlette.middleware.base import BaseHTTPMiddleware

    class InjectUser(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            request.state.user = {"email": "vip@test.com"}
            return await call_next(request)

    app = FastAPI()
    # 后注册者先执行：RateLimit 先注册、InjectUser 后注册 → InjectUser 先跑设 user，RateLimit 再读到
    app.add_middleware(RateLimitMiddleware, anonymous_limit=2, authenticated_limit=5)
    app.add_middleware(InjectUser)

    @app.get("/api/test")
    async def ep():
        return {"ok": True}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        codes = [(await c.get("/api/test")).status_code for _ in range(6)]
    # 认证用户 limit=5：前5次200，第6次429（而非匿名 limit=2 的第3次就429）
    assert codes[:5] == [200, 200, 200, 200, 200]
    assert codes[5] == 429


# ==================== AuthMiddleware ====================

@pytest.mark.asyncio
async def test_auth_skipped_without_jwt_secret(monkeypatch):
    """未配置 JWT_SECRET 时跳过认证（fail-open），受保护路径仍可访问"""
    monkeypatch.delenv("JWT_SECRET", raising=False)
    app = FastAPI()
    app.add_middleware(AuthMiddleware)

    @app.post("/api/v1/pipeline")
    async def ep():
        return {"ok": True}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.post("/api/v1/pipeline", json={})
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_auth_401_without_token(monkeypatch):
    """配置 JWT_SECRET 后，受保护路径无 token → 401"""
    monkeypatch.setenv("JWT_SECRET", auth_service.secret or "test-secret")
    app = FastAPI()
    app.add_middleware(AuthMiddleware)

    @app.post("/api/v1/pipeline")
    async def ep():
        return {"ok": True}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.post("/api/v1/pipeline", json={})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_auth_401_invalid_token(monkeypatch):
    """配置 JWT_SECRET 后，无效 token → 401"""
    monkeypatch.setenv("JWT_SECRET", auth_service.secret or "test-secret")
    app = FastAPI()
    app.add_middleware(AuthMiddleware)

    @app.post("/api/v1/customer-service/chat")
    async def ep():
        return {"ok": True}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.post("/api/v1/customer-service/chat", json={},
                         headers={"Authorization": "Bearer invalid.token.here"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_auth_pass_with_valid_token(monkeypatch):
    """配置 JWT_SECRET 后，有效 token 放行并附加 request.state.user"""
    monkeypatch.setenv("JWT_SECRET", auth_service.secret)
    app = FastAPI()
    app.add_middleware(AuthMiddleware)

    @app.post("/api/v1/pipeline")
    async def ep():
        return {"ok": True}

    token = auth_service._create_token({"id": 1, "email": "t@t.com", "company": ""})
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.post("/api/v1/pipeline", json={},
                         headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_auth_non_protected_path_open(monkeypatch):
    """即使配置 JWT_SECRET，非保护路径（如 /api/v1/status）的 POST 也放行"""
    monkeypatch.setenv("JWT_SECRET", auth_service.secret or "test-secret")
    app = FastAPI()
    app.add_middleware(AuthMiddleware)

    @app.post("/api/v1/other")
    async def ep():
        return {"ok": True}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.post("/api/v1/other", json={})
    assert r.status_code == 200


# ==================== SignatureMiddleware ====================

@pytest.mark.asyncio
async def test_signature_skipped_without_api_secret(monkeypatch):
    """未配置 API_SECRET 时跳过签名校验"""
    monkeypatch.delenv("API_SECRET", raising=False)
    app = FastAPI()
    app.add_middleware(SignatureMiddleware)

    @app.post("/api/v1/x")
    async def ep():
        return {"ok": True}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.post("/api/v1/x", json={"a": 1})
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_signature_401_missing_header(monkeypatch):
    """配置 API_SECRET 后，POST 缺签名头 → 401"""
    monkeypatch.setenv("API_SECRET", "test-api-secret")
    app = FastAPI()
    app.add_middleware(SignatureMiddleware)

    @app.post("/api/v1/x")
    async def ep():
        return {"ok": True}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.post("/api/v1/x", json={"a": 1})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_signature_401_expired_timestamp(monkeypatch):
    """配置 API_SECRET 后，时间戳过期（>5分钟）→ 401"""
    secret = "test-api-secret"
    monkeypatch.setenv("API_SECRET", secret)
    app = FastAPI()
    app.add_middleware(SignatureMiddleware)

    @app.post("/api/v1/x")
    async def ep():
        return {"ok": True}

    body = json.dumps({"a": 1})
    old_ts = str(int(time.time()) - 600)  # 10分钟前
    sig = hmac.new(secret.encode(), f"{old_ts}:{body}".encode(), hashlib.sha256).hexdigest()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.post("/api/v1/x", content=body,
                         headers={"Content-Type": "application/json", "X-Timestamp": old_ts, "X-Signature": sig})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_signature_pass_with_valid_signature(monkeypatch):
    """配置 API_SECRET 后，正确时间戳+签名放行"""
    secret = "test-api-secret"
    monkeypatch.setenv("API_SECRET", secret)
    app = FastAPI()
    app.add_middleware(SignatureMiddleware)

    @app.post("/api/v1/x")
    async def ep():
        return {"ok": True}

    body = json.dumps({"a": 1})
    ts = str(int(time.time()))
    sig = hmac.new(secret.encode(), f"{ts}:{body}".encode(), hashlib.sha256).hexdigest()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.post("/api/v1/x", content=body,
                         headers={"Content-Type": "application/json", "X-Timestamp": ts, "X-Signature": sig})
    assert r.status_code == 200
