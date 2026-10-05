import os


def _build_database_url() -> str:
    explicit = os.getenv("DATABASE_URL")
    if explicit:
        return explicit
    host = os.getenv("DB_HOST")
    if not host:
        # 本地开发/测试默认使用 SQLite，容器内通过 DB_HOST 指向 PostgreSQL
        return os.getenv("SQLITE_URL", "sqlite:///./fire_inspect.db")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "app_db")
    user = os.getenv("DB_USER", "app_user")
    password = os.getenv("DB_PASSWORD", "app_password")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"


class Settings:
    """全局配置：环境变量经此处被中间件/服务/请求封装共同读取。"""

    APP_NAME = "消防设施巡检维保平台"
    DATABASE_URL = _build_database_url()
    JWT_SECRET = os.getenv("JWT_SECRET", "local-dev-secret")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_TTL_MINUTES = int(os.getenv("ACCESS_TOKEN_TTL_MINUTES", "720"))
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "240"))
    LOGIN_RATE_LIMIT_PER_MINUTE = int(os.getenv("LOGIN_RATE_LIMIT_PER_MINUTE", "12"))


settings = Settings()
