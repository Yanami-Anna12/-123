"""MCP 服务器：把 RAG 检索、新闻查询、统计等能力通过 MCP 协议暴露成工具。

Agent 通过 MCP 客户端（stdio）连接本服务器，调用这些工具。
"""
import json

from fastmcp import FastMCP

import db
import rag

mcp = FastMCP("intel-tools")


# @mcp.tool() 装饰器：被装饰的函数会自动注册成 MCP 工具，
# Agent 就能通过 MCP 协议（这里是 stdio）调用这些工具。
@mcp.tool()
def search_knowledge(query: str, top_k: int = 5) -> str:
    """在本地知识库（Milvus）中检索与问题相关的片段，返回带来源的结果。"""
    try:
        results = rag.search(query, top_k=top_k)
    except Exception as exc:  # noqa: BLE001
        return f"知识库检索失败：{exc}"
    if not results:
        return "知识库中没有检索到相关内容。"
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] 来源={r['source']} 相关度={r['score']}\n{r['text'].strip()}")
    return "\n\n".join(lines)


@mcp.tool()
def query_news(keyword: str = "", category: str = "", source: str = "", limit: int = 10) -> str:
    """按关键词/分类/来源查询新闻（MySQL 数据库）。"""
    rows = db.query_news(
        keyword=keyword or None,
        category=category or None,
        source=source or None,
        limit=limit,
    )
    if not rows:
        return "没有查到符合条件的新闻。"
    lines = []
    for r in rows:
        lines.append(
            f"- {r['title']}｜来源={r['source']}｜分类={r['category'] or '未分类'}｜"
            f"时间={r['publish_time']}｜评分={r['score']}｜URL={r['url']}"
        )
    return "\n".join(lines)


@mcp.tool()
def get_statistics() -> str:
    """获取系统统计信息。"""
    return json.dumps({"news_count": db.count_news()}, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="stdio")
