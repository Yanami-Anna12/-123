"""统一的数据访问层（SQLAlchemy）：查询 / 导入 news 表。

成员A 负责表结构（sql/news.sql），成员B 的 MCP 工具、成员C 的接口
都通过这里访问同一张 news 表，避免各写一套。
"""
from datetime import datetime

from sqlalchemy import func, or_

from app.database.db import SessionLocal
from app.database.models.news import News


def _parse_time(value):
    """把字符串/时间戳统一成 datetime（容忍空值）。"""
    if value is None or isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value)
    text = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def init_db():
    """创建所有表（幂等：已存在不会重复建）。"""
    from app.database.db import Base, engine

    Base.metadata.create_all(bind=engine)


def seed_from_json(json_path):
    """把爬虫产出的 JSON（data/hacker_news.json）导入 news 表，返回导入条数。

    以 URL 为去重依据：已存在则更新，不存在则插入。
    """
    import json
    from pathlib import Path

    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    db = SessionLocal()
    try:
        for item in data:
            fields = {
                "source_id": item.get("source_id"),
                "title": item.get("title", ""),
                "source": item.get("source", "Hacker News"),
                "author": item.get("author"),
                "score": item.get("score"),
                "comments": item.get("comments"),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
                "category": item.get("category"),
                "publish_time": _parse_time(item.get("publish_time")),
                "content_hash": item.get("content_hash"),
            }
            existing = db.query(News).filter(News.url == fields["url"]).first()
            if existing:
                for key, value in fields.items():
                    setattr(existing, key, value)
            else:
                db.add(News(**fields))
        db.commit()
    finally:
        db.close()
    return len(data)


def query_news(keyword=None, category=None, source=None, start=None, end=None, limit=10):
    """按条件查询 news 表，返回字典列表（按发布时间倒序）。"""
    db = SessionLocal()
    try:
        query = db.query(News)
        if keyword:
            like = f"%{keyword}%"
            query = query.filter(or_(News.title.like(like), News.content.like(like)))
        if category:
            query = query.filter(News.category == category)
        if source:
            query = query.filter(News.source == source)
        if start:
            query = query.filter(News.publish_time >= _parse_time(start))
        if end:
            query = query.filter(News.publish_time <= _parse_time(end))

        rows = query.order_by(News.publish_time.desc()).limit(int(limit)).all()
        return [
            {
                "id": n.id,
                "title": n.title,
                "source": n.source,
                "author": n.author,
                "score": n.score,
                "comments": n.comments,
                "url": n.url,
                "category": n.category,
                "publish_time": str(n.publish_time) if n.publish_time else None,
            }
            for n in rows
        ]
    finally:
        db.close()


def count_news():
    """新闻总数；数据库不可用时返回 0（避免接口直接报错）。"""
    db = SessionLocal()
    try:
        return db.query(func.count(News.id)).scalar() or 0
    except Exception:
        return 0
    finally:
        db.close()
