# 企业智能情报采集与分析 Agent 平台 需求文档

## 一、项目简介

本项目面向企业信息分析、行业研究与智能决策场景，构建一个以 **Python 爬虫 + FastAPI + RAG + LangGraph Agent + MCP** 为核心的企业智能情报平台。

系统持续采集互联网公开信息，包括新闻、企业公告、政策文件、招聘信息、行业资讯等，经过清洗、去重、分类、结构化入库后，一部分进入 MySQL 作为业务数据，一部分经过文档解析、OCR、向量化后进入 Milvus 知识库。

用户可以通过 AI 对话直接提出企业、行业、政策、招聘与趋势分析问题，由 LangGraph Agent 根据问题意图自主选择数据库查询、知识库检索、网页搜索、统计分析等工具，并完成多阶段分析，最终生成带来源的结构化报告。

项目目标：通过一个真实可运行的后端项目，完整展示 **Python 爬虫、FastAPI、LangChain、LangGraph、RAG、Agent、Function Calling、MCP、OCR、Memory、MySQL、Milvus** 等大模型应用开发与工程化能力。

---

## 二、项目核心能力展示映射表

| 技术模块 | 项目应用位置 | 展示能力点 |
| --- | --- | --- |
| Python 爬虫 | 新闻、公告、招聘、政策数据采集 | requests/httpx、parsel、Scrapy、Playwright、增量爬取、去重、清洗 |
| FastAPI | AI 服务与爬虫管理 API | REST API、异步接口、SSE、依赖注入、Pydantic |
| models 大模型调用 | AI 分析、报告生成 | 多模型封装、流式输出、结构化输出、模型切换 |
| prompt 提示词 | 情报分析、报告生成、分类 | PromptTemplate、Few-shot、变量注入、输出约束 |
| chains 链 | 文档分析、情报总结 | LCEL 串行/并行链、检索增强链 |
| RAG | 企业新闻、公告、政策、报告知识库 | 文档解析、Chunk、Embedding、混合检索、Rerank、引用来源 |
| agent 智能体 | 企业情报分析助手 | Function Calling、Tool Calling、ReAct、自主工具选择 |
| memory 记忆 | 用户会话与分析偏好 | 短期会话记忆、长期用户偏好、线程隔离 |
| LangGraph | 情报分析、日报、数据入库 | StateGraph、条件边、并行、循环、Retry、Checkpoint、流式执行 |
| MCP | 标准化工具服务 | MCP Server、MCP Client、工具协议化 |
| OCR | 扫描 PDF、图片公告、政策文件 | OCR 文本提取、表格/图片文档解析 |
| MySQL | 结构化情报数据 | 新闻、企业、招聘、爬虫任务、报告管理 |
| Redis | 缓存与任务状态 | 热点查询缓存、任务锁、短期状态 |
| Milvus | 向量知识库 | Dense/Sparse、Hybrid Search、索引、RRF |
| LangSmith（可选） | AI 调用链路 | Trace、调试、评估、可观测性 |

---

## 三、用户角色

| 角色 | 说明 | 主要权限 |
| --- | --- | --- |
| 管理员 | 系统运营人员 | 爬虫任务管理、知识库管理、数据管理、报告管理、AI 配置 |
| 分析员 | 企业/行业研究人员 | AI 情报问答、企业对比、行业分析、报告生成 |
| 普通用户 | 使用智能情报助手的用户 | AI 对话、查看公开情报、查看报告 |

---

## 四、功能需求

### A. 用户与系统基础功能

#### 1. 登录与安全

- 用户通过账号密码登录。
- API 使用 Token/JWT 鉴权。
- 不同角色具有不同权限。
- API Key、数据库密码、模型配置统一通过 `.env` 管理。
- 敏感配置禁止硬编码。

#### 2. 用户管理

- 获取用户列表。
- 添加、修改、删除用户。
- 根据用户 id 查询详情。
- 修改密码。
- 用户角色管理。

#### 3. 系统配置

- 配置默认大模型。
- 配置 Embedding 模型。
- 配置 Reranker。
- 配置爬虫数据源。
- 配置定时任务。
- 配置知识库参数。

---

### B. Python 爬虫模块

