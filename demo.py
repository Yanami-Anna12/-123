"""命令行演示：初始化数据库 → 文档入库 → Agent 问答。"""
import argparse
from pathlib import Path

import config
import db


def setup():
    """初始化并导入新闻数据。"""
    db.init_db()
    json_path = Path(config.ROOT) / "data" / "hacker_news.json"
    if json_path.exists():
        n = db.seed_from_json(str(json_path))
        print(f"[DB] 已导入 {n} 条新闻")
    print(f"[DB] 新闻总数: {db.count_news()}")


def main():
    # 三种用法：--setup 初始化数据库 / --ingest 文档入库 / 直接提问走 Agent
    parser = argparse.ArgumentParser(description="企业智能情报 Agent（LangGraph + MCP）")
    parser.add_argument("question", nargs="?", help="要问的问题")
    parser.add_argument("--setup", action="store_true", help="初始化并导入新闻数据")
    parser.add_argument("--ingest", nargs="*", help="要入库的文档路径")
    args = parser.parse_args()

    if args.setup:
        setup()
        return

    if args.ingest:
        import rag

        n = rag.ingest(args.ingest)
        print(f"[RAG] 已入库 {n} 个片段")
        return

    if not args.question:
        parser.error("请提供问题，或用 --setup / --ingest")

    import agent

    answer, trace = agent.ask(args.question)
    if trace:
        print("工具调用:", " -> ".join(trace))
    print("回答:", answer)


if __name__ == "__main__":
    main()
