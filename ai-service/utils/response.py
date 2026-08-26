from config.constants import Code


def success(data=None, message="success"):
    """成功响应：所有接口统一返回 {code, message, data}"""
    return {"code": Code.SUCCESS, "message": message, "data": data}


def fail(code: int, message: str, data=None):
    """失败响应：返回错误码、错误信息、可选数据"""
    return {"code": code, "message": message, "data": data}