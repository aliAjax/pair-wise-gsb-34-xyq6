"""数据库引擎与会话管理。"""

from collections.abc import Iterator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from src.config.settings import settings

_IS_SQLITE = settings.DATABASE_URL.startswith("sqlite")
_engine_options: dict = {"future": True}
if _IS_SQLITE:
    # SQLite：允许跨线程连接，等待写锁最多 30s，支撑两名巡检员并发提交
    _engine_options["connect_args"] = {"check_same_thread": False, "timeout": 30}

engine = create_engine(settings.DATABASE_URL, **_engine_options)

if _IS_SQLITE:
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        try:
            # 确保该连接在 WAL 模式下；已是 wal 时查询不加锁，万一被外部改回 delete 则重新切换
            cursor.execute("PRAGMA busy_timeout=30000")
            mode = cursor.execute("PRAGMA journal_mode").fetchone()[0]
            if mode != "wal":
                cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    from src.models.entities import Base

    Base.metadata.create_all(bind=engine)
    if _IS_SQLITE:
        # 幂等确认 WAL（journal_mode 是数据库持久属性，已是 wal 时该查询不加写锁）
        with engine.begin() as conn:
            mode = conn.execute(text("PRAGMA journal_mode=WAL")).scalar()
            if mode != "wal":
                raise RuntimeError(f"SQLite 无法启用 WAL（当前 {mode}），并发提交可能受限")


def get_session() -> Iterator[Session]:
    """FastAPI 依赖：每个请求一个事务，写操作在 service 内 commit。"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
