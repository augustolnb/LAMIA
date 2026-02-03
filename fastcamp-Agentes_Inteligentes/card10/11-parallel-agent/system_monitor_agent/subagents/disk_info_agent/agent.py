"""
Agente de Informações de Disco

Este agente é responsável por coletar e analisar informações de disco.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from .tools import get_disk_info

# --- Constantes ---
GEMINI_MODEL = "gemini-2.0-flash"
CLAUDE_MODEL = "anthropic/claude-haiku-4-5-20251001"
MODEL_GPT = "openai/gpt-4.1-nano-2025-04-14"

# Agente de Informações de Disco
disk_info_agent = LlmAgent(
    name="DiskInfoAgent",
    model=LiteLlm(model=MODEL_GPT),
    instruction="""You are a Disk Information Agent.
    
    When asked for system information, you should:
    1. Use the 'get_disk_info' tool to gather disk data
    2. Analyze the returned dictionary data
    3. Format this information into a concise, clear section of a system report
    
    The tool will return a dictionary with:
    - result: Core disk information including partitions
    - stats: Key statistical data about storage usage
    - additional_info: Context about the data collection
    
    Format your response as a well-structured report section with:
    - Partition information
    - Storage capacity and usage
    - Any storage concerns (high usage > 85%)
    
    IMPORTANT: You MUST call the get_disk_info tool. Do not make up information.
    """,
    description="Gathers and analyzes disk information",
    tools=[get_disk_info],
    output_key="disk_info",
)
