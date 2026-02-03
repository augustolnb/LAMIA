"""
Agente de Informações de CPU

Este agente é responsável por coletar e analisar informações de CPU.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from .tools import get_cpu_info

# --- Constantes ---
GEMINI_MODEL = "gemini-2.0-flash"
CLAUDE_MODEL = "anthropic/claude-haiku-4-5-20251001"
MODEL_GPT = "openai/gpt-4.1-nano-2025-04-14"

# Agente de Informações de CPU
cpu_info_agent = LlmAgent(
    name="CpuInfoAgent",
    model=LiteLlm(model=MODEL_GPT),
    instruction="""You are a CPU Information Agent.
    
    When asked for system information, you should:
    1. Use the 'get_cpu_info' tool to gather CPU data
    2. Analyze the returned dictionary data
    3. Format this information into a concise, clear section of a system report
    
    The tool will return a dictionary with:
    - result: Core CPU information
    - stats: Key statistical data about CPU usage
    - additional_info: Context about the data collection
    
    Format your response as a well-structured report section with:
    - CPU core information (physical vs logical)
    - CPU usage statistics
    - Any performance concerns (high usage > 80%)
    
    IMPORTANT: You MUST call the get_cpu_info tool. Do not make up information.
    """,
    description="Gathers and analyzes CPU information",
    tools=[get_cpu_info],
    output_key="cpu_info",
)
