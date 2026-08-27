"""爬虫接口：真正调用成员A 的 HackerNews 爬虫。

完整流水线：抓取新闻 → 存 JSON 备份 → 写入 MySQL → 文本切分 →
Embedding → 写入 Milvus 向量库。采集在后台任务中执行，接口立即返回任务 ID。
"""
from fastapi import APIRouter, BackgroundTasks

from app.config.constants import Code, TaskStatus
from app.utils.response import fail, success

router = APIRouter()

# 简单的内存任务表（重启后清空，演示/答辩够用）
_tasks: dict[int, dict] = {}
_task_seq = 0


def _run_crawl(task_id: int, limit: int) -> None:
    """后台执行完整采集流水线，并更新任务状态。"""
    task = _tasks[task_id]
    try:
        from app.crawler.hacker_news import get_mysql_statistics, get_news_list, save_json, save_to_mysql

        task["status"] = TaskStatus.RUNNING

        # 1. 抓取
        news_list = get_news_list(limit=limit)
        # 2. 存 JSON + MySQL
        save_json(news_list)
        mysql_ok, mysql_err = save_to_mysql(news_list)

        # 3. 切分 → Embedding → Milvus（可选：Milvus 未启动时跳过，不影响数据入库）
        milvus_note = ""
        milvus_count = 0
        chunk_count = 0
        try:
            from app.config.settings import settings
            from pymilvus import MilvusClient

            probe = MilvusClient(uri=settings.MILVUS_URI)
            probe.list_collections()  # 探活：连不上会立刻抛异常
        except Exception as exc:  # noqa: BLE001
            milvus_note = f"Milvus 未连接（{exc}），已跳过向量入库；新闻数据已存入 MySQL"
        else:
            try:
                from app.crawler.hacker_news import embed_chunks, save_to_milvus, split_new

                chunks = split_new(news_list)
                embedded = embed_chunks(chunks)
                chunk_count = len(embedded)
                milvus_count = save_to_milvus(embedded)
            except Exception as exc:  # noqa: BLE001
                milvus_note = f"向量入库失败（{exc}），已跳过；新闻数据已存入 MySQL"

        # 4. 统计
        total, hn_count = get_mysql_statistics()

        task.update(
            status=TaskStatus.SUCCESS,
            news_count=len(news_list),
            mysql_success=mysql_ok,
            mysql_error=mysql_err,
            chunk_count=chunk_count,
            milvus_count=milvus_count,
            db_total=total,
            db_hacker_news=hn_count,
            note=milvus_note,
            error="",
        )
    except Exception as exc:  # noqa: BLE001
        task.update(status=TaskStatus.FAILED, error=str(exc))


@router.get("/crawler/tasks")
def crawler_tasks():
    """爬虫任务列表（真实后台任务状态）"""
    return success(list(_tasks.values()))


@router.get("/crawler/tasks/{task_id}")
def crawler_task_detail(task_id: int):
    """查询某个爬虫任务的实时状态"""
    task = _tasks.get(task_id)
    if not task:
        return fail(Code.NOT_FOUND, "任务不存在")
    return success(task)


@router.post("/crawler/start")
def crawler_start(
    background_tasks: BackgroundTasks,
    spider_name: str = "hacker_news",
    limit: int = 20,
):
    """启动爬虫：抓取 Hacker News → 存 JSON/MySQL → 切分 → Embedding → 写入 Milvus"""
    global _task_seq
    if spider_name != "hacker_news":
        return fail(Code.PARAM_ERROR, f"暂不支持爬虫 {spider_name}，目前只有 hacker_news")
    _task_seq += 1
    _tasks[_task_seq] = {
        "id": _task_seq,
        "spider_name": spider_name,
        "limit": limit,
        "status": TaskStatus.PENDING,
        "error": "",
    }
    background_tasks.add_task(_run_crawl, _task_seq, limit)
    return success({"task_id": _task_seq, "status": TaskStatus.PENDING})


@router.get("/crawler/statistics")
def crawler_statistics():
    """数据库新闻统计（总条数 / Hacker News 条数）"""
    try:
        from app.crawler.hacker_news import get_mysql_statistics

        total, hn_count = get_mysql_statistics()
        return success({"news_count": total, "hacker_news_count": hn_count})
    except Exception as exc:  # noqa: BLE001
        return fail(Code.CRAWLER_ERROR, f"统计失败: {exc}")