#### 4. 数据源管理

支持多个可插拔数据源：

- 科技/AI 新闻网站。
- 企业官方网站。
- 政府政策与公告网站。
- 招聘网站。
- 行业资讯网站。
- PDF/文件型公开信息源。

数据源配置字段建议：

- source_name
- source_url
- source_type
- enabled
- crawl_interval
- parser_type

#### 5. 爬虫任务

支持：

- 手动启动。
- 定时启动。
- 单次抓取。
- 增量抓取。
- 任务停止。
- 失败重试。
- 任务状态查询。
- 任务日志查看。

任务状态：

`等待中 / 运行中 / 成功 / 失败 / 已停止`

#### 6. 数据解析与清洗

爬虫获得原始 HTML 后完成：

- HTML 标签清理。
- 广告、导航、脚本去除。
- 标题提取。
- 正文提取。
- 发布时间提取。
- 作者提取。
- 来源提取。
- URL 标准化。
- 文本空白清理。
- 分类标签提取。

#### 7. 去重与增量更新

使用 URL、标题、内容摘要等字段进行去重。

支持：

- URL 唯一约束。
- 内容 Hash 去重。
- 发布时间增量抓取。
- 已抓取记录跳过。
- 内容变化检测。

#### 8. 爬虫数据处理流

```text
抓取
 ↓
解析
 ↓
清洗
 ↓
去重
 ↓
分类
 ↓
结构化入库
 ↓
文本切分
 ↓
Embedding
 ↓
Milvus
 ↓
任务完成通知
```

---

### C. 企业情报数据模块

#### 9. 新闻管理

- 新闻列表。
- 新闻详情。
- 按来源查询。
- 按分类查询。
- 按时间范围查询。
- 按关键词搜索。
- 删除无效数据。

#### 10. 企业信息

企业字段建议：

- company_name
- industry
- website
- introduction
- financing_stage
- financing_amount
- founded_time
- location
- employee_scale
- related_news

支持：

- 企业查询。
- 企业详情。
- 企业相关新闻聚合。
- 企业招聘信息聚合。
- 企业对比。

#### 11. 招聘信息

字段建议：

- company_name
- position
- city
- salary
- experience
- education
- description
- url
- publish_time

支持按照企业、岗位、地区、发布时间进行查询和统计。

#### 12. 政策与公告

支持：

- 政策文件上传。
- 公告网页采集。
- PDF 解析。
- OCR。
- 文档分类。
- 生效时间管理。
- 来源记录。

---

### D. AI 智能问答模块

#### 13. AI 情报助手

用户可直接提出自然语言问题，例如：

- “最近一个月 AI Agent 行业发生了哪些重要事件？”
- “比较三家 AI 企业最近的招聘情况。”
- “某企业最近有哪些产品与融资动态？”
- “最近半年 AI 行业有哪些政策变化？”
- “根据知识库生成一份 AI Agent 行业月报。”

AI 助手支持：

- 流式输出。
- 多模型切换。
- 会话历史。
- 结构化输出。
- 来源引用。
- Tool Calling。
- RAG 检索。

#### 14. 流式输出

使用 SSE：

`POST /api/ai/chat/stream`

服务端持续返回模型生成内容和执行状态。

可选展示：

```text
思考/规划
 ↓
调用工具
 ↓
工具结果
 ↓
分析
 ↓
最终回答
```

---

### E. RAG 知识库

#### 15. 文档管理

支持上传：

- PDF
- Word
- Markdown
- HTML
- TXT
- 图片扫描件

功能：

- 上传。
- 删除。
- 列表。
- 状态查询。
- 解析失败重试。
- 查看切分数量。
- 查看来源信息。

#### 16. 文档解析

建议：

- PDF：MinerU / PyMuPDF。
- 扫描 PDF：OCR。
- Word：Unstructured / python-docx。
- HTML：BeautifulSoup / Trafilatura。
- Markdown：Markdown loader。

#### 17. 文本切分

建议参数：

- chunk_size：500~800。
- overlap：50~100。
- 优先按标题、段落、句号等语义边界切分。
- 中文场景可结合结巴等分词方案。

#### 18. 向量化

使用 BGE-M3：

