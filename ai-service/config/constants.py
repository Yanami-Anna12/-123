class Code:
    """统一错误编码"""
    SUCCESS = 200
    PARAM_ERROR = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    DUPLICATE = 409
    VALIDATION_ERROR = 422
    INTERNAL_ERROR = 500
    LLM_ERROR = 501
    RAG_ERROR = 502
    CRAWLER_ERROR = 503
    AGENT_ERROR = 504
    OCR_ERROR = 505
    VECTOR_ERROR = 506
    MCP_ERROR = 507


class Role:
    """用户角色"""
    ADMIN = "admin"
    ANALYST = "analyst"
    USER = "user"


class TaskStatus:
    """爬虫任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    STOPPED = "stopped"