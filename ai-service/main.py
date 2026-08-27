from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from sqlalchemy import text
from database.db import engine

from config.settings import settings
from config.constants import Code
from utils.response import fail
from api.chat import router as chat_router
from api.agent import router as agent_router
from api.crawler import router as crawler_router
from api.knowledge import router as knowledge_router
from api.report import router as report_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# CORS：允许前端（Vue）跨域访问，开发阶段先全放开
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由，统一挂载到 /api 前缀下
app.include_router(chat_router, prefix="/api")
app.include_router(agent_router, prefix="/api")
app.include_router(crawler_router, prefix="/api")
app.include_router(knowledge_router, prefix="/api")
app.include_router(report_router, prefix="/api")


# 兜底异常：任何没被处理的报错，都统一返回 {code, message, data}
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=fail(Code.INTERNAL_ERROR, f"服务器内部错误: {exc}"),
    )


# 参数校验失败（比如没传 message），统一返回 422
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content=fail(Code.VALIDATION_ERROR, "参数校验失败", {"errors": exc.errors()}),
    )


# 访问不存在的接口，统一返回 404
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=fail(exc.status_code, str(exc.detail)),
    )


@app.get("/")
def root():
    return {"message": "AI Service Running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db():
    """检查数据库是否连上"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "error": str(e)}
    