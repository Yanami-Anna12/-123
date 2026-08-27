import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.database.db import SessionLocal
from app.database.models.news import News
from app.graph.state import IntelligenceState
from app.services.llm_service import SYSTEM_PROMPT, _create_model

# 任务规划提示词：让大模型输出 JSON
UNDERSTAND_PROMPT = (
    "你是任务规划器。请分析用户问题，只输出 JSON，格式：\n"
    '{"intent": "query 或 analyze", "keywords": ["关键词1", "关键词2"]}\n'
    "intent：查询具体信息填 query，分析/报告/趋势填 analyze；"
    "keywords：给出 1 到 3 个用于搜索新闻的关键词。"
)


def _search_news(keyword: str, limit: int = 3) -> list:
    """从 MySQL 查新闻（关键词模糊匹配）；查不到就返回示例数据（演示用）"""
    try:
        db = SessionLocal()
        try:
            rows = (
                db.query(News)
                .filter(News.title.contains(keyword))
                .limit(limit)
                .all()
            )
            if rows:
                return [
                    {"title": n.title, "source": n.source, "url": n.url,
                     "publish_time": str(n.publish_time)}
                    for n in rows
                ]
        finally:
            db.close()
    except Exception:
        pass
    return [
        {"title": f"AI行业快讯：{keyword}相关新闻示例1", "source": "示例来源", "url": "https://example.com/1"},
        {"title": f"AI行业快讯：{keyword}相关新闻示例2", "source": "示例来源", "url": "https://example.com/2"},
    ]


def understand_node(state: IntelligenceState) -> dict:
    """节点1：大模型制定查询计划（意图 + 关键词）"""
    model = _create_model()
    resp = model.invoke(
        [
            SystemMessage(content=UNDERSTAND_PROMPT),
            HumanMessage(content=state["question"]),
        ]
    )
    try:
        plan = json.loads(resp.content)
        intent = plan.get("intent", "analyze")
        keywords = plan.get("keywords") or [state["question"]]
    except Exception:
        intent = "analyze"
        keywords = [state["question"]]
    return {"intent": intent, "keywords": keywords, "attempts": 0}


def query_data_node(state: IntelligenceState) -> dict:
    """节点2：按计划查下一个关键词（Reducer 把 data 追加进状态，循环时数据累积）"""
    idx = state["attempts"]
    keyword = state["keywords"][idx] if idx < len(state["keywords"]) else state["question"]
    results = _search_news(keyword)
    return {"data": results, "attempts": state["attempts"] + 1}


def report_node(state: IntelligenceState) -> dict:
    """节点3：用大模型基于数据生成最终回答"""
    model = _create_model()
    data_text = json.dumps(state["data"], ensure_ascii=False)[:2000]
    resp = model.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT + "\n请严格基于给定的数据回答用户问题。"),
            HumanMessage(content=f"用户问题：{state['question']}\n\n相关数据：{data_text}"),
        ]
    )
    return {"answer": resp.content or ""}
