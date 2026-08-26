from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """AI 聊天请求参数"""
    message: str = Field(..., min_length=1, description="用户问题（必填，不能为空）")
    session_id: str = Field("", description="会话ID，记忆功能用")