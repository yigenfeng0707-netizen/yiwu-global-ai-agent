"""义乌小商品出海智能体 - SQLite数据库持久化层"""

import os
import sqlite3
import time
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List


DB_PATH = os.getenv("DATABASE_PATH", str(Path(__file__).resolve().parent.parent.parent / "data" / "app.db"))


class Database:
    """SQLite数据库 - 用户管理、会话存储、API用量追踪、查询历史"""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self):
        """初始化数据库表"""
        with self._get_conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    company TEXT DEFAULT '',
                    role TEXT DEFAULT 'user',
                    created_at REAL NOT NULL,
                    last_login REAL,
                    is_active INTEGER DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_email TEXT,
                    category TEXT DEFAULT '',
                    language TEXT DEFAULT 'zh',
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    message_count INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    emotion TEXT,
                    created_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT,
                    endpoint TEXT NOT NULL,
                    method TEXT DEFAULT 'GET',
                    status_code INTEGER DEFAULT 200,
                    duration_ms REAL,
                    created_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS query_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT,
                    agent_name TEXT NOT NULL,
                    params_json TEXT,
                    result_summary TEXT,
                    created_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS real_data_cache (
                    source TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    is_real INTEGER DEFAULT 0,
                    fetched_at REAL DEFAULT 0,
                    source_url TEXT DEFAULT '',
                    error TEXT DEFAULT '',
                    updated_at REAL NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
                CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_messages(session_id);
                CREATE INDEX IF NOT EXISTS idx_api_usage_time ON api_usage(created_at);
                CREATE INDEX IF NOT EXISTS idx_query_history_time ON query_history(created_at);
                CREATE INDEX IF NOT EXISTS idx_real_data_updated ON real_data_cache(updated_at);
            """)

    # ==================== 用户管理 ====================

    def create_user(self, email: str, password_hash: str, company: str = "") -> Optional[int]:
        """创建用户，返回用户ID；邮箱已存在返回None"""
        try:
            with self._get_conn() as conn:
                cursor = conn.execute(
                    "INSERT INTO users (email, password_hash, company, created_at) VALUES (?, ?, ?, ?)",
                    (email, password_hash, company, time.time()),
                )
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取用户"""
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            if row:
                return dict(row)
            return None

    def update_last_login(self, email: str):
        """更新最后登录时间"""
        with self._get_conn() as conn:
            conn.execute("UPDATE users SET last_login = ? WHERE email = ?", (time.time(), email))

    def get_user_count(self) -> int:
        """获取用户总数"""
        with self._get_conn() as conn:
            return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    # ==================== 会话管理 ====================

    def save_chat_message(self, session_id: str, role: str, content: str,
                          emotion: str = "", category: str = "", language: str = "zh",
                          user_email: str = ""):
        """保存聊天消息"""
        now = time.time()
        with self._get_conn() as conn:
            # 确保会话记录存在
            existing = conn.execute(
                "SELECT id FROM chat_sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
            if not existing:
                conn.execute(
                    "INSERT INTO chat_sessions (session_id, user_email, category, language, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (session_id, user_email, category, language, now, now),
                )
            # 插入消息
            conn.execute(
                "INSERT INTO chat_messages (session_id, role, content, emotion, created_at) VALUES (?, ?, ?, ?, ?)",
                (session_id, role, content, emotion, now),
            )
            # 更新会话统计
            conn.execute(
                "UPDATE chat_sessions SET updated_at = ?, message_count = message_count + 1 WHERE session_id = ?",
                (now, session_id),
            )

    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取会话聊天历史"""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
                (session_id, limit),
            ).fetchall()
            return [dict(r) for r in reversed(rows)]

    def get_session_count(self) -> int:
        """获取会话总数"""
        with self._get_conn() as conn:
            return conn.execute("SELECT COUNT(*) FROM chat_sessions").fetchone()[0]

    # ==================== API用量追踪 ====================

    def record_api_usage(self, endpoint: str, method: str = "GET", status_code: int = 200,
                         duration_ms: float = 0, user_email: str = ""):
        """记录API调用"""
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO api_usage (user_email, endpoint, method, status_code, duration_ms, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (user_email, endpoint, method, status_code, duration_ms, time.time()),
            )

    def get_api_usage_stats(self, hours: int = 24) -> Dict[str, Any]:
        """获取API使用统计"""
        cutoff = time.time() - (hours * 3600)
        with self._get_conn() as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM api_usage WHERE created_at > ?", (cutoff,)
            ).fetchone()[0]
            by_endpoint = conn.execute(
                "SELECT endpoint, COUNT(*) as cnt FROM api_usage WHERE created_at > ? GROUP BY endpoint ORDER BY cnt DESC LIMIT 10",
                (cutoff,),
            ).fetchall()
            avg_duration = conn.execute(
                "SELECT AVG(duration_ms) FROM api_usage WHERE created_at > ? AND duration_ms > 0",
                (cutoff,),
            ).fetchone()[0] or 0
            return {
                "total_calls": total,
                "period_hours": hours,
                "avg_duration_ms": round(avg_duration, 2),
                "top_endpoints": [{"endpoint": r["endpoint"], "count": r["cnt"]} for r in by_endpoint],
            }

    # ==================== 查询历史 ====================

    def record_query(self, agent_name: str, params: Dict[str, Any], result_summary: str = "",
                     user_email: str = ""):
        """记录Agent查询历史"""
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO query_history (user_email, agent_name, params_json, result_summary, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_email, agent_name, json.dumps(params, ensure_ascii=False), result_summary, time.time()),
            )

    def get_query_history(self, user_email: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        """获取查询历史"""
        with self._get_conn() as conn:
            if user_email:
                rows = conn.execute(
                    "SELECT * FROM query_history WHERE user_email = ? ORDER BY created_at DESC LIMIT ?",
                    (user_email, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM query_history ORDER BY created_at DESC LIMIT ?", (limit,)
                ).fetchall()
            return [dict(r) for r in rows]

    # ==================== 真实数据源缓存（P1-1 ETL） ====================

    def save_real_data(self, result: Dict[str, Any]):
        """UPSERT 一条真实数据源抓取结果（FetchResult.to_dict()）。

        进程重启后可从本表回退到"上次成功值"，避免单次抓取失败导致数据空洞。
        """
        source = result.get("source", "")
        if not source:
            return
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO real_data_cache
                    (source, payload_json, is_real, fetched_at, source_url, error, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source) DO UPDATE SET
                    payload_json = excluded.payload_json,
                    is_real      = excluded.is_real,
                    fetched_at   = excluded.fetched_at,
                    source_url   = excluded.source_url,
                    error        = excluded.error,
                    updated_at   = excluded.updated_at
                """,
                (
                    source,
                    json.dumps(result, ensure_ascii=False),
                    1 if result.get("is_real") else 0,
                    result.get("fetched_at", 0) or 0,
                    result.get("source_url", ""),
                    result.get("error", ""),
                    time.time(),
                ),
            )

    def get_real_data(self, source: str) -> Optional[Dict[str, Any]]:
        """按源标识取最近落库结果（含 payload），无则 None。"""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM real_data_cache WHERE source = ?", (source,)
            ).fetchone()
            if not row:
                return None
            record = dict(row)
            try:
                record["payload"] = json.loads(record.get("payload_json") or "{}")
            except (ValueError, TypeError):
                record["payload"] = {}
            return record

    def get_all_real_data(self) -> List[Dict[str, Any]]:
        """取全部真实数据源缓存（按更新时间倒序），用于 /data-sources 状态汇总。"""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM real_data_cache ORDER BY updated_at DESC"
            ).fetchall()
            out: List[Dict[str, Any]] = []
            for r in rows:
                record = dict(r)
                try:
                    record["payload"] = json.loads(record.get("payload_json") or "{}")
                except (ValueError, TypeError):
                    record["payload"] = {}
                out.append(record)
            return out


# 全局数据库实例（懒加载）
_db_instance: Optional[Database] = None


def get_db() -> Database:
    """获取全局数据库实例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
