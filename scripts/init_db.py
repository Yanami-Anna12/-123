"""初始化数据库：建表 + 导入 data/hacker_news.json。

用法：python scripts/init_db.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config.settings import settings  # noqa: E402
from app.database import repo  # noqa: E402


def main():
    print("=" * 50)
    print("初始化数据库...")
    repo.init_db()
    print("表结构就绪")

    json_path = settings.ROOT / "data" / "hacker_news.json"
    if json_path.exists():
        count = repo.seed_from_json(str(json_path))
        print(f"已导入 {count} 条新闻")

    print(f"新闻总数: {repo.count_news()}")
    print("=" * 50)


if __name__ == "__main__":
    main()
