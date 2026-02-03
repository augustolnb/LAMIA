"""
Agente Root do Monitor de Sistema

Este módulo define o agente root para a aplicação de monitoramento de sistema.
Ele usa um agente paralelo para coleta de informações do sistema e um pipeline
sequencial para o fluxo geral.
"""

from google.adk.agents import ParallelAgent, SequentialAgent

from .subagents.cpu_info_agent import cpu_info_agent
from .subagents.disk_info_agent import disk_info_agent
from .subagents.memory_info_agent import memory_info_agent
from .subagents.synthesizer_agent import system_report_synthesizer

# --- 1. Cria Agente Paralelo para coletar informações simultaneamente ---
system_info_gatherer = ParallelAgent(
    name="system_info_gatherer",
    sub_agents=[cpu_info_agent, memory_info_agent, disk_info_agent],
)

# --- 2. Cria Pipeline Sequencial para coletar info em paralelo, depois sintetizar ---
root_agent = SequentialAgent(
    name="system_monitor_agent",
    sub_agents=[system_info_gatherer, system_report_synthesizer],
)
