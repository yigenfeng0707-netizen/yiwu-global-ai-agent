"""测试数据库模块"""

import os
import time
import pytest
import tempfile
from app.db.database import Database


@pytest.fixture
def db():
    """创建临时测试数据库"""
    fd, path = tempfile.mkstemp(suffix=".db")
    database = Database(db_path=path)
    yield database
    try:
        os.close(fd)
        os.unlink(path)
    except Exception:
        pass


class TestUserManagement:
    def test_create_user(self, db):
        user_id = db.create_user("test@example.com", "hash123", "TestCo")
        assert user_id is not None
        assert user_id > 0

    def test_create_duplicate_user(self, db):
        db.create_user("dup@example.com", "hash1")
        result = db.create_user("dup@example.com", "hash2")
        assert result is None

    def test_get_user_by_email(self, db):
        db.create_user("find@example.com", "hash123", "FindCo")
        user = db.get_user_by_email("find@example.com")
        assert user is not None
        assert user["email"] == "find@example.com"
        assert user["company"] == "FindCo"

    def test_get_nonexistent_user(self, db):
        user = db.get_user_by_email("noone@example.com")
        assert user is None

    def test_update_last_login(self, db):
        db.create_user("login@example.com", "hash1")
        db.update_last_login("login@example.com")
        user = db.get_user_by_email("login@example.com")
        assert user["last_login"] is not None

    def test_get_user_count(self, db):
        assert db.get_user_count() == 0
        db.create_user("a@example.com", "h1")
        db.create_user("b@example.com", "h2")
        assert db.get_user_count() == 2


class TestChatSessions:
    def test_save_and_get_messages(self, db):
        db.save_chat_message("sess1", "user", "你好", category="玩具")
        db.save_chat_message("sess1", "bot", "你好！有什么可以帮你的？")
        messages = db.get_chat_history("sess1")
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "bot"

    def test_session_count(self, db):
        db.save_chat_message("s1", "user", "msg1")
        db.save_chat_message("s2", "user", "msg2")
        assert db.get_session_count() == 2

    def test_empty_session(self, db):
        messages = db.get_chat_history("nonexistent")
        assert len(messages) == 0


class TestAPIUsage:
    def test_record_and_stats(self, db):
        db.record_api_usage("/api/v1/market-insight", "GET", 200, 50.5)
        db.record_api_usage("/api/v1/smart-selection", "GET", 200, 30.2)
        stats = db.get_api_usage_stats(hours=1)
        assert stats["total_calls"] == 2
        assert stats["avg_duration_ms"] > 0
        assert len(stats["top_endpoints"]) > 0


class TestQueryHistory:
    def test_record_and_get(self, db):
        db.record_query("market_insight", {"category": "玩具"}, "success")
        history = db.get_query_history(limit=10)
        assert len(history) == 1
        assert history[0]["agent_name"] == "market_insight"

    def test_filter_by_user(self, db):
        db.record_query("agent1", {}, user_email="user@test.com")
        db.record_query("agent2", {}, user_email="other@test.com")
        history = db.get_query_history(user_email="user@test.com")
        assert len(history) == 1
        assert history[0]["agent_name"] == "agent1"


# ==================== P3-2：连接池 thread-local 复用 ====================

class TestConnectionPooling:
    """P3-2：_get_conn 用 thread-local 缓存连接，避免每操作新建。"""

    def test_same_thread_reuses_connection(self, db):
        """同线程内多次 _get_conn 返回同一 Connection 对象（复用，非新建）。"""
        c1 = db._get_conn()
        c2 = db._get_conn()
        c3 = db._get_conn()
        assert c1 is c2 is c3

    def test_cross_thread_isolation(self, db):
        """不同线程拿到不同 Connection（sqlite3 非线程安全，必须隔离）。"""
        import threading
        main_conn = db._get_conn()
        other_conn_holder = {}

        def worker():
            other_conn_holder["conn"] = db._get_conn()

        t = threading.Thread(target=worker)
        t.start()
        t.join(timeout=5)
        assert "conn" in other_conn_holder
        assert other_conn_holder["conn"] is not main_conn

    def test_close_all_releases_connection(self, db):
        """close_all 后下次 _get_conn 应新建（旧连接已释放）。"""
        c1 = db._get_conn()
        db.close_all()
        c2 = db._get_conn()
        assert c1 is not c2

    def test_operations_still_work_after_close_all(self, db):
        """close_all 后后续操作应自动重连，功能不受影响（WAL 持久化）。"""
        db.create_user("pool@test.com", "hash", "PoolCo")
        db.close_all()
        user = db.get_user_by_email("pool@test.com")
        assert user is not None
        assert user["company"] == "PoolCo"


# ==================== P3-2：LLM 日计数 SQLite 承载 ====================

class TestLLMDailyCount:
    """P3-2：llm_daily_count 表 get/set/incr 原子性与按日期隔离。"""

    def test_get_missing_date_returns_zero(self, db):
        assert db.get_llm_daily_count("1999-01-01") == 0

    def test_set_then_get(self, db):
        db.set_llm_daily_count("2026-09-09", 42)
        assert db.get_llm_daily_count("2026-09-09") == 42

    def test_set_overwrites(self, db):
        db.set_llm_daily_count("2026-09-09", 10)
        db.set_llm_daily_count("2026-09-09", 25)
        assert db.get_llm_daily_count("2026-09-09") == 25

    def test_incr_from_zero(self, db):
        assert db.incr_llm_daily_count("2026-09-10") == 1
        assert db.incr_llm_daily_count("2026-09-10") == 2
        assert db.incr_llm_daily_count("2026-09-10") == 3
        assert db.get_llm_daily_count("2026-09-10") == 3

    def test_incr_after_set(self, db):
        db.set_llm_daily_count("2026-09-11", 100)
        assert db.incr_llm_daily_count("2026-09-11") == 101

    def test_dates_isolated(self, db):
        """不同日期计数互不干扰。"""
        db.set_llm_daily_count("2026-09-09", 5)
        db.set_llm_daily_count("2026-09-10", 7)
        assert db.get_llm_daily_count("2026-09-09") == 5
        assert db.get_llm_daily_count("2026-09-10") == 7
        assert db.incr_llm_daily_count("2026-09-09") == 6
        assert db.get_llm_daily_count("2026-09-10") == 7  # 未受影响
