from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config.settings import settings

# 数据库连接串
DATABASE_URL = (
    f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # 取连接前先探活，防止连接断开报错
    pool_recycle=3600,    # 连接 1 小时回收一次
    echo=False,           # 改成 True 会打印所有 SQL，调试用
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_db():
    """FastAPI 依赖：每个请求开一个会话，用完自动关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()