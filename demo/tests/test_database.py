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
