from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# ============================================================
# MySQL 配置
# ============================================================

MYSQL_USER = "root"

MYSQL_PASSWORD = "52misaka"

MYSQL_HOST = "localhost"

MYSQL_PORT = 3306

MYSQL_DATABASE = "ai_intelligence"


# ============================================================
# 数据库连接 URL
# ============================================================

DATABASE_URL = (
    f"mysql+pymysql://"
    f"{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/"
    f"{MYSQL_DATABASE}"
    f"?charset=utf8mb4"
)


# ============================================================
# 创建数据库引擎
# ============================================================

engine = create_engine(
    DATABASE_URL,

    # False = 不打印 SQL
    echo=False,

    # 自动检查数据库连接是否有效
    pool_pre_ping=True,

    # 连接池大小
    pool_size=5,

    # 最大溢出连接
    max_overflow=10,
)


# ============================================================
# 创建 Session
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,

    autoflush=False,

    autocommit=False,
)