"""命令行演示：直接向 Agent 提问（走 MCP 工具）。

用法：python scripts/demo_ask.py "最近 AI 行业有什么新闻"
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.agent.agent import ask  # noqa: E402


def main():
    if len(sys.argv) < 2:
        print('用法: python scripts/demo_ask.py "你的问题"')
        return
    question = " ".join(sys.argv[1:])
    answer, trace = ask(question)
    if trace:
        print("工具调用:", " -> ".join(trace))
    print("回答:", answer)


if __name__ == "__main__":
    main()
