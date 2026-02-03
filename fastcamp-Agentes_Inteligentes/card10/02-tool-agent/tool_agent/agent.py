from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm 
from google.adk.tools.langchain_tool import LangchainTool
from langchain_community.tools import DuckDuckGoSearchRun # executar `pip3.12 install -U ddgs` antes
from datetime import datetime

MODEL_GEMINI = "gemini-2.0-flash"
MODEL_GPT = "openai/gpt-4.1-nano-2025-04-14"
MODEL_CLAUDE = "anthropic/claude-haiku-4-5-20251001"
MODEL_CLAUDE_OPUS = "anthropic/claude-opus-4-5-20251101"
# instancia duck duck go
duckduckgo_tool_instance = DuckDuckGoSearchRun(
    max_results = 5,
)

# add ddg_search como uma ferramenta adk
adk_duckduckgo_tool = LangchainTool(
    tool=duckduckgo_tool_instance,
)

def get_current_time() -> dict:
    """
    Get the current time in the format YYYY-MM-DD HH:MM:SS
    """
    return {
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

root_agent = Agent(
    name="tool_agent",
    model=LiteLlm(model=MODEL_CLAUDE_OPUS),
    description = "Researches on a given topic using DuckDuckGo Search.",
    instruction = """
    You are a Research AI agent.
    Use DuckDuckGo search to find recent and relevant information on the provided topic.
    **Do not** add information on your own apart from what you found after the DuckDuckGo search.
    Summarize key points, statistics, and insights in bullet points.
    You are a helpful assistant that can use the following tools:
    - get_current_time
    - adk_duckduckgo_tool
    """,
    tools = [get_current_time, adk_duckduckgo_tool],
)
