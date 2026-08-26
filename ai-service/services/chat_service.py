def chat(message: str, session_id: str = "") -> dict:
    """
    业务层：处理聊天请求。
    目前先返回固定内容，验证整条调用链；
    下一步会在这里接入真实大模型。
    """
    return {
        "result": f"正在分析: {message}",
        "session_id": session_id,
    }