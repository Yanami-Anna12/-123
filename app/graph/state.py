from operator import add
from typing import Annotated, TypedDict


class IntelligenceState(TypedDict):
    """LangGraph 状态：整个工作流中传递的数据"""
    question: str                       # 用户问题
    intent: str                         # 意图：query / analyze
    keywords: list                      # 查询计划（关键词列表）
    data: Annotated[list, add]          # 查到的数据（Reducer：循环时追加，不覆盖）
    attempts: int                       # 已查询次数（循环计数器，防止死循环）
    answer: str                         # 最终回答
