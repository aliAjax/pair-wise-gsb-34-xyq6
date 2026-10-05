import os
import tempfile

import pytest
from fastapi.testclient import TestClient

# 测试使用独立临时 SQLite 库；StaticPool 让 TestClient 工作线程与主线程共用同一连接，
# 避免 drop_all 重建时 SQLAlchemy 连接池里的旧连接持有文件锁。
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"
# 测试中关闭接口限流，避免连续用例触发滑动窗口 429。
os.environ["RATE_LIMIT_PER_MINUTE"] = "100000000"

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

import src.db.session as db_session  # noqa: E402

test_engine = create_engine(
    f"sqlite:///{_tmp.name}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
db_session.engine = test_engine
db_session.SessionLocal.configure(bind=test_engine)

from src.db.session import Base, SessionLocal  # noqa: E402
from src.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    Base.metadata.create_all(bind=test_engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth(client):
    def _login(username):
        resp = client.post("/api/auth/login", json={"username": username, "password": username})
        assert resp.status_code == 200, resp.text
        token = resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _login


@pytest.fixture(autouse=True)
def reset_database():
    # 每个用例前清空全部表并重建（含自增序列归零），再重新播种演示数据。
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    from src.seed import seed_database

    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield
