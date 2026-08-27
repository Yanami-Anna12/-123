from fastapi import APIRouter

from utils.response import success

router = APIRouter()


@router.get("/crawler/tasks")
def crawler_tasks(status: str = ""):
    """爬虫任务列表（骨架版：返回示例数据，等A的爬虫就绪后接真实数据）"""
    tasks = [
        {"id": 1, "spider_name": "hacker_news", "status": "success", "data_count": 320},
        {"id": 2, "spider_name": "tech_news", "status": "running", "data_count": 128},
    ]
    return success(tasks)


@router.get("/crawler/tasks/{task_id}")
def crawler_task_detail(task_id: int):
    """爬虫任务详情（骨架版）"""
    return success({"id": task_id, "spider_name": "hacker_news", "status": "success", "data_count": 320})


@router.post("/crawler/start")
def crawler_start(spider_name: str = "hacker_news"):
    """启动爬虫（骨架版）"""
    return success({"task_id": 99, "spider_name": spider_name, "status": "pending"})