- Dense Embedding。
- Sparse Representation。
- 统一向量化接口。

#### 19. 混合检索

```text
用户 Query
    ↓
 ┌───┴────┐
 ↓        ↓
Dense    Sparse
 ↓        ↓
 └───┬────┘
     ↓
 Hybrid Search
     ↓
 RRF 融合
     ↓
 Top 20
     ↓
 Reranker
     ↓
 Top 5
     ↓
 LLM
```

Milvus：

- Dense 向量索引。
- Sparse 倒排/稀疏索引。
- Hybrid Search。
- RRF 融合。

#### 20. Reranker

使用 BGE-Reranker 对候选文档进行二次排序。

输入：

`Query + Candidate Documents`

输出：

`Document + Relevance Score`

最终选择 Top-K 文档注入 Prompt。

#### 21. 引用与来源

每条知识库回答尽量返回：

- 文档名称。
- 来源网站。
- 原文 URL。
- 发布时间。
- 相关片段。

避免只返回无法追溯的纯文本结论。

---

### F. Agent 智能体

#### 22. 情报分析 Agent

使用 LangGraph 构建主 Agent。

Agent 负责：

- 理解用户问题。
- 识别任务类型。
- 制定查询计划。
- 选择工具。
- 合并工具结果。
- 判断是否需要继续调用工具。
- 生成最终答案。

#### 23. Agent Tools

建议提供：

- `query_news`：查询新闻。
- `query_company`：查询企业。
- `query_jobs`：查询招聘。
- `query_policy`：查询政策。
- `search_knowledge`：RAG 检索。
- `search_web`：网页搜索。
- `get_statistics`：统计分析。
- `compare_company`：企业对比。
- `crawler_start`：启动爬虫。
- `generate_report`：生成报告。

#### 24. Function Calling

- 模型自主选择工具。
- 使用 Pydantic 定义 args_schema。
- 校验参数。
- 处理工具异常。
- 工具失败支持 Retry。
- 限制最大工具调用次数。

#### 25. Agent 执行模式

建议支持：

- 普通问答。
- RAG 问答。
- 数据查询。
- 多工具组合。
- 企业对比。
- 行业分析。
- 自动报告生成。

---

### G. LangGraph 工作流

#### 26. 智能情报分析工作流

```text
START
 ↓
问题理解
 ↓
任务规划
 ↓
 ┌───────────────┬───────────────┐
 ↓               ↓               ↓
MySQL 查询      RAG 检索        Web Search
 ↓               ↓               ↓
 └───────────────┴───────────────┘
                 ↓
              结果融合
                 ↓
              Reranker
                 ↓
              分析节点
                 ↓
              报告生成
                 ↓
                END
```

体现：

- StateGraph。
- State 状态管理。
- 并行节点。
- Reducer。
- 条件边。
- 循环。
- Retry。
- Checkpoint。
- Stream。

#### 27. 爬虫数据入库工作流

```text
START
 ↓
获取任务
 ↓
抓取
 ↓
解析
 ↓
清洗
 ↓
去重
 ↓
分类
 ↓
MySQL
 ↓
Chunk
 ↓
Embedding
 ↓
Milvus
 ↓
通知
 ↓
END
```

抓取/解析/Embedding 等节点支持失败重试。

#### 28. 企业对比分析工作流

示例：

> “比较三家企业过去 3 个月的新闻、招聘与融资动态。”

```text
用户问题
 ↓
实体识别
 ↓
并行查询企业 A/B/C
 ↓
并行查询新闻/招聘/融资
 ↓
统一数据结构
 ↓
指标计算
 ↓
对比分析
 ↓
生成报告
```

体现 LangGraph 的并行执行、状态合并与报告生成能力。

#### 29. 自动日报工作流

```text
定时任务
 ↓
抓取当天数据
 ↓
去重
 ↓
分类
 ↓
重要性评分
 ↓
筛选 Top N
 ↓
RAG 补充背景资料
 ↓
Agent 分析
 ↓
生成日报
 ↓
保存数据库
```

---

### H. Memory 记忆机制

#### 30. 短期记忆

使用 LangGraph Checkpoint 保存会话状态。

同一个 `thread_id` 内保持：

