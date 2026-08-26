"""MySQL 数据库：只有一张 news 表，结构对齐成员A 的 news.sql。"""
import json
from pathlib import Path

import pymysql

import config

# 建表语句（与 news.sql 的字段一一对应）
_SCHEMA = """
CREATE TABLE IF NOT EXISTS news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_id INT,
    title VARCHAR(512),
    source VARCHAR(255),
    author VARCHAR(255),
    score INT,
    comments INT,
    url VARCHAR(768),
    content LONGTEXT,
    category VARCHAR(100),
    publish_time DATETIME,
    content_hash VARCHAR(64),
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_news_content_hash (content_hash)
)
"""

_database_ready = False


def _ensure_database():
    """第一次连接前确保业务数据库存在。"""
    global _database_ready
    if _database_ready:
        return

    conn = pymysql.connect(
        host=config.MYSQL_HOST,
        port=config.MYSQL_PORT,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{config.MYSQL_DATABASE}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
        _database_ready = True
    finally:
        conn.close()


def _conn():
    _ensure_database()
    conn = pymysql.connect(
        host=config.MYSQL_HOST,
        port=config.MYSQL_PORT,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE,
        cursorclass=pymysql.cursors.DictCursor,
    )
    with conn.cursor() as cursor:
        cursor.execute(_SCHEMA)  # 表不存在则自动创建
    conn.commit()
    return conn


def init_db():
    """显式初始化数据库（可选，因为 _conn 会自动建表）。"""
    _conn().close()


def seed_from_json(json_path):
    """把爬虫产出的 JSON（如 hacker_news.json）导入 news 表，返回导入条数。"""
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    conn = _conn()
    try:
        with conn.cursor() as cursor:
            for item in data:
                cursor.execute(
                    """
                    REPLACE INTO news
                        (source_id, title, source, author, score, comments, url,
                         content, category, publish_time, content_hash)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        item.get("source_id"),
                        item.get("title"),
                        item.get("source"),
                        item.get("author"),
                        item.get("score"),
                        item.get("comments"),
                        item.get("url"),
                        item.get("content"),
                        item.get("category"),
                        item.get("publish_time"),
                        item.get("content_hash"),
                    ),
                )
        conn.commit()
    finally:
        conn.close()
    return len(data)


def query_news(keyword=None, category=None, source=None, start=None, end=None, limit=10):
    """按条件查询 news 表，返回字典列表（按发布时间倒序）。"""
    sql = (
        "SELECT id, title, source, author, score, comments, url, category, publish_time "
        "FROM news"
    )
    # 动态拼接 WHERE 条件；用 %s 占位符 + 参数列表传参，防止 SQL 注入
    where, params = [], []
    if keyword:
        where.append("(title LIKE %s OR content LIKE %s)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    if category:
        where.append("category = %s")
        params.append(category)
    if source:
        where.append("source = %s")
        params.append(source)
    if start:
        where.append("publish_time >= %s")
        params.append(start)
    if end:
        where.append("publish_time <= %s")
        params.append(end)
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY publish_time DESC LIMIT %s"
    params.append(int(limit))

    conn = _conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
    finally:
        conn.close()
    return rows


def count_news():
    conn = _conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS n FROM news")
            row = cursor.fetchone()
            return row["n"]
    finally:
        conn.close()
