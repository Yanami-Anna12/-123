from fastapi import APIRouter
from pydantic import BaseModel, Field

from utils.response import success

router = APIRouter()


class ReportIndustryRequest(BaseModel):
    """行业报告请求"""
    industry: str = Field(..., min_length=1)


@router.post("/report/industry")
def report_industry(request: ReportIndustryRequest):
    """生成行业报告（骨架版）"""
    return success({"report_id": 1, "report_type": "industry", "industry": request.industry, "status": "generating"})


@router.get("/report/list")
def report_list(report_type: str = ""):
    """报告列表（骨架版）"""
    reports = [
        {"id": 1, "report_type": "industry", "title": "AI行业趋势报告", "status": "success"},
    ]
    return success(reports)


@router.get("/report/{report_id}")
def report_detail(report_id: int):
    """报告详情（骨架版）"""
    return success({"id": report_id, "title": "AI行业趋势报告", "content": "（示例）报告正文..."})