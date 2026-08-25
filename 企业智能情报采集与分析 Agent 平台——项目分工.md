# 企业智能情报采集与分析 Agent 平台
## 三人小组项目分工

### 成员A：爬虫 + MySQL
- 负责 Python 爬虫开发
- 采集新闻、企业等公开信息
- 完成数据清洗、去重
- 设计 MySQL 数据表
- 实现爬虫数据入库

**主要成果：** 爬虫模块、MySQL 数据库、原始情报数据。

### 成员B：RAG + Agent
- 负责知识库构建
- 完成文本切分、Embedding、向量存储
- 实现 RAG 检索
- 开发 Agent Tools
- 实现企业/新闻/RAG 等工具调用

**主要成果：** RAG 模块、Agent、工具调用功能。

### 成员C：FastAPI + LangGraph
- 负责 FastAPI 后端接口
- 实现 AI 问答、爬虫、知识库相关 API
- 使用 LangGraph 组织 Agent 工作流
- 负责三个模块的最终联调
- 负责项目运行和接口测试

**主要成果：** FastAPI、LangGraph 工作流、系统联调。

### 三人共同完成
- README.md
- PPT 和项目汇报
- 功能测试
- 答辩演示
- 最终项目部署

### 项目核心流程

```text
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
FastAPI
 ↓
AI 情报分析
```

**目标：3 人分工明确，各自负责一个核心模块，最后完成整体联调。**