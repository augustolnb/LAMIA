from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

pkm_agent = Agent(
    name="pkm_agent",
    model=LiteLlm("openai/gpt-4o"),
    instruction=(
        "Você é um especialista em Gestão do Conhecimento Pessoal (PKM) e Obsidian. "
        "Transforme o conteúdo recebido em uma nota no formato Markdown para o método Zettelkasten. "
        "Inclua Frontmatter (YAML) compatível com Dataview. "
        "REGRAS IMPORTANTES DE FORMATAÇÃO: "
        "1. Nunca adicione o caractere '#' dentro da lista de tags nas propriedades YAML, use apenas a palavra (ex: tags: [projetos]). "
        "2. Não utilize as tags ou tipos de nota GES e TASK nos seus templates."
    )
)

session_service = InMemorySessionService()
runner = Runner(agent=pkm_agent, app_name="pkm_app", session_service=session_service)

async def execute(payload: dict):
    await session_service.create_session(app_name="pkm_app", user_id="lucas", session_id="aula")
    
    prompt = f"Formate o seguinte conteúdo de aula em Markdown para Obsidian:\n\n{payload.get('content')}"
    
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    async for event in runner.run_async(user_id="lucas", session_id="aula", new_message=message):
        if event.is_final_response():
            return {"markdown": event.content.parts[0].text}
