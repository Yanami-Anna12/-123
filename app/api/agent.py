"""Agent 接口：优先走成员B 的 LangGraph ReAct 智能体（MCP 工具），
失败时自动回落到成员C 的 LangGraph 情报分析工作流。
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.config.constants import Code
from app.utils.response import fail, success

router = APIRouter()


class AgentRequest(BaseModel):
    """Agent 工作流请求"""
    message: str = Field(..., min_length=1)


@router.post("/ai/agent/invoke")
def agent_invoke(request: AgentRequest):
    """调用智能体：ReAct（MCP 工具）→ 失败自动回落到 LangGraph 情报分析工作流"""
    try:
        from app.agent.agent import ask

        answer, trace = ask(request.message)
        return success({"answer": answer, "tools": trace, "mode": "react"})
    except Exception as exc:  # noqa: BLE001
        try:
            from app.graph.workflow import run_workflow

            result = run_workflow(request.message)
            return success(
                {
                    "answer": result.get("answer", ""),
                    "mode": "langgraph",
                    "fallback_reason": str(exc),
                }
            )
        except Exception as exc2:  # noqa: BLE001
            return fail(Code.AGENT_ERROR, f"Agent 调用失败: {exc2}")
