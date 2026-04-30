from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

theory_agent = Agent(
    name="theory_agent",
    model=LiteLlm("openai/gpt-4o"),
    instruction=(
        "Você é um tutor especialista em Física e Matemática para Engenharia. "
        "Sua função é explicar conceitos complexos de forma didática e prática. "
        "Sempre use analogias com o mundo real e exemplos de engenharia elétrica."
    )
)

session_service = InMemorySessionService()
runner = Runner(agent=theory_agent, app_name="theory_app", session_service=session_service)

async def execute(payload: dict):
    await session_service.create_session(app_name="theory_app", user_id="lucas", session_id="aula")
    
    prompt = (
        f"Explique o tópico {payload.get('topico')} da disciplina de {payload.get('materia')} "
        f"para um aluno do nível {payload.get('nivel')}. O foco da aula é: {payload.get('foco')}."
    )
    
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    async for event in runner.run_async(user_id="lucas", session_id="aula", new_message=message):
        if event.is_final_response():
            return {"explicacao": event.content.parts[0].text}
