class Code:
    """统一错误编码：所有接口返回的 code 都从这里取，前后端共用一套含义"""

    # ===== 通用 =====
    SUCCESS = 200          # 成功：一切正常
    PARAM_ERROR = 400      # 请求参数错误：参数格式/内容不对（比如少了必填字段）
    UNAUTHORIZED = 401     # 未登录或 Token 无效：需要登录才能访问
    FORBIDDEN = 403        # 无权限：登录了，但你的角色不允许访问
    NOT_FOUND = 404        # 数据不存在：请求的资源/接口找不到
    DUPLICATE = 409        # 数据重复：插入的数据和已有数据冲突
    VALIDATION_ERROR = 422 # 数据校验失败：Pydantic 拦下的（类型不对、为空等）

    # ===== 服务内部错误 =====
    INTERNAL_ERROR = 500   # 服务器内部错误：代码没处理到的意外异常（兜底）
    LLM_ERROR = 501        # AI 模型调用失败：大模型接口报错/超时
    RAG_ERROR = 502        # RAG 检索失败：知识库查询出错
    CRAWLER_ERROR = 503    # 爬虫任务启动失败：爬虫模块出错
    AGENT_ERROR = 504      # Agent/工作流执行失败：LangGraph 流程出错
    OCR_ERROR = 505        # OCR/文档解析失败：图片、PDF 识别出错
    VECTOR_ERROR = 506     # 向量库服务失败：Milvus 出错
    MCP_ERROR = 507        # MCP 工具调用失败


class Role:
    """用户角色（以后做权限用）"""
    ADMIN = "admin"        # 管理员：能管爬虫任务、知识库、数据、报告
    ANALYST = "analyst"    # 分析员：能 AI 问答、看情报、生成报告
    USER = "user"          # 普通用户：只能对话、看公开情报


class TaskStatus:
    """爬虫任务状态"""
    PENDING = "pending"    # 等待中：还没开始跑
    RUNNING = "running"    # 运行中：正在抓取
    SUCCESS = "success"    # 成功：抓完并入库
    FAILED = "failed"      # 失败：出错中断
    STOPPED = "stopped"    # 已停止：被人为停掉
