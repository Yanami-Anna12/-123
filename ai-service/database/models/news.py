from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, String, Text

from database.db import Base


class News(Base):
    __tablename__ = "news"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    source = Column(String(100))
    url = Column(String(500), unique=True, nullable=False)
    content = Column(Text)
    category = Column(String(50))
    publish_time = Column(DateTime)
    content_hash = Column(String(64), index=True)
    create_time = Column(DateTime, default=datetime.now)