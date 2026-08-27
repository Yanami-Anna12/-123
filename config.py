"""全局配置：密钥从 .env 读取，其余给默认值。"""
import os
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录（本文件所在目录）
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

# ---- DeepSeek 大模型（OpenAI 兼容接口）----
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_KEY", "")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

# ---- RAG：向量化与检索 ----
# 本地已下载好的 BGE-M3 模型（一次同时产出 Dense + Sparse 两种向量）
EMBEDDING_MODEL_PATH = str(ROOT / "data" / "models" / "bge-m3")
# 本地已下载好的 BGE-Reranker 模型（对候选片段做二次精排）
RERANKER_MODEL_PATH = str(ROOT / "data" / "models" / "BAAI--bge-reranker-large" / "snapshots" / "master")

# Milvus 向量库（你 Docker 里部署的）
MILVUS_URI = os.environ.get("MILVUS_URI", "http://localhost:19530")
MILVUS_COLLECTION = os.environ.get("MILVUS_COLLECTION", "intel_rag")

# 文本切分参数
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "500"))       # 每段最多 500 字
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "50"))  # 相邻段重叠 50 字

# 检索参数
HYBRID_TOP_K = int(os.environ.get("HYBRID_TOP_K", "20"))   # 混合检索先召回 20 条候选
TOP_K = int(os.environ.get("TOP_K", "5"))                  # 重排后最终返回 5 条

# ---- MySQL 数据库 ----
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "123")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "ai_intelligence")
