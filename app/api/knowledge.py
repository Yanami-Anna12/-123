"""知识库接口：真正调用成员B 的 RAG（混合检索 + Reranker 精排）与文档入库。"""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.config.constants import Code
from app.utils.response import fail, success

router = APIRouter()


class KnowledgeQueryRequest(BaseModel):
    """知识库检索请求"""

    question: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=20)


class KnowledgeIngestRequest(BaseModel):
    """文档入库请求（支持 .pdf / .docx / .txt / .md）"""

    paths: list[str] = Field(..., min_length=1)


@router.post("/knowledge/query")
def knowledge_query(request: KnowledgeQueryRequest):
    """RAG 检索：向量化 → 混合检索（Dense+Sparse+RRF）→ Reranker 精排"""
    try:
        from app.rag.retriever import search, search_crawler_collection

        results = search(request.question, top_k=request.top_k)
        engine = "hybrid"
        # intel_rag 里没有内容时，兜底去搜爬虫流水线写入的 hacker_news 集合
        if not results:
            results = search_crawler_collection(request.question, top_k=request.top_k)
            engine = "crawler"
        return success({"question": request.question, "engine": engine, "results": results})
    except Exception as exc:  # noqa: BLE001
        # RAG 不可用（Milvus/模型未就绪）时，退回数据库关键词检索，保证接口可用
        try:
            from app.database import repo

            rows = repo.query_news(keyword=request.question, limit=request.top_k)
            return success(
                {
                    "question": request.question,
                    "engine": "keyword_fallback",
                    "note": f"RAG 暂不可用，已退回数据库关键词检索：{exc}",
                    "results": rows,
                }
            )
        except Exception as exc2:  # noqa: BLE001
            return fail(Code.RAG_ERROR, f"知识库检索失败: {exc2}")


@router.post("/knowledge/ingest")
def knowledge_ingest(request: KnowledgeIngestRequest):
    """文档入库：解析 → 切分 → 向量化 → 写入 Milvus"""
    try:
        from app.rag.retriever import ingest

        count = ingest(request.paths)
        return success({"ingested": count})
    except Exception as exc:  # noqa: BLE001
        return fail(Code.VECTOR_ERROR, f"文档入库失败: {exc}")


@router.get("/knowledge/stats")
def knowledge_stats():
    """知识库状态：集合名 + 向量条数（Milvus 未启动时返回提示）"""
    try:
        from app.config.settings import settings
        from pymilvus import MilvusClient

        client = MilvusClient(uri=settings.MILVUS_URI)
        stats = client.get_collection_stats(settings.MILVUS_COLLECTION)
        return success(
            {
                "collection": settings.MILVUS_COLLECTION,
                "chunk_count": stats.get("row_count", 0),
            }
        )
    except Exception as exc:  # noqa: BLE001
        return fail(Code.VECTOR_ERROR, f"Milvus 未连接: {exc}")
