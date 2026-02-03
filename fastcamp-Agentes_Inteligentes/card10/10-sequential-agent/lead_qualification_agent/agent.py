"""
Agente Sequencial com Callback Mínimo

Este exemplo demonstra um pipeline de qualificação de leads com um
before_agent_callback mínimo que inicializa o estado apenas uma vez no início.
"""

from google.adk.agents import SequentialAgent

from .subagents.recommender import action_recommender_agent
from .subagents.scorer import lead_scorer_agent

# Importa os subagentes
from .subagents.validator import lead_validator_agent

# Cria o agente sequencial com callback mínimo
root_agent = SequentialAgent(
    name="LeadQualificationPipeline",
    sub_agents=[lead_validator_agent, lead_scorer_agent, action_recommender_agent],
    description="A pipeline that validates, scores, and recommends actions for sales leads",
)
