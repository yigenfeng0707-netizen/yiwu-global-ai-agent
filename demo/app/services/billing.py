"""P3-5 商业化验证 - 计费与转化服务

实现：
  - 定价 A/B 测试：确定性 hash 分桶，同一用户永远看到同一变体
  - 付费转化埋点：page_view / plan_click / checkout_start / checkout_complete / checkout_abandon
  - 沙箱支付闭环：创建订单 -> 模拟支付回调 -> 激活订阅
  - 与前端 Pricing 页形成真实闭环（非 mock）
"""

import hashlib
import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from ..db.database import get_db

logger = logging.getLogger(__name__)

# ==================== 套餐定义（SSOT） ====================

PLANS: List[Dict[str, Any]] = [
    {
        "code": "yiwu_merchant",
        "name": "义乌商户专享版",
        "price_cny": 199,
        "price_display": "199",
        "period": "元/月",
        "description": "义乌国际商贸城商户专属普惠价",
        "features": [
            "高级版全部功能",
            "义乌专属数据",
            "供应链优先匹配",
            "1039合规指导",
            "义新欧班列专享运价",
        ],
        "highlight": True,
        "cta": "义乌商户首选",
        "duration_days": 30,
    },
    {
        "code": "basic",
        "name": "基础版",
        "price_cny": 299,
        "price_display": "299",
        "period": "元/月",
        "description": "适合小微企业和个人卖家",
        "features": [
            "市场洞察报告",
            "智能选品推荐",
            "跨境内容生成",
            "10大品类覆盖",
            "8种语言支持",
        ],
        "highlight": False,
        "cta": "立即订阅",
        "duration_days": 30,
    },
    {
        "code": "pro",
        "name": "高级版",
        "price_cny": 999,
        "price_display": "999",
        "period": "元/月",
        "description": "适合成长型电商企业",
        "features": [
            "基础版全部功能",
            "供应链匹配(7大Agent)",
            "合规助手(15国)",
            "智能客服(7x24h)",
            "义新欧班列物流",
        ],
        "highlight": False,
        "cta": "立即订阅",
        "duration_days": 30,
    },
    {
        "code": "enterprise",
        "name": "企业定制",
        "price_cny": 50000,
        "price_display": "5万",
        "period": "起/年",
        "description": "适合大型企业和团队",
        "features": [
            "高级版全部功能",
            "私有化部署",
            "定制Agent开发",
            "API接口对接",
            "专属客户经理",
        ],
        "highlight": False,
        "cta": "联系我们",
        "duration_days": 365,
    },
]

PLAN_MAP: Dict[str, Dict[str, Any]] = {p["code"]: p for p in PLANS}

# ==================== A/B 测试配置 ====================

# 实验名称：pricing_layout
#   variant_a: 原始布局（卡片 3 列，突出"义乌商户专享版"）
#   variant_b: 紧凑布局（卡片 4 列，突出"高级版"高性价比）
# 分桶比例：50/50（确定性 hash，同一用户永远一致）
AB_EXPERIMENT = "pricing_layout"
AB_VARIANTS = {
    "variant_a": {
        "label": "推荐布局A",
        "layout": "grid-3",
        "highlight_plan": "yiwu_merchant",
        "description": "3列卡片，突出义乌商户专享版",
    },
    "variant_b": {
        "label": "推荐布局B",
        "layout": "grid-4",
        "highlight_plan": "pro",
        "description": "4列紧凑卡片，突出高级版性价比",
    },
}

# 转化事件类型
EVENT_TYPES = {
    "page_view": "Pricing 页面浏览",
    "plan_click": "点击套餐 CTA",
    "checkout_start": "发起结算",
    "checkout_complete": "支付完成",
    "checkout_abandon": "放弃结算",
}


def _deterministic_bucket(key: str, buckets: int = 2) -> int:
    """确定性 hash 分桶：同一 key 永远落到同一桶。

    使用 SHA-256 前 8 字节取模，避免 random 导致同用户每次不同变体。
    """
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(h[:8], 16) % buckets


