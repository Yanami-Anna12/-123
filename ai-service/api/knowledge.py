from fastapi import APIRouter
from pydantic import BaseModel, Field

from utils.response import success

router = APIRouter()


class KnowledgeQueryRequest(BaseModel):
    """知识库检索请求"""
    question: str = Field(..., min_length=1)


@router.get("/knowledge/list")
def knowledge_list():
    """文档列表（骨架版：等B的RAG就绪后接真实数据）"""
    docs = [
        {"id": 1, "name": "AI行业政策汇总.pdf", "status": "indexed", "chunk_count": 56},
        {"id": 2, "name": "企业情报报告.docx", "status": "parsing", "chunk_count": 0},
    ]
    return success(docs)


@router.post("/knowledge/query")
def knowledge_query(request: KnowledgeQueryRequest):
    """知识库检索（骨架版）"""
    return success({"question": request.question, "results": "（示例）检索到相关片段..."})


@router.delete("/knowledge/{doc_id}")
def knowledge_delete(doc_id: int):
    """删除文档（骨架版）"""
    return success(message=f"文档 {doc_id} 已删除")