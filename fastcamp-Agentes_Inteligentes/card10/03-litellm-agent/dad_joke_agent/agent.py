import os
import random

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

model = LiteLlm(model="anthropic/claude-haiku-4-5-20251001")

def get_dad_joke():
    jokes = [
        "No almoço de domingo, é pavê ou pra comê?",
        "Sabe por que a plantinha não foi atendida no hospital? Porque lá só tinha médico de plantão.",
        "Você conhece a piada do pônei? Pô, nei eu.",
        "Qual é o rei dos queijos? O Reiqueijão.",
        "Por que o jacaré tirou o filho da escola? Porque ele réptil de ano.",
        "O que o tijolo falou para o outro? Há um ciúme (cimento) entre nós.",
        "Sabe o que o pagodeiro foi fazer na igreja? Foi cantar Pá God.",
        "Por que o pinheiro não se perde na floresta? Porque ele tem uma pinha (um mapinha).",
    ]
    return random.choice(jokes)


root_agent = Agent(
    name="dad_joke_agent",
    model=model,
    description="Dad joke agent",
    instruction="""
    You are a helpful assistant that can tell dad jokes. 
    Only use the tool `get_dad_joke` to tell jokes.
    """,
    tools=[get_dad_joke],
)
