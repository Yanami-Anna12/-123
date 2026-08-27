from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, String, Text

from app.database.db import Base


class Company(Base):
    __tablename__ = "company"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    website = Column(String(255))
    introduction = Column(Text)
    location = Column(String(100))
    create_time = Column(DateTime, default=datetime.now)
