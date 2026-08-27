from langgraph.graph import END, START, StateGraph

from graph.nodes import query_data_node, report_node, understand_node
from graph.state import IntelligenceState


def should_continue(state: IntelligenceState) -> str:
    """条件边：计划没执行完且数据不够 → 继续循环；否则去生成报告"""
    if state["attempts"] < len(state["keywords"]) and len(state["data"]) < 4:
        return "continue"
    return "done"


def build_graph():
    g = StateGraph(IntelligenceState)

    # 节点
    g.add_node("understand", understand_node)
    g.add_node("query_data", query_data_node)
    g.add_node("report", report_node)

    # 连线
    g.add_edge(START, "understand")
    g.add_edge("understand", "query_data")

    # 循环核心：query_data 之后判断，continue 就回到自己
    g.add_conditional_edges(
        "query_data",
        should_continue,
        {"continue": "query_data", "done": "report"},
    )

    g.add_edge("report", END)

    return g.compile()


# 全局唯一的工作流实例
workflow = build_graph()


def run_workflow(question: str) -> dict:
    """执行工作流，返回最终状态（含回答和过程数据）"""
    result = workflow.invoke(
        {"question": question, "intent": "", "keywords": [], "data": [], "attempts": 0, "answer": ""}
    )
    return result
