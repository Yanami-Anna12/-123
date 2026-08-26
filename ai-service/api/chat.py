from fastapi import APIRouter

from schemas.chat_schema import ChatRequest
from services.chat_service import chat
from utils.response import success

router = APIRouter()


@router.post("/ai/chat")
def ai_chat(request: ChatRequest):
    """
    AI 智能问答接口
    请求体: {"message": "分析AI行业"}
    """
    result = chat(request.message, request.session_id)
    return success(result)