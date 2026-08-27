"""Agent：LangGraph + DeepSeek，通过 MCP 客户端调用外部工具。"""
import asyncio
import sys

from langchain_deepseek import ChatDeepSeek
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from app.config.settings import settings as config

SYSTEM_PROMPT = (
    "你是企业智能情报分析助手。根据用户问题自主判断是否需要调用工具"
    "（知识库检索 search_knowledge、新闻查询 query_news、统计 get_statistics）。"
    "调用合适工具后，基于工具结果给出准确、有依据的回答，并尽量标注信息来源。"
    "不要编造工具没有返回的信息。"
)


async def _load_tools():
    """通过 MCP 客户端（stdio）加载 mcp_server.py 暴露的工具。"""
    # stdio 方式：Agent 进程启动 mcp_server.py 作为子进程，通过标准输入输出通信。
    # 这样工具就解耦了——Agent 不直接 import 工具函数，而是走 MCP 协议。
    client = MultiServerMCPClient(
        {
            "intel": {
                "transport": "stdio",
                "command": sys.executable,
                "args": ["-m", "app.agent.mcp_server"],
                "cwd": str(config.ROOT),
            }
        }
    )
    return await client.get_tools()


def build_agent(tools):
    """用 LangGraph 现成的 ReAct 智能体：模型自主决定调用哪些工具。"""
    model = ChatDeepSeek(
        model=config.DEEPSEEK_MODEL,
        api_key=config.DEEPSEEK_KEY,
        api_base=config.DEEPSEEK_BASE_URL,
        temperature=0,
    )
    return create_react_agent(model, tools, prompt=SYSTEM_PROMPT)


async def _run(question):
    tools = await _load_tools()
    agent = build_agent(tools)
    result = await agent.ainvoke({"messages": [("user", question)]})
    return result["messages"]


def ask(question):
    """同步入口：返回 (最终回答, 调用过的工具名列表)。"""
    # asyncio.run 把异步的 MCP 调用和 Agent 执行包成同步接口，方便命令行调用
    messages = asyncio.run(_run(question))
    trace = []
    for m in messages:
        for tc in getattr(m, "tool_calls", None) or []:
            trace.append(tc.get("name", ""))
    answer = messages[-1].content if messages else ""
    return answer, trace
