from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from schemas.chat_schema import ChatRequest
from services.chat_service import chat
from services.llm_service import stream_chat
from utils.response import success

router = APIRouter()


@router.post("/ai/chat")
def ai_chat(request: ChatRequest):
    """AI 智能问答（普通，一次性返回完整回答）"""
    result = chat(request.message, request.session_id)
    return success(result)


@router.post("/ai/chat/stream")
async def ai_chat_stream(request: ChatRequest):
    """AI 智能问答(SSE 流式，逐字输出）"""
    return StreamingResponse(
        sse_wrap(request.message),
        media_type="text/event-stream",
    )


def sse_wrap(message: str):
    """把模型输出包装成 SSE 格式：每个片段一行 data: xxx"""
    for text in stream_chat(message):
        yield f"data: {text}\n\n"
    yield "data: [DONE]\n\n"