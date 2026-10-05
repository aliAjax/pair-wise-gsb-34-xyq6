import os

PORT = int(os.getenv("PORT", "8000"))

DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "app_db")
DB_USER = os.getenv("DB_USER", "app_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "app_password")

# 生产/容器内走 PostgreSQL；本地缺依赖或单测时回退到本地 SQLite 文件库，保证流程可运行。
if DB_HOST:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    )
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fire_inspect.db")

JWT_SECRET = os.getenv("JWT_SECRET", "local-dev-secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))

# 接口限流：同 IP 每分钟最大请求数。
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
