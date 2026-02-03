"""
Agente Pontuador de Lead

Este agente é responsável por pontuar o nível de qualificação de um lead
com base em vários critérios.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm 

# --- Constantes ---
GEMINI_MODEL = "gemini-2.0-flash"
CLAUDE_MODEL = "anthropic/claude-haiku-4-5-20251001"

# Cria o agente pontuador
lead_scorer_agent = LlmAgent(
    name="LeadScorerAgent",
    model=LiteLlm(model=CLAUDE_MODEL),
    instruction="""You are a Lead Scoring AI.
    
    Analyze the lead information and assign a qualification score from 1-10 based on:
    - Expressed need (urgency/clarity of problem)
    - Decision-making authority
    - Budget indicators
    - Timeline indicators
    
    Output ONLY a numeric score and ONE sentence justification.
    
    Example output: '8: Decision maker with clear budget and immediate need'
    Example output: '3: Vague interest with no timeline or budget mentioned'
    """,
    description="Scores qualified leads on a scale of 1-10.",
    output_key="lead_score",
)
