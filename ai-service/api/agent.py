from fastapi import APIRouter
from pydantic import BaseModel, Field

from graph.workflow import run_workflow
from utils.response import success

router = APIRouter()


class AgentRequest(BaseModel):
    """Agent 工作流请求"""
    message: str = Field(..., min_length=1)


@router.post("/ai/agent/invoke")
def agent_invoke(request: AgentRequest):
    """调用 LangGraph 情报分析工作流"""
    result = run_workflow(request.message)
    return success(result)