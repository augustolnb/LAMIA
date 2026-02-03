"""
Agente Root do Gerador de Posts LinkedIn

Este módulo define o agente root para a aplicação de geração de posts LinkedIn.
Ele usa um agente sequencial com um gerador de post inicial seguido por um loop de refinamento.
"""

from google.adk.agents import LoopAgent, SequentialAgent

from .subagents.post_generator import initial_post_generator
from .subagents.post_refiner import post_refiner
from .subagents.post_reviewer import post_reviewer

# Cria o Agente de Loop de Refinamento
refinement_loop = LoopAgent(
    name="PostRefinementLoop",
    max_iterations=10,
    sub_agents=[
        post_reviewer,
        post_refiner,
    ],
    description="Iteratively reviews and refines a LinkedIn post until quality requirements are met",
)

# Cria o Pipeline Sequencial
root_agent = SequentialAgent(
    name="LinkedInPostGenerationPipeline",
    sub_agents=[
        initial_post_generator,  # Etapa 1: Gera post inicial
        refinement_loop,  # Etapa 2: Revisa e refina em loop
    ],
    description="Generates and refines a LinkedIn post through an iterative review process",
)
