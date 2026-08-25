import hashlib
import json
import re
import time
from datetime import datetime
from pathlib import Path

import requests
from sqlalchemy import text

from database.mysql import SessionLocal


# ============================================================
# Hacker News API 配置
# ============================================================

BASE_URL = "https://hacker-news.firebaseio.com/v0"


# ============================================================
# 数据保存目录
# ============================================================

DATA_DIR = Path("../data")

DATA_FILE = DATA_DIR / "hacker_news.json"


# ============================================================
# 请求头
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/137.0.0.0 "
        "Safari/537.36"
    ),

    "Accept": "application/json",

    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


# ============================================================
# 获取 Top Stories ID
# ============================================================

def get_top_story_ids(limit: int = 50) -> list[int]:
    """
    获取 Hacker News Top Stories ID
    """

    url = f"{BASE_URL}/topstories.json"

    print("正在获取 Hacker News 热门新闻 ID...")

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20,
    )

    print(
        f"请求状态码: "
        f"{response.status_code}"
    )

    response.raise_for_status()

    story_ids = response.json()

    if not isinstance(story_ids, list):
        raise ValueError(
            "Hacker News API 返回的数据格式错误"
        )

    return story_ids[:limit]


# ============================================================
# 获取单条新闻
# ============================================================

def get_story(story_id: int) -> dict | None:
    """
    根据 Hacker News ID 获取新闻详情
    """

    url = (
        f"{BASE_URL}/item/"
        f"{story_id}.json"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()

    return data


# ============================================================
# 清理文本
# ============================================================

def clean_text(text: str | None) -> str:
    """
    清理 HTML 标签和多余空白
    """

    if not text:
        return ""

    # 去掉 HTML 标签
    text = re.sub(
        r"<[^>]+>",
        " ",
        text,
    )

    # HTML 实体简单处理
    text = (
        text.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#x27;", "'")
    )

    # 合并空白
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# Unix 时间戳 → datetime
# ============================================================

def convert_timestamp(
    timestamp: int | None,
) -> datetime | None:
    """
    Hacker News 时间戳转换成 Python datetime
    """

    if not timestamp:
        return None

    try:

        return datetime.fromtimestamp(
            timestamp
        )

    except Exception:

        return None


# ============================================================
# 构造新闻正文
# ============================================================

def build_content(
    data: dict,
) -> str:
    """
    构造用于数据库和后续 RAG 的文本
    """

    title = clean_text(
        data.get("title")
    )

    author = clean_text(
        data.get("by")
    )

    score = data.get(
        "score",
        0,
    )

    comments = data.get(
        "descendants",
        0,
    )

    raw_text = data.get(
        "text",
        "",
    )

    article_text = clean_text(
        raw_text
    )

    content_parts = [
        f"标题：{title}",
        "来源：Hacker News",
        f"作者：{author}",
        f"评分：{score}",
        f"评论数：{comments}",
    ]

    if article_text:

        content_parts.extend(
            [
                "",
                "正文：",
                article_text,
            ]
        )

    return "\n".join(
        content_parts
    )


# ============================================================
# 生成内容 Hash
# ============================================================

def generate_content_hash(
    content: str,
) -> str:
    """
    使用 SHA256 生成内容指纹
    """

    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


# ============================================================
# 获取新闻列表
# ============================================================

def get_news_list(
    limit: int = 50,
) -> list[dict]:
    """
    获取并处理 Hacker News
    """

    story_ids = get_top_story_ids(
        limit
    )

    print(
        f"获取到新闻 ID："
        f"{len(story_ids)}"
    )

    print()

    news_list = []

    for index, story_id in enumerate(
        story_ids,
        start=1,
    ):

        try:

            # ------------------------------------------------
            # 获取新闻详情
            # ------------------------------------------------

            data = get_story(
                story_id
            )

            # ------------------------------------------------
            # 数据为空
            # ------------------------------------------------

            if not data:
                print(
                    f"[{index:02d}] "
                    f"ID={story_id} "
                    f"数据为空"
                )
                continue

            # ------------------------------------------------
            # 只处理 Story
            # ------------------------------------------------

            if data.get("type") != "story":

                print(
                    f"[{index:02d}] "
                    f"ID={story_id} "
                    f"跳过："
                    f"{data.get('type')}"
                )

                continue

            # ------------------------------------------------
            # 获取标题
            # ------------------------------------------------

            title = clean_text(
                data.get("title")
            )

            if not title:

                print(
                    f"[{index:02d}] "
                    f"ID={story_id} "
                    f"跳过：没有标题"
                )

                continue

            # ------------------------------------------------
            # 获取 URL
            # ------------------------------------------------

            url = clean_text(
                data.get("url")
            )

            # ------------------------------------------------
            # Ask HN 没有外部 URL
            # 使用 Hacker News 自己的链接
            # ------------------------------------------------

            if not url:

                url = (
                    "https://news.ycombinator.com/"
                    f"item?id={story_id}"
                )

            # ------------------------------------------------
            # 构造正文
            # ------------------------------------------------

            content = build_content(
                data
            )

            # ------------------------------------------------
            # 内容 Hash
            # ------------------------------------------------

            content_hash = (
                generate_content_hash(
                    content
                )
            )

            # ------------------------------------------------
            # 发布时间
            # ------------------------------------------------

            publish_time = (
                convert_timestamp(
                    data.get("time")
                )
            )

            # ------------------------------------------------
            # 作者
            # ------------------------------------------------

            author = clean_text(
                data.get("by")
            )

            # ------------------------------------------------
            # 评分
            # ------------------------------------------------

            score = data.get(
                "score",
                0,
            )

            # ------------------------------------------------
            # 评论数
            # ------------------------------------------------

            comments = data.get(
                "descendants",
                0,
            )

            # ------------------------------------------------
            # 统一数据结构
            # ------------------------------------------------

            news = {

                "source_id": story_id,

                "title": title,

                "source": "Hacker News",

                "author": author,

                "score": score,

                "comments": comments,

                "url": url,

                "content": content,

                "category": "科技情报",

                "publish_time": publish_time,

                "content_hash": content_hash,
            }

            news_list.append(
                news
            )

            print(
                f"[{len(news_list):02d}] "
                f"{title[:70]}"
            )

            # ------------------------------------------------
            # 稍微降低请求频率
            # ------------------------------------------------

            time.sleep(0.05)

        except requests.RequestException as e:

            print(
                f"[{index:02d}] "
                f"ID={story_id} "
                f"网络请求失败："
                f"{e}"
            )

        except Exception as e:

            print(
                f"[{index:02d}] "
                f"ID={story_id} "
                f"处理失败："
                f"{e}"
            )

    return news_list


# ============================================================
# 保存 JSON
# ============================================================

def save_json(
    news_list: list[dict],
) -> None:
    """
    保存 JSON 备份
    """

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_data = []

    for news in news_list:

        item = news.copy()

        publish_time = item.get(
            "publish_time"
        )

        if isinstance(
            publish_time,
            datetime,
        ):

            item["publish_time"] = (
                publish_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

        json_data.append(
            item
        )

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            json_data,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=" * 60)
    print(
        "JSON 备份完成"
    )
    print(
        f"文件：{DATA_FILE}"
    )
    print(
        f"数据数量："
        f"{len(json_data)}"
    )
    print("=" * 60)


# ============================================================
# 保存 MySQL
# ============================================================

def save_to_mysql(
    news_list: list[dict],
) -> tuple[int, int]:
    """
    将新闻写入 MySQL

    返回：
        insert/update 处理数量
        error 数量
    """

    if not news_list:

        print(
            "没有数据需要保存到 MySQL"
        )

        return 0, 0

    db = SessionLocal()

    success_count = 0

    error_count = 0

    try:

        # ----------------------------------------------------
        # SQL
        # ----------------------------------------------------

        sql = text(
            """
            INSERT INTO news (
                source_id,
                title,
                source,
                author,
                score,
                comments,
                url,
                content,
                category,
                publish_time,
                content_hash
            )
            VALUES (
                :source_id,
                :title,
                :source,
                :author,
                :score,
                :comments,
                :url,
                :content,
                :category,
                :publish_time,
                :content_hash
            )

            ON DUPLICATE KEY UPDATE

                title = VALUES(title),

                author = VALUES(author),

                score = VALUES(score),

                comments = VALUES(comments),

                url = VALUES(url),

                content = VALUES(content),

                category = VALUES(category),

                publish_time =
                    VALUES(publish_time),

                content_hash =
                    VALUES(content_hash)
            """
        )

        # ----------------------------------------------------
        # 批量执行
        # ----------------------------------------------------

        for news in news_list:

            try:

                db.execute(
                    sql,
                    news,
                )

                success_count += 1

            except Exception as e:

                error_count += 1

                print(
                    "MySQL 保存失败："
                    f"{news.get('title', '')[:50]}"
                )

                print(
                    f"错误：{e}"
                )

        # ----------------------------------------------------
        # 提交
        # ----------------------------------------------------

        db.commit()

        print()
        print("=" * 60)
        print(
            "MySQL 保存完成"
        )
        print(
            f"成功：{success_count}"
        )
        print(
            f"失败：{error_count}"
        )
        print("=" * 60)

    except Exception as e:

        db.rollback()

        print()
        print("=" * 60)
        print(
            "MySQL 事务失败"
        )
        print(
            f"错误：{e}"
        )
        print("=" * 60)

    finally:

        db.close()

    return success_count, error_count


# ============================================================
# 查询数据库统计
# ============================================================

def get_mysql_statistics():
    """
    查询数据库中的新闻统计
    """

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # 总数量
        # ----------------------------------------------------

        result = db.execute(
            text(
                """
                SELECT COUNT(*)
                FROM news
                """
            )
        )

        total = result.scalar()

        # ----------------------------------------------------
        # Hacker News 数量
        # ----------------------------------------------------

        result = db.execute(
            text(
                """
                SELECT COUNT(*)
                FROM news
                WHERE source = 'Hacker News'
                """
            )
        )

        hacker_news_count = (
            result.scalar()
        )

        return (
            total,
            hacker_news_count,
        )

    except Exception as e:

        print(
            f"数据库统计失败：{e}"
        )

        return (
            None,
            None,
        )

    finally:

        db.close()


# ============================================================
# 主程序
# ============================================================

def main():

    print()
    print("=" * 60)
    print(
        "Hacker News 新闻采集器启动"
    )
    print("=" * 60)
    print()

    try:

        # ====================================================
        # 第一步：获取新闻
        # ====================================================

        news_list = get_news_list(
            limit=50
        )

        print()
        print("=" * 60)
        print(
            f"提取到有效新闻："
            f"{len(news_list)} 条"
        )
        print("=" * 60)

        # ====================================================
        # 第二步：保存 JSON
        # ====================================================

        save_json(
            news_list
        )

        # ====================================================
        # 第三步：保存 MySQL
        # ====================================================

        save_to_mysql(
            news_list
        )

        # ====================================================
        # 第四步：数据库统计
        # ====================================================

        total, hacker_count = (
            get_mysql_statistics()
        )

        print()
        print("=" * 60)
        print(
            "数据库统计"
        )
        print("=" * 60)

        if total is not None:

            print(
                f"新闻总数量："
                f"{total}"
            )

            print(
                f"Hacker News："
                f"{hacker_count}"
            )

        print("=" * 60)

        print()
        print(
            "🎉 新闻采集任务完成！"
        )

    except requests.RequestException as e:

        print()
        print("=" * 60)
        print(
            "网络请求失败"
        )
        print(
            f"错误：{e}"
        )
        print("=" * 60)

    except Exception as e:

        print()
        print("=" * 60)
        print(
            "程序运行失败"
        )
        print(
            f"错误：{e}"
        )
        print("=" * 60)


# ============================================================
# 程序入口
# ============================================================

if __name__ == "__main__":

    main()