- 上下文消息。
- 当前分析任务。
- 工具调用结果。
- Agent 中间状态。

#### 31. 长期记忆

保存用户偏好，例如：

```json
{
  "interested_industries": ["AI", "Robotics"],
  "preferred_report_style": "detailed",
  "preferred_companies": ["CompanyA", "CompanyB"]
}
```

跨会话恢复用户偏好。

---

### I. MCP 服务

#### 32. MCP Server

使用 FastMCP，统一暴露：

- 查询新闻。
- 查询企业。
- 查询招聘。
- 查询知识库。
- 统计分析。
- 启动爬虫。
- 生成报告。

传输方式：

- Streamable HTTP。

#### 33. MCP Client

LangChain / Agent 通过 MCP Client 连接 MCP Server。

目标：

- Tool 与 Agent 解耦。
- 第三方 Agent 可复用业务能力。
- 后续可增加其他 MCP Server。

---

### J. 自动分析报告

#### 34. 报告类型

支持生成：

- 企业情报报告。
- 行业趋势报告。
- 企业对比报告。
- 招聘分析报告。
- 政策分析报告。
- AI 行业日报。
- AI 行业周报。
- AI 行业月报。

#### 35. 报告结构

建议统一输出：

1. 摘要。
2. 核心数据。
3. 重要事件。
4. 企业动态。
5. 行业趋势。
6. 风险/机会。
7. 结论。
8. 信息来源。

最终结果可保存为 Markdown / HTML，后续可扩展 PDF。

---

## 五、系统架构

建议采用「前端 + Python AI 服务 + 数据基础设施」架构：

```text
┌────────────────────┐
│      Vue3 前端      │
│  情报 / AI / 报告   │
└──────────┬─────────┘
           │ HTTP / SSE
           ▼
┌──────────────────────────────────┐
│          FastAPI AI 服务          │
│                                  │
│  Controller                      │
│       ↓                          │
│  Service                         │
│       ↓                          │
│  LangGraph Agent                 │
│       ├── SQL Tool               │
│       ├── RAG Tool               │
│       ├── Search Tool            │
│       └── Statistics Tool        │
│                                  │
│  RAG                             │
│  ├── Loader                      │
│  ├── Embedding                   │
│  ├── Hybrid Retrieval            │
│  └── Reranker                    │
│                                  │
│  Crawler                         │
│  ├── Spider                      │
│  ├── Parser                      │
│  ├── Cleaner                     │
│  └── Pipeline                    │
│                                  │
│  MCP Server                      │
└──────────────┬───────────────────┘
               │
      ┌────────┼─────────┬────────────┐
      ▼        ▼         ▼            ▼
   MySQL     Milvus     Redis        Object Storage
      │        │
      │        └── Vector Knowledge
      └── Structured Intelligence
```

说明：

- FastAPI 负责所有 Python AI 能力。
- 爬虫与 AI 服务统一由 Python 实现。
- MySQL 保存结构化数据。
- Milvus 保存向量与稀疏检索数据。
- Redis 用于缓存、任务锁与临时状态。
- 文件对象存储保存 PDF、HTML、原始文件等。

---

## 六、接口设计

基础地址：`http://localhost:8000`

### 用户接口

| 序号 | 功能 | 方法 | URL | 参数 |
| --- | --- | --- | --- | --- |
| 1 | 登录 | POST | /api/auth/login | username、password |
| 2 | 当前用户 | GET | /api/user/me | token |
| 3 | 修改密码 | POST | /api/user/password | password |
| 4 | 用户列表 | GET | /api/user/list | token |

### 情报数据接口

| 序号 | 功能 | 方法 | URL | 参数 |
| --- | --- | --- | --- | --- |
| 5 | 新闻列表 | GET | /api/news/list | keyword、category、start、end |
| 6 | 新闻详情 | GET | /api/news/detail | id |
| 7 | 企业列表 | GET | /api/company/list | keyword |
| 8 | 企业详情 | GET | /api/company/detail | id |
| 9 | 企业对比 | POST | /api/company/compare | company_ids |
| 10 | 招聘列表 | GET | /api/job/list | company、city、keyword |
| 11 | 政策列表 | GET | /api/policy/list | keyword、category |

