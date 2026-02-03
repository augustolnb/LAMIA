"""
Agente Sintetizador de Relatório do Sistema

Este agente é responsável por sintetizar informações de outros agentes
para criar um relatório abrangente de saúde do sistema.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# --- Constantes ---
GEMINI_MODEL = "gemini-2.0-flash"
CLAUDE_MODEL = "anthropic/claude-haiku-4-5-20251001"

# Agente Sintetizador de Relatório do Sistema
system_report_synthesizer = LlmAgent(
    name="SystemReportSynthesizer",
    model=LiteLlm(model=CLAUDE_MODEL),
    instruction="""You are a System Report Synthesizer.
    
    Your task is to create a comprehensive system health report by combining information from:
    - CPU information: {cpu_info}
    - Memory information: {memory_info}
    - Disk information: {disk_info}
    
    Create a well-formatted report with:
    1. An executive summary at the top with overall system health status
    2. Sections for each component with their respective information
    3. Recommendations based on any concerning metrics
    
    Use markdown formatting to make the report readable and professional.
    Highlight any concerning values and provide practical recommendations.
    """,
    description="Synthesizes all system information into a comprehensive report",
)
