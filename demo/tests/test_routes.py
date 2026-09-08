"""测试API路由"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ==================== 基础接口 ====================

class TestBasicRoutes:
    @pytest.mark.asyncio
    async def test_api_root(self, client):
        resp = await client.get("/api/v1/")
        assert resp.status_code == 200
        data = resp.json()
        assert "service" in data
        assert "version" in data

    @pytest.mark.asyncio
    async def test_health(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_agents_info(self, client):
        resp = await client.get("/api/v1/agents/info")
        assert resp.status_code == 200
        agents = resp.json()["agents"]
        assert len(agents) == 7

    @pytest.mark.asyncio
    async def test_categories(self, client):
        resp = await client.get("/api/v1/categories")
        assert resp.status_code == 200
        categories = resp.json()["categories"]
        assert len(categories) == 10
        assert "日用百货" in categories

    @pytest.mark.asyncio
    async def test_regions(self, client):
        resp = await client.get("/api/v1/regions")
        assert resp.status_code == 200
        regions = resp.json()["regions"]
        assert len(regions) > 0

    @pytest.mark.asyncio
    async def test_yiwu_index(self, client):
        resp = await client.get("/api/v1/yiwu-index")
        assert resp.status_code == 200
        data = resp.json()
        # P1-1：诚实拆分为 演示基准 + 官方发布真实值 + 实时汇率 三段
        assert "demo_composite" in data
        assert "official_published" in data
        assert "exchange_rate" in data
        # 演示基准段保留旧字段（向后兼容）
        assert "current" in data["demo_composite"]
        assert "trend" in data["demo_composite"]
        assert data["demo_composite"]["is_real"] is False
        # 官方发布段带溯源结构（不依赖 live 网络，仅校验字段存在）
        assert "is_real" in data["official_published"]
        assert "records" in data["official_published"]
        assert "source_url" in data["official_published"]


# ==================== 业务接口 ====================

class TestBusinessRoutes:
    @pytest.mark.asyncio
    async def test_market_insight(self, client):
        resp = await client.get("/api/v1/market-insight?category=玩具&region=东南亚")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["category"] == "玩具"

    @pytest.mark.asyncio
    async def test_smart_selection(self, client):
        resp = await client.get("/api/v1/smart-selection?category=日用百货&budget=中")
        assert resp.status_code == 200
        data = resp.json()
        assert "overall_score" in data

    @pytest.mark.asyncio
    async def test_supply_chain(self, client):
        resp = await client.get("/api/v1/supply-chain/玩具")
        assert resp.status_code == 200
        data = resp.json()
        assert "suppliers" in data
        assert "logistics" in data

    @pytest.mark.asyncio
    async def test_compliance(self, client):
        resp = await client.get("/api/v1/compliance?category=玩具&target_country=德国")
        assert resp.status_code == 200
        data = resp.json()
        assert "certifications" in data

    @pytest.mark.asyncio
    async def test_content_generate(self, client):
        resp = await client.post("/api/v1/content/generate", json={
            "product_name": "USB风扇",
            "category": "电子电器",
            "platform": "amazon",
            "target_language": "en",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "content" in data

    @pytest.mark.asyncio
    async def test_customer_service_chat(self, client):
        resp = await client.post("/api/v1/customer-service/chat", json={
            "message": "你好，我想了解玩具出口",
            "category": "玩具",
            "language": "zh",
            "session_id": "test_session",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "reply" in data

    @pytest.mark.asyncio
    async def test_policy_cities(self, client):
        resp = await client.get("/api/v1/policy-replication/cities")
        assert resp.status_code == 200
        data = resp.json()
        assert "cities" in data
        assert len(data["cities"]) > 0

    @pytest.mark.asyncio
    async def test_tariff_calculate(self, client):
        resp = await client.post("/api/v1/tariff/calculate", json={
            "category": "玩具",
            "target_country": "德国",
            "product_value": 10000,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_cost"] > 10000

    @pytest.mark.asyncio
    async def test_pipeline(self, client):
        resp = await client.post("/api/v1/pipeline", json={
            "category": "玩具",
            "region": "东南亚",
            "budget": "中",
            "target_country": "泰国",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "summary" in data
        assert data["summary"]["total_steps"] == 7


# ==================== 认证接口 ====================

class TestAuthRoutes:
    @pytest.mark.asyncio
    async def test_register_and_login(self, client):
        # 注册
        resp = await client.post("/api/v1/auth/register", json={
            "email": "testuser@example.com",
            "password": "testpass123",
            "company": "TestCo",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

        # 登录
        resp = await client.post("/api/v1/auth/login", json={
            "email": "testuser@example.com",
            "password": "testpass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "token" in data

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client):
        # 先注册
        await client.post("/api/v1/auth/register", json={
            "email": "wrong@example.com",
            "password": "correct",
        })
        # 错误密码
        resp = await client.post("/api/v1/auth/login", json={
            "email": "wrong@example.com",
            "password": "incorrect",
        })
        # P2-3: 登录失败返回 401（REST 规范），不再 200+success:false
        assert resp.status_code == 401
        assert "detail" in resp.json()


# ==================== 系统监控 ====================

class TestMonitorRoutes:
    @pytest.mark.asyncio
    async def test_status(self, client):
        resp = await client.get("/api/v1/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "agents" in data
        assert "cache" in data

    @pytest.mark.asyncio
    async def test_usage_stats(self, client):
        resp = await client.get("/api/v1/stats/usage")
        assert resp.status_code == 200
        data = resp.json()
        assert "api_usage" in data
        assert "cache" in data

    @pytest.mark.asyncio
    async def test_query_history(self, client):
        resp = await client.get("/api/v1/stats/history")
        assert resp.status_code == 200
        assert "history" in resp.json()
