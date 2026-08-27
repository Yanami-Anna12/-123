"""一键运行爬虫流水线：
抓取 Hacker News → 存 JSON → 写 MySQL → 切分 → Embedding → 写 Milvus。

用法：python scripts/run_crawler.py --limit 20
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.crawler.hacker_news import (  # noqa: E402
    embed_chunks,
    get_mysql_statistics,
    get_news_list,
    save_json,
    save_to_milvus,
    save_to_mysql,
    split_new,
)


def main():
    parser = argparse.ArgumentParser(description="Hacker News 采集流水线")
    parser.add_argument("--limit", type=int, default=20, help="抓取条数（默认 20）")
    args = parser.parse_args()

    print("开始采集...")
    news_list = get_news_list(limit=args.limit)
    print(f"抓取到 {len(news_list)} 条新闻")

    save_json(news_list)
    ok, err = save_to_mysql(news_list)
    print(f"MySQL 保存成功 {ok} 条，失败 {err} 条")

    chunks = split_new(news_list)
    embedded = embed_chunks(chunks)
    milvus_count = save_to_milvus(embedded)
    print(f"Milvus 写入 {milvus_count} 个片段")

    total, hn_count = get_mysql_statistics()
    print(f"数据库统计：总 {total} 条，Hacker News {hn_count} 条")


if __name__ == "__main__":
    main()