### AI 接口

| 序号 | 功能 | 方法 | URL | 参数 | 说明 |
| --- | --- | --- | --- | --- | --- |
| 12 | AI 对话 | POST | /api/ai/chat | message、session_id、model | 普通问答 |
| 13 | AI 流式对话 | POST | /api/ai/chat/stream | message、session_id | SSE |
| 14 | 会话历史 | GET | /api/ai/session/history | session_id | |
| 15 | Agent 调用 | POST | /api/ai/agent/invoke | message | 返回执行过程 |
| 16 | Tool 列表 | GET | /api/ai/agent/tools | token | |

### 知识库接口

| 序号 | 功能 | 方法 | URL | 参数 |
| --- | --- | --- | --- | --- |
| 17 | 上传知识文档 | POST | /api/knowledge/upload | file |
| 18 | 文档列表 | GET | /api/knowledge/list | token |
| 19 | 删除文档 | DELETE | /api/knowledge/{id} | id |
| 20 | 知识库检索测试 | POST | /api/knowledge/query | question |

### 爬虫接口

| 序号 | 功能 | 方法 | URL | 参数 |
| --- | --- | --- | --- | --- |
| 21 | 启动爬虫 | POST | /api/crawler/start | spider_name |
| 22 | 停止爬虫 | POST | /api/crawler/stop | task_id |
| 23 | 任务列表 | GET | /api/crawler/tasks | status |
| 24 | 任务详情 | GET | /api/crawler/tasks/{id} | id |
| 25 | 日志查询 | GET | /api/crawler/tasks/{id}/logs | id |

### 报告接口

| 序号 | 功能 | 方法 | URL | 参数 |
| --- | --- | --- | --- | --- |
| 26 | 生成企业报告 | POST | /api/report/company | company_id |
| 27 | 生成行业报告 | POST | /api/report/industry | industry |
| 28 | 生成对比报告 | POST | /api/report/compare | company_ids |
| 29 | 报告列表 | GET | /api/report/list | type、page |
| 30 | 报告详情 | GET | /api/report/{id} | id |

### MCP

| 序号 | 功能 | 方法 | URL |
| --- | --- | --- | --- |
| 31 | MCP Server | POST | /mcp |

---

## 七、数据库设计

### 用户表（user）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| username | varchar | 用户名 |
| password_hash | varchar | 密码哈希 |
| role | varchar | admin/analyst/user |
| create_time | datetime | 创建时间 |

### 新闻表（news）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| title | varchar | 标题 |
| source | varchar | 来源 |
| url | varchar | 原始链接，唯一 |
| content | longtext | 正文 |
| category | varchar | 分类 |
| publish_time | datetime | 发布时间 |
| content_hash | varchar | 内容去重 Hash |
| create_time | datetime | 入库时间 |

### 企业表（company）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| name | varchar | 企业名称 |
| industry | varchar | 行业 |
| website | varchar | 官网 |
| introduction | text | 企业简介 |
| location | varchar | 所在地 |
| create_time | datetime | 创建时间 |

### 招聘表（job）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| company_id | bigint | 企业 ID |
| position | varchar | 岗位 |
| city | varchar | 城市 |
| salary | varchar | 薪资 |
| experience | varchar | 经验 |
| education | varchar | 学历 |
| description | text | 岗位描述 |
| url | varchar | 来源链接 |
| publish_time | datetime | 发布时间 |

### 政策表（policy）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| title | varchar | 政策名称 |
| source | varchar | 发布单位 |
| url | varchar | 来源链接 |
| content | longtext | 政策内容 |
| publish_time | datetime | 发布时间 |

### 知识库文档表（knowledge_document）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| name | varchar | 文档名称 |
| source_type | varchar | upload/crawler |
| source_url | varchar | 原始来源 |
| file_path | varchar | 文件路径 |
| status | varchar | parsing/indexed/failed |
| chunk_count | int | Chunk 数量 |
| create_time | datetime | 创建时间 |

### 爬虫任务表（crawler_task）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| spider_name | varchar | 爬虫名称 |
| status | varchar | pending/running/success/failed/stopped |
| start_time | datetime | 开始时间 |
| end_time | datetime | 结束时间 |
| data_count | int | 采集数量 |
| error_message | text | 错误信息 |
| log | longtext | 执行日志 |

