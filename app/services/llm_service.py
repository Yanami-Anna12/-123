from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config.settings import settings

SYSTEM_PROMPT = "你是一个企业智能情报分析助手，请用中文简洁、专业地回答。"


def _create_model(model_name: str | None = None) -> ChatOpenAI:
    """创建大模型客户端（LangChain 封装版，和你老师教的一致）"""
    return ChatOpenAI(
        model=model_name or settings.OPENAI_MODEL,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_api_base=settings.OPENAI_BASE_URL,
        temperature=0.6,
    )


def chat_completion(message: str, model_name: str | None = None) -> str:
    """普通问答：调用大模型，返回完整回答"""
    model = _create_model(model_name)
    resp = model.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=message),
        ]
    )
    return resp.content or ""


def stream_chat(message: str, model_name: str | None = None):
    """流式问答：生成器，逐段返回文本（配合 SSE）"""
    model = _create_model(model_name)
    for chunk in model.stream(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=message),
        ]
    ):
        if chunk.content:
            yield chunk.content
