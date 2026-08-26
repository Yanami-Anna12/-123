from openai import OpenAI

from config.settings import settings

# 客户端：连接大模型（OpenAI 兼容接口）
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
)

SYSTEM_PROMPT = "你是一个企业智能情报分析助手，请用中文简洁、专业地回答。"


def chat_completion(message: str, model: str | None = None) -> str:
    """普通问答：调用大模型，返回完整回答"""
    resp = client.chat.completions.create(
        model=model or settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
    )
    return resp.choices[0].message.content or ""


def stream_chat(message: str, model: str | None = None):
    """流式问答：生成器，逐段返回文本（配合 SSE）"""
    stream = client.chat.completions.create(
        model=model or settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        stream=True,
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content