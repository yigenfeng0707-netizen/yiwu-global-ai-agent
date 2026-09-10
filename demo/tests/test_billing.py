"""P3-5 商业化验证测试 - 定价 A/B 测试 / 转化埋点 / 沙箱支付"""

import os
import tempfile
import pytest

from app.db.database import Database
from app.services.billing import billing_service, BillingService, PLANS, PLAN_MAP


class TestBillingService:
    """BillingService 全链路测试"""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """每个测试用独立数据库，避免串扰。"""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.environ["DATABASE_PATH"] = path
        db = Database(db_path=path)
        # billing_service 是全局实例，需要刷新其 db 引用
        billing_service.db = db
        yield
        db.close_all()
        try:
            os.close(fd)
            os.unlink(path)
        except PermissionError:
            pass

    # ==================== A/B 测试 ====================

    def test_variant_deterministic(self):
        """同一用户每次分到同一变体。"""
        v1 = billing_service.get_variant("user1@test.com", "user1@test.com")
        v2 = billing_service.get_variant("user1@test.com", "user1@test.com")
        assert v1 == v2
        assert v1 in ("variant_a", "variant_b")

    def test_variant_persisted(self):
        """变体分配后持久化到 DB。"""
        v = billing_service.get_variant("user2@test.com", "user2@test.com")
        stored = billing_service.db.get_ab_variant("pricing_layout", "user2@test.com")
        assert stored is not None
        assert stored["variant"] == v

    def test_variant_different_users(self):
        """不同用户可能分到不同变体（覆盖至少两种变体）。"""
        variants = set()
        for i in range(50):
            v = billing_service.get_variant(f"user{i}@test.com", f"user{i}@test.com")
            variants.add(v)
        # 50 个用户应该覆盖至少 2 种变体
        assert len(variants) >= 2

    def test_get_plans_with_variant(self):
        """获取套餐列表+变体信息。"""
        result = billing_service.get_plans_with_variant(
            "user3@test.com", "user3@test.com"
        )
        assert len(result["plans"]) == 4
        assert result["variant"] in ("variant_a", "variant_b")
        assert result["layout"] in ("grid-3", "grid-4")
        assert result["experiment"] == "pricing_layout"
        # 高亮套餐只有一个
        highlights = [p for p in result["plans"] if p["highlight"]]
        assert len(highlights) == 1

    # ==================== 转化埋点 ====================

    def test_track_event(self):
        """记录转化事件。"""
        eid = billing_service.track(
            "page_view", "user@test.com", "", "variant_a", "sess1"
        )
        assert eid > 0

    def test_track_event_with_metadata(self):
        """记录带 metadata 的事件。"""
        eid = billing_service.track(
            "plan_click",
            "user@test.com",
            "basic",
            "variant_a",
            "sess1",
            metadata={"source": "hero_cta"},
        )
        assert eid > 0

    def test_funnel_summary(self):
        """漏斗汇总正确计算。"""
        billing_service.track("page_view", "user@test.com", "", "", "sess1")
        billing_service.track("plan_click", "user@test.com", "basic", "", "sess1")
        billing_service.track("checkout_start", "user@test.com", "basic")
        billing_service.track("checkout_complete", "user@test.com", "basic")

        summary = billing_service.get_funnel_summary(24)
        assert summary["events"]["page_view"] == 1
        assert summary["events"]["plan_click"] == 1
        assert summary["events"]["checkout_start"] == 1
        assert summary["events"]["checkout_complete"] == 1
        assert summary["total_events"] == 4
        assert summary["conversion_rate"] == 100.0
        assert summary["checkout_rate"] == 100.0
        assert summary["payment_rate"] == 100.0

    # ==================== 沙箱支付 ====================

    def test_create_checkout(self):
        """创建沙箱订单。"""
        result = billing_service.create_checkout("payuser@test.com", "basic")
        assert result["success"] is True
        assert result["order_no"].startswith("YW")
        assert result["amount_cny"] == 299
        assert result["plan_name"] == "基础版"
        assert result["status"] == "pending"
        assert result["provider"] == "sandbox"
        assert "sandbox" in result["note"].lower() or "沙箱" in result["note"]

    def test_create_checkout_invalid_plan(self):
        """未知套餐创建订单失败。"""
        result = billing_service.create_checkout("payuser@test.com", "nonexistent")
        assert result["success"] is False

    def test_confirm_payment(self):
        """完整支付流程：创建订单 -> 确认支付 -> 获得订阅。"""
        # 创建订单
        checkout = billing_service.create_checkout("payuser2@test.com", "pro")
        assert checkout["success"]

        # 确认支付
        pay_result = billing_service.confirm_payment(
            checkout["order_no"], "payuser2@test.com"
        )
        assert pay_result["success"] is True
        assert pay_result["status"] == "paid"
        assert pay_result["plan_code"] == "pro"
        assert pay_result["plan_name"] == "高级版"
        assert pay_result["subscription_id"] > 0

        # 验证订阅已创建
        sub = billing_service.get_subscription("payuser2@test.com")
        assert sub is not None
        assert sub["plan_code"] == "pro"
        assert sub["status"] == "active"
        assert sub["expires_at"] > sub["started_at"]

    def test_confirm_payment_already_paid(self):
        """重复支付同一订单。"""
        checkout = billing_service.create_checkout("payuser3@test.com", "basic")
        r1 = billing_service.confirm_payment(checkout["order_no"], "payuser3@test.com")
        assert r1["success"] is True

        r2 = billing_service.confirm_payment(checkout["order_no"], "payuser3@test.com")
        assert r2["success"] is True
        assert r2.get("already_paid") is True

    def test_confirm_payment_wrong_user(self):
        """订单归属不匹配。"""
        checkout = billing_service.create_checkout("user_a@test.com", "basic")
        result = billing_service.confirm_payment(
            checkout["order_no"], "user_b@test.com"
        )
        assert result["success"] is False
        assert "归属不匹配" in result["detail"]

    def test_confirm_payment_nonexistent_order(self):
        """不存在的订单。"""
        result = billing_service.confirm_payment("YW_NONEXISTENT", "user@test.com")
        assert result["success"] is False

    # ==================== 订单历史 ====================

    def test_list_orders(self):
        """订单列表正确返回。"""
        billing_service.create_checkout("orders_user@test.com", "basic")
        billing_service.create_checkout("orders_user@test.com", "pro")

        orders = billing_service.get_orders("orders_user@test.com")
        assert len(orders) == 2
        # 按创建时间倒序（最新在前）
        assert orders[0]["created_at"] >= orders[1]["created_at"]

    # ==================== 套餐定义 ====================

    def test_plans_complete(self):
        """4 个套餐字段完整。"""
        for plan in PLANS:
            assert "code" in plan
            assert "name" in plan
            assert "price_cny" in plan
            assert "features" in plan
            assert "duration_days" in plan
            assert len(plan["features"]) >= 5

    def test_plan_map(self):
        """PLAN_MAP 与 PLANS 一致。"""
        for plan in PLANS:
            assert plan["code"] in PLAN_MAP
            assert PLAN_MAP[plan["code"]]["name"] == plan["name"]
