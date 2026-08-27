"""全局配置：所有环境变量集中在这里读取（.env 文件位于项目根目录）。

整合版把成员A（爬虫/MySQL）、成员B（RAG/Agent）、成员C（FastAPI/LangGraph）
三方的配置统一到了这一份里，避免各自读各自的 .env。
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录：整合版/（即本文件向上三级：app/config/settings.py → 整合版/）
ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


class Settings:
    """集中管理所有环境变量配置"""

    # 项目根目录（整合版/），供 settings.ROOT 调用（如脚本、Agent MCP 工作目录）
    ROOT = ROOT

    # ===== 应用配置 =====
    APP_NAME = os.getenv("APP_NAME", "Enterprise AI Agent Service")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

    # ===== MySQL 数据库（成员A 的 news.sql 使用的库：ai_intelligence）=====
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "123")
    DB_NAME = os.getenv("DB_NAME", "ai_intelligence")

    # ===== 大模型配置（DeepSeek，OpenAI 兼容接口）=====
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "deepseek-chat")

    # 兼容成员B agent.py 里的 DEEPSEEK_* 命名：没单独配就回落到 OPENAI_*
    DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY", OPENAI_API_KEY)
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", OPENAI_BASE_URL)
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", OPENAI_MODEL)

    # ===== Milvus 向量库（成员B）=====
    MILVUS_URI = os.getenv("MILVUS_URI", "http://localhost:19530")
    MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
    MILVUS_COLLECTION = os.getenv("MILVUS_COLLECTION", "intel_rag")

    # ===== RAG：本地模型路径（bge-base-zh-v1.5，可在 .env 覆盖）=====
    EMBEDDING_MODEL_PATH = os.getenv(
        "EMBEDDING_MODEL_PATH",
        str(ROOT / "data" / "models" / "bge-base-zh-v1.5"),
    )
    RERANKER_MODEL_PATH = os.getenv(
        "RERANKER_MODEL_PATH",
        str(ROOT / "data" / "models" / "bge-reranker-large"),
    )

    # ===== 文本切分与检索参数 =====
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
    HYBRID_TOP_K = int(os.getenv("HYBRID_TOP_K", "20"))
    TOP_K = int(os.getenv("TOP_K", "5"))


# 全局唯一实例，其他模块通过下面这行引用配置
settings = Settings()