class BillingService:
    """商业化计费服务 - A/B 测试 + 转化埋点 + 沙箱支付"""

    def __init__(self):
        self.db = get_db()

    # ==================== A/B 测试 ====================

    def get_variant(self, user_email: str = "", session_id: str = "") -> str:
        """获取用户的 A/B 变体分配（确定性，持久化到 DB）。"""
        # 优先用 email 分桶（已登录用户），否则用 session_id（匿名访客）
        bucket_key = user_email or session_id or "anonymous"
        variant_idx = _deterministic_bucket(bucket_key, len(AB_VARIANTS))
        variant_key = list(AB_VARIANTS.keys())[variant_idx]

        # 持久化到 DB（已分配则不覆盖）
        stored = self.db.get_ab_variant(AB_EXPERIMENT, user_email or session_id)
        if stored:
            return stored["variant"]
        return self.db.save_ab_variant(
            AB_EXPERIMENT, user_email or session_id, variant_key
        )

    def get_plans_with_variant(
        self, user_email: str = "", session_id: str = ""
    ) -> Dict[str, Any]:
        """获取套餐列表 + A/B 变体信息。"""
        variant = self.get_variant(user_email, user_email or session_id)
        variant_info = AB_VARIANTS.get(variant, AB_VARIANTS["variant_a"])

        # 根据 variant 调整 highlight
        plans_out = []
        highlight_code = variant_info["highlight_plan"]
        for p in PLANS:
            plan_copy = dict(p)
            plan_copy["highlight"] = p["code"] == highlight_code
            plans_out.append(plan_copy)

        return {
            "plans": plans_out,
            "variant": variant,
            "variant_label": variant_info["label"],
            "layout": variant_info["layout"],
            "experiment": AB_EXPERIMENT,
        }

    # ==================== 转化埋点 ====================

    def track(
        self,
        event_type: str,
        user_email: str = "",
        plan_code: str = "",
        variant: str = "",
        session_id: str = "",
        metadata: Optional[Dict] = None,
    ) -> int:
        """记录转化事件。"""
        if event_type not in EVENT_TYPES:
            logger.warning("未知转化事件类型: %s", event_type)
        return self.db.track_event(
            event_type, user_email, plan_code, variant, session_id, metadata
        )

    def get_funnel_summary(self, hours: int = 24) -> Dict[str, Any]:
        """获取漏斗汇总（最近 N 小时）。"""
        events = self.db.get_events_summary(hours=hours)
        summary = {et: 0 for et in EVENT_TYPES}
        for e in events:
            summary[e["event_type"]] = e["cnt"]

        page_views = summary.get("page_view", 0)
        checkout_starts = summary.get("checkout_start", 0)
        completions = summary.get("checkout_complete", 0)

        return {
            "events": summary,
            "conversion_rate": round(completions / page_views * 100, 2)
            if page_views
            else 0.0,
            "checkout_rate": round(checkout_starts / page_views * 100, 2)
            if page_views
            else 0.0,
            "payment_rate": round(completions / checkout_starts * 100, 2)
            if checkout_starts
            else 0.0,
            "total_events": sum(summary.values()),
            "hours": hours,
        }

    # ==================== 沙箱支付 ====================

    def create_checkout(
        self,
        user_email: str,
        plan_code: str,
        pay_method: str = "alipay_sandbox",
    ) -> Dict[str, Any]:
        """创建支付订单（沙箱模式）。

        沙箱支付流程：
          1. 前端 POST /pricing/checkout -> 后端创建订单（status=pending）
          2. 前端跳转/弹出沙箱支付页 -> 用户点"模拟支付"
          3. 前端 POST /pricing/payment-callback -> 后端标记 paid + 创建订阅
          4. 前端展示成功页 + 订单历史
        """
        plan = PLAN_MAP.get(plan_code)
        if not plan:
            return {"success": False, "detail": f"未知套餐: {plan_code}"}

        order_no = f"YW{int(time.time())}{uuid.uuid4().hex[:8].upper()}"
        order = self.db.create_order(
            order_no=order_no,
            user_email=user_email,
            plan_code=plan_code,
            amount_cny=plan["price_cny"],
            provider="sandbox",
            metadata={
                "plan_name": plan["name"],
                "duration_days": plan["duration_days"],
            },
        )

        logger.info(
            "沙箱订单创建: %s 用户=%s 套餐=%s 金额=%.2f",
            order_no,
            user_email,
            plan_code,
            plan["price_cny"],
        )

        return {
            "success": True,
            "order_no": order_no,
            "amount_cny": plan["price_cny"],
            "plan_name": plan["name"],
            "plan_code": plan_code,
            "status": "pending",
            "provider": "sandbox",
            "pay_method": pay_method,
            "pay_url": f"/api/v1/pricing/sandbox-pay/{order_no}",
            "expires_in_seconds": 600,
            "note": "沙箱模式：无需真实付款，点击确认即完成模拟支付",
        }

    def confirm_payment(
        self, order_no: str, user_email: str, pay_method: str = "alipay_sandbox"
    ) -> Dict[str, Any]:
        """确认沙箱支付（模拟回调）。"""
        order = self.db.get_order(order_no)
        if not order:
            return {"success": False, "detail": "订单不存在"}

        if order["user_email"] != user_email:
            return {"success": False, "detail": "订单归属不匹配"}

        if order["status"] == "paid":
            return {
                "success": True,
                "order_no": order_no,
                "detail": "订单已支付",
                "already_paid": True,
            }

        if order["status"] != "pending":
            return {"success": False, "detail": f"订单状态异常: {order['status']}"}

        # 标记支付成功
        self.db.update_order_status(order_no, "paid", pay_method)

        # 创建订阅
        metadata = {}
        try:
            import json as _json

            metadata = _json.loads(order.get("metadata_json") or "{}")
        except (ValueError, TypeError):
            pass

        duration = metadata.get("duration_days", 30)
        plan_code = order["plan_code"]
        sub = self.db.create_subscription(
            user_email, plan_code, order_no, duration_days=duration
        )

        # 埋点：支付完成
        self.track(
            "checkout_complete", user_email, plan_code, "", "", {"order_no": order_no}
        )

        logger.info("沙箱支付成功: %s 用户=%s 套餐=%s", order_no, user_email, plan_code)

        return {
            "success": True,
            "order_no": order_no,
            "status": "paid",
            "plan_code": plan_code,
            "plan_name": metadata.get(
                "plan_name", PLAN_MAP.get(plan_code, {}).get("name", "")
            ),
            "subscription_id": sub.get("id"),
            "expires_at": sub.get("expires_at"),
        }

    def get_orders(self, user_email: str) -> List[Dict[str, Any]]:
        """获取用户订单列表。"""
        return self.db.list_orders(user_email)

    def get_subscription(self, user_email: str) -> Optional[Dict[str, Any]]:
        """获取用户当前有效订阅。"""
        return self.db.get_subscription(user_email)


# 全局实例
billing_service = BillingService()
