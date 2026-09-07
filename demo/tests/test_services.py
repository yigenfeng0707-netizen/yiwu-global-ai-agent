"""测试服务层模块"""

import os
import time
import pytest
import tempfile
from app.services.auth import AuthService, _hash_password
from app.services.llm import LLMService
from app.models.schemas import (
    ContentGenerateRequest, CustomerChatRequest, TariffCalcRequest,
    LoginRequest, RegisterRequest, PipelineRequest, SupplyChainRequest,
    PolicyBenefitCalcRequest,
)
from app.data.sources import (
    DataSourceManager, YiwuMarketDataSource, YixinouLogisticsDataSource,
    AmazonDataSource, AlibabaDataSource, IndustryReportDataSource,
)


# ==================== 认证服务 ====================

class TestAuthService:
    @pytest.fixture
    def auth(self):
        fd, path = tempfile.mkstemp(suffix=".db")
        os.environ["DATABASE_PATH"] = path
        # 重新导入以使用新数据库路径
        from app.db.database import Database
        db = Database(db_path=path)
        service = AuthService()
        service.db = db
        yield service
        try:
            os.close(fd)
            os.unlink(path)
        except Exception:
            pass

    def test_register_success(self, auth):
        result = auth.register("new@test.com", "pass123", "Company")
        assert result["success"] is True

    def test_register_duplicate(self, auth):
        auth.register("dup@test.com", "pass")
        result = auth.register("dup@test.com", "pass")
        assert result["success"] is False

    def test_login_success(self, auth):
        auth.register("login@test.com", "pass123")
        result = auth.login("login@test.com", "pass123")
        assert result["success"] is True
        assert "token" in result

    def test_login_wrong_password(self, auth):
        auth.register("wp@test.com", "correct")
        result = auth.login("wp@test.com", "wrong")
        assert result["success"] is False

    def test_login_nonexistent(self, auth):
        result = auth.login("noone@test.com", "pass")
        assert result["success"] is False

    def test_token_verify(self, auth):
        auth.register("verify@test.com", "pass")
        login = auth.login("verify@test.com", "pass")
        payload = auth.verify(login["token"])
        assert payload is not None
        assert payload["email"] == "verify@test.com"

    def test_password_hash(self):
        h1 = _hash_password("test")
        h2 = _hash_password("test")
        assert h1 == h2
        assert _hash_password("different") != h1


# ==================== LLM服务 ====================

class TestLLMService:
    def test_init_defaults(self):
        service = LLMService()
        assert service.model == os.getenv("LLM_MODEL", "qwen-plus")
        assert service.daily_limit > 0

    def test_daily_limit_check(self):
        service = LLMService()
        service.daily_limit = 2
        service._daily_count = 0
        assert service._check_limit() is True
        service._daily_count = 2
        assert service._check_limit() is False

    def test_daily_usage_property(self):
        service = LLMService()
        usage = service.daily_usage
        assert "used" in usage
        assert "limit" in usage


# ==================== Pydantic模型 ====================

class TestSchemas:
    def test_content_request_defaults(self):
        req = ContentGenerateRequest()
        assert req.category == "日用百货"
        assert req.platform == "amazon"

    def test_tariff_calc_request(self):
        req = TariffCalcRequest(product_value=5000)
        assert req.product_value == 5000
        assert req.target_country == "德国"

    def test_pipeline_request(self):
        req = PipelineRequest(category="玩具", region="东南亚")
        assert req.category == "玩具"

    def test_login_request(self):
        req = LoginRequest(email="test@test.com", password="pass")
        assert req.email == "test@test.com"


# ==================== 数据源管理 ====================

class TestDataSources:
    def test_manager_init(self):
        manager = DataSourceManager()
        sources = manager.list_sources()
        assert len(sources) == 5

    def test_fetch_all(self):
        manager = DataSourceManager()
        results = manager.fetch_all("玩具")
        assert len(results) == 5

    def test_fetch_by_source(self):
        manager = DataSourceManager()
        result = manager.fetch_by_source("义新欧班列", "")
        assert result is not None
        assert result["source"] == "义新欧班列"

    def test_yiwu_market_data(self):
        source = YiwuMarketDataSource()
        result = source.fetch("玩具")
        assert result["total_shops"] == 75000
        assert len(result["products"]) > 0

    def test_yixinou_logistics(self):
        source = YixinouLogisticsDataSource()
        result = source.fetch()
        assert result["total_routes"] == 19
        assert len(result["routes"]) > 0

    def test_amazon_data(self):
        source = AmazonDataSource()
        result = source.fetch("玩具")
        assert "avg_selling_price" in result

    def test_alibaba_data(self):
        source = AlibabaDataSource()
        result = source.fetch("玩具")
        assert "supplier_count" in result

    def test_industry_report(self):
        source = IndustryReportDataSource()
        result = source.fetch("玩具")
        assert "market_size" in result
        assert "growth" in result
