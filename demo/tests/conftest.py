"""测试配置与共享fixtures"""

import os
import sys
import pytest
import tempfile
from pathlib import Path

# 确保测试时数据库使用临时文件
_test_db_fd, _test_db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_PATH"] = _test_db_path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    """测试结束后清理临时数据库"""
    yield
    try:
        os.close(_test_db_fd)
        os.unlink(_test_db_path)
    except Exception:
        pass


@pytest.fixture
def test_db():
    """创建临时测试数据库"""
    from app.db.database import Database
    db = Database(db_path=_test_db_path)
    yield db


@pytest.fixture
def anyio_backend():
    return "asyncio"
