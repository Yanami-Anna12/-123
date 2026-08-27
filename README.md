# 企业智能情报采集与分析 Agent 平台（整合版）

三人小组代码整合版：把成员A 的爬虫 + MySQL、成员B 的 RAG + Agent + MCP、
成员C 的 FastAPI + LangGraph 合并成一个可以直接跑起来的统一项目。

## 目录结构

```text
整合版/
├── app/
│   ├── main.py            # FastAPI 入口（uvicorn app.main:app）
│   ├── api/               # 接口层：chat / agent / crawler / knowledge / report
│   ├── config/            # 统一配置（一份 .env 管所有模块）
│   ├── database/          # SQLAlchemy 引擎 + news 表模型 + 统一数据访问层(repo)
│   ├── graph/             # LangGraph 情报分析工作流（成员C）
│   ├── services/          # LLM 调用、对话服务
│   ├── crawler/           # Hacker News 爬虫（成员A）
│   ├── rag/               # RAG：混合检索 retriever + embedding + milvus（成员B）
│   ├── agent/             # ReAct 智能体 + MCP 服务（成员B）
│   └── utils/             # 统一响应格式
├── scripts/
│   ├── init_db.py         # 建表 + 导入 data/hacker_news.json
│   ├── run_crawler.py     # 一键跑爬虫流水线
│   └── demo_ask.py        # 命令行向 Agent 提问
├── data/                  # 爬虫原始数据备份
├── sql/news.sql           # 成员A 的 MySQL 表结构与数据
├── requirements.txt
├── .env.example           # 复制为 .env 后填写
└── Dockerfile
```

## 环境准备

1. **Python 3.11** + MySQL（建库 `ai_intelligence`，可直接导入 `sql/news.sql`）
2. **Milvus 向量库**（本地 Docker 启动，默认 `localhost:19530`）
3. **DeepSeek API Key**：复制 `.env.example` 为 `.env`，填 `OPENAI_API_KEY`

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

> 如果你已经有自己的 conda 环境（例如 `my_new_env`），直接在 PyCharm 里把它选为
> 项目解释器即可，只需确认装了 `fastmcp` 和 `langchain-mcp-adapters` 两个包：
> `conda activate my_new_env && pip install fastmcp langchain-mcp-adapters`

## 初始化与启动

```bash
# 1. 建表 + 导入已有新闻数据
python scripts/init_db.py

# 2. 启动 API 服务（http://127.0.0.1:8000，接口文档 /docs）
uvicorn app.main:app --reload --port 8000
```

## 主要接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/ai/chat` | AI 问答（普通） |
| POST | `/api/ai/chat/stream` | AI 问答（SSE 流式） |
| POST | `/api/ai/agent/invoke` | Agent 智能体（ReAct + MCP 工具，失败自动回落到 LangGraph 工作流） |
| POST | `/api/crawler/start?spider_name=hacker_news&limit=20` | 启动爬虫（后台执行完整流水线） |
| GET | `/api/crawler/tasks` | 爬虫任务列表 |
| GET | `/api/crawler/statistics` | 新闻统计 |
| POST | `/api/knowledge/query` | RAG 知识库检索（混合检索，自动兜底爬虫集合） |
| POST | `/api/knowledge/ingest` | 文档入库（pdf/docx/txt/md） |
| GET | `/api/knowledge/stats` | 知识库状态 |
| POST | `/api/report/industry` | 生成行业分析报告（查新闻 + 大模型撰写） |

## 命令行工具

```bash
python scripts/run_crawler.py --limit 20   # 抓取新闻入库
python scripts/demo_ask.py "最近 AI 行业有什么新闻"
```

## 备注

- RAG 的混合检索需要本地模型：`data/models/bge-m3` 和
  `data/models/BAAI--bge-reranker-large`（体积大，未随代码提交），
  也可通过 `.env` 里的 `EMBEDDING_MODEL_PATH` / `RERANKER_MODEL_PATH` 指定。
- 爬虫流水线用的是 sentence-transformers 的 BGE-M3（首次运行自动下载），
  写入 `hacker_news` 集合；知识库接口优先查 `intel_rag`，没有结果时兜底查 `hacker_news`。
