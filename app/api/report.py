"""报告接口：从 MySQL 检索行业新闻 → 大模型生成结构化行业分析报告。"""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.config.constants import Code
from app.utils.response import fail, success

router = APIRouter()

REPORT_PROMPT = (
    "你是企业情报分析师。请基于下面的新闻数据，生成一份简洁、专业的行业分析报告。\n"
    "报告结构：1. 行业概况 2. 重点动态（逐条引用新闻标题和来源）3. 趋势判断 4. 风险提示。\n"
    "使用中文，Markdown 格式，总字数 600 字以内。"
)


class ReportIndustryRequest(BaseModel):
    """行业报告请求"""

    industry: str = Field(..., min_length=1)


@router.post("/report/industry")
def report_industry(request: ReportIndustryRequest):
    """生成行业报告：检索「行业」相关新闻 → 大模型撰写"""
    try:
        from app.database import repo
        from app.services.llm_service import chat_completion

        news = repo.query_news(keyword=request.industry, limit=10)
        if not news:
            return fail(
                Code.NOT_FOUND,
                f"没有找到与「{request.industry}」相关的新闻，请先运行爬虫采集数据",
            )

        data_text = "\n".join(
            f"- {n['title']}（{n['source']}，{n['publish_time']}）{n['url']}"
            for n in news
        )
        content = chat_completion(
            f"行业：{request.industry}\n\n新闻数据：\n{data_text}\n\n{REPORT_PROMPT}"
        )
        return success(
            {
                "industry": request.industry,
                "report": content,
                "news_used": len(news),
                "sources": [n["url"] for n in news],
            }
        )
    except Exception as exc:  # noqa: BLE001
        return fail(Code.LLM_ERROR, f"报告生成失败: {exc}")


@router.get("/report/list")
def report_list(report_type: str = ""):
    """报告列表（本次整合不落库，返回空列表）"""
    return success([])
