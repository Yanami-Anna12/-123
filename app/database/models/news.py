from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text

from app.database.db import Base


class News(Base):
    """news 表（字段与成员A 的 sql/news.sql 一一对应）"""

    __tablename__ = "news"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_id = Column(BigInteger, nullable=False)
    title = Column(String(500), nullable=False)
    source = Column(String(100), nullable=False)
    author = Column(String(100))
    score = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    url = Column(String(768), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100))
    publish_time = Column(DateTime)
    content_hash = Column(String(64), index=True)
    create_time = Column(DateTime, default=datetime.now)