### 会话表（conversation）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| user_id | bigint | 用户 ID |
| thread_id | varchar | LangGraph 线程 ID |
| title | varchar | 会话标题 |
| create_time | datetime | 创建时间 |

### 消息表（message）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| conversation_id | bigint | 会话 ID |
| role | varchar | user/assistant/tool |
| content | longtext | 消息内容 |
| create_time | datetime | 创建时间 |

### 报告表（report）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| report_type | varchar | company/industry/compare/daily/weekly/monthly |
| title | varchar | 报告标题 |
| query | text | 用户请求 |
| content | longtext | 报告正文 |
| status | varchar | generating/success/failed |
| create_time | datetime | 创建时间 |

### 用户画像表（user_profile）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| user_id | bigint | 用户 ID |
| profile_json | json | 用户偏好 |
| update_time | datetime | 更新时间 |

---

## 八、错误编码

| 编码 | 含义 |
| --- | --- |
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未登录或 Token 无效 |
| 403 | 无权限 |
| 404 | 数据不存在 |
| 409 | 数据重复 |
| 422 | 数据校验失败 |
| 500 | 服务内部错误 |
| 501 | AI 模型调用失败 |
| 502 | RAG 检索失败 |
| 503 | 爬虫任务启动失败 |
| 504 | Agent/工作流执行失败 |
| 505 | OCR/文档解析失败 |
| 506 | 向量库服务失败 |
| 507 | MCP 工具调用失败 |

统一返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

## 九、页面清单

| 页面 | 所属端 | 说明 |
| --- | --- | --- |
| 登录页 | 全部 | 登录、鉴权 |
| 情报首页 | 全部 | 今日数据、热点企业、热点新闻 |
| 新闻列表 | 管理/分析端 | 搜索、筛选、查看详情 |
| 企业列表 | 管理/分析端 | 企业搜索、行业筛选 |
| 企业详情 | 管理/分析端 | 企业信息、新闻、招聘、趋势 |
| AI 智能问答 | 全部 | 流式问答、来源引用 |
| 知识库管理 | 管理端 | 文档上传、删除、检索测试 |
| Agent 工具页 | 管理端 | Tool 列表、调用测试 |
| 爬虫任务 | 管理端 | 启停任务、日志、统计 |
| 报告中心 | 分析端 | 报告生成、列表、详情 |
| 数据看板 | 分析端 | 新闻/招聘/企业统计 |
| 系统配置 | 管理端 | 模型、爬虫、知识库配置 |

---

## 十、非功能需求

1. **安全性**：密码安全存储；Token/JWT 鉴权；API Key 不写入代码。
2. **稳定性**：爬虫任务支持 Retry；Agent 工具调用失败可重试；关键流程支持 Checkpoint。
3. **性能**：AI 回答支持 SSE；常用统计结果使用 Redis 缓存。
4. **可扩展**：爬虫采用插件化设计；Agent Tool 独立注册；MCP 标准化工具。
5. **可追溯**：RAG 回答保留来源；爬虫记录原始 URL；报告记录生成依据。
6. **可观测**：保存爬虫日志、Agent 执行日志、工作流记录，可选接入 LangSmith。
7. **数据质量**：支持 URL 去重、内容 Hash 去重、无效页面过滤、发布时间校验。

---

## 十一、开发计划（建议里程碑）

| 阶段 | 内容 | 对应技术 |
| --- | --- | --- |
| 1 | FastAPI 基础框架、用户、MySQL | Python / FastAPI / SQLAlchemy |
| 2 | Python 爬虫与数据清洗入库 | httpx / parsel / Scrapy |
| 3 | 文档解析、OCR、知识库 | MinerU / OCR / BGE-M3 |
| 4 | Dense + Sparse + Hybrid + Reranker | Milvus / BM25 / RRF |
| 5 | AI 问答、Prompt、LCEL | LangChain |
| 6 | Agent + Function Calling + Tools | LangChain Agent |
| 7 | LangGraph 情报分析工作流 | LangGraph |
| 8 | Memory、报告生成、自动日报 | LangGraph / Redis / MySQL |
| 9 | MCP Server / Client | FastMCP |
| 10 | Docker 部署、监控、项目演示 | Docker / Linux |

