from services.llm_service import chat_completion


def chat(message: str, session_id: str = "") -> dict:
    """
    业务层：调用大模型生成真实回答。
    之前的"正在分析: xxx"假返回已被替换。
    """
    answer = chat_completion(message)
    return {
        "result": answer,
        "session_id": session_id,
    }