from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

exercise_agent = Agent(
    name="exercise_agent",
    model=LiteLlm("openai/gpt-4o"),
    instruction=(
        "Você é um especialista em elaboração de material didático para Física e Matemática. "
        "1. Forneça o enunciado claro. "
        "2. Aplique princípios ágeis na resolução: quebre a solução em pequenos 'sprints' lógicos. "
        "3. Forneça o gabarito final."
    )
)

session_service = InMemorySessionService()
runner = Runner(agent=exercise_agent, app_name="exercise_app", session_service=session_service)

async def execute(payload: dict):
    await session_service.create_session(app_name="exercise_app", user_id="lucas", session_id="aula")
    
    prompt = (
        f"Gere 3 exercícios de {payload.get('materia')} sobre o tópico {payload.get('topico')} "
        f"adequados para o nível {payload.get('nivel')}."
    )
    
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    async for event in runner.run_async(user_id="lucas", session_id="aula", new_message=message):
        if event.is_final_response():
            return {"questoes": event.content.parts[0].text}