建议开发顺序遵循：

```text
FastAPI
 ↓
爬虫
 ↓
MySQL
 ↓
RAG
 ↓
Agent
 ↓
LangGraph
 ↓
OCR
 ↓
MCP
 ↓
部署与优化
```

---

## 十二、项目展示建议

答辩/面试建议按照“数据入口 → 知识构建 → Agent → 工作流”的顺序展示。

### 1. 演示爬虫

启动指定爬虫，实时展示：

```text
抓取 320 条
 ↓
清洗 287 条
 ↓
去重 35 条
 ↓
新增 252 条
 ↓
MySQL 入库
 ↓
知识库更新
```

### 2. 演示 RAG

上传一份政策 PDF 或企业报告。

提问：

> “这份政策对 AI 企业有哪些影响？”

展示：

- 检索候选。
- Hybrid Search。
- Reranker。
- 最终引用来源。

### 3. 演示 Agent

输入：

> “分析最近一个月 AI Agent 行业的重要事件，并总结三条趋势。”

展示：

```text
Planner
 ↓
News Tool
 ↓
RAG Tool
 ↓
Statistics Tool
 ↓
Analyzer
 ↓
Reporter
```

### 4. 演示企业对比

输入：

> “比较三家 AI 企业最近三个月的新闻、招聘和融资情况。”

展示 LangGraph 并行查询与结果合并。

### 5. 演示自动日报

手动触发日报工作流：

```text
采集
 ↓
筛选
 ↓
聚类
 ↓
分析
 ↓
生成日报
```

### 6. 演示 Memory

同一用户第一次说：

> “我主要关注 AI Agent 和机器人行业。”

之后用户只说：

> “今天有什么值得关注的？”

系统结合长期偏好生成个性化结果。

### 7. 演示 MCP

展示 MCP Server 暴露的工具，并演示 Agent 通过 MCP 调用知识库/数据库工具。

---

## 十三、项目核心亮点（简历/面试版）

### 亮点 1：数据采集闭环

通过 Python 爬虫建立公开互联网情报数据入口，实现“采集 → 清洗 → 去重 → 结构化入库 → 知识库更新”的自动化数据链路。

### 亮点 2：完整 RAG 检索链路

采用 BGE-M3 构建 Dense + Sparse 双路召回，通过 Milvus Hybrid Search + RRF 融合，并使用 Reranker 进行二次排序，最终将高相关上下文注入 LLM。

### 亮点 3：Agent 自主工具调用

基于 LangChain Function Calling 定义 SQL、RAG、搜索、统计等工具，使 Agent 根据用户问题自动规划并选择工具完成复杂情报任务。

### 亮点 4：LangGraph 工作流编排

通过 StateGraph 实现情报分析、企业对比、爬虫入库和自动日报等流程，覆盖并行节点、条件分支、循环、Retry、Checkpoint 与流式执行。

### 亮点 5：MCP 工具标准化

将核心业务能力封装为 MCP Server，通过标准协议供 Agent 调用，提高 Tool 的复用性和扩展性。

### 亮点 6：可追溯的 AI 输出

AI 结论绑定新闻、政策、企业信息与知识库原始来源，使分析结果可回溯、可验证。

---

## 十四、项目最终定位

本项目不是传统的“新闻爬虫 + ChatGPT”项目，而是一个完整的 **AI Agent 数据应用闭环**：

```text
                数据层
                   ↓
       Python 爬虫 + OCR + 文档解析
                   ↓
              数据治理层
                   ↓
         MySQL + Milvus + Redis
                   ↓
             知识增强层
                   ↓
         Dense + Sparse + Rerank
                   ↓
              Agent 层
                   ↓
    LangGraph + Tool Calling + MCP
                   ↓
              应用层
                   ↓
   情报问答 / 企业对比 / 行业分析 / 自动报告
```

最终形成：

> **“从互联网数据采集，到知识库构建，再到 Agent 自主分析与报告生成”的完整 AI 应用项目。**
