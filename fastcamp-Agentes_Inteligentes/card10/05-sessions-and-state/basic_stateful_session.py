import asyncio
import uuid
from pathlib import Path

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from question_answering_agent import root_agent

# Carregar .env da pasta do agente
env_path = Path(__file__).parent / "question_answering_agent" / ".env"
load_dotenv(dotenv_path=env_path)


async def main():
    session_service_stateful = InMemorySessionService()

    initial_state = {
        "user_name": "Lucas Augusto",
        "user_preferences": """
            🌴 Um engenheiro eletricista das terras tropicais, entusiasta em IA e IOT;
            🐍 Desenvolvedor Python em projetos autônomos;
            🌵 Trabalhando como professor de matemática e física;
            🐢 Estudando sempre que possível .
        """,
    }

    APP_NAME = "Augusto Bot"
    USER_ID = "lucas_augusto"
    SESSION_ID = str(uuid.uuid4())

    # Criar sessão com await
    stateful_session = await session_service_stateful.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state=initial_state,
    )
    print("Nova Sessão Criada:")
    print(f"\tID da Sessão: {SESSION_ID}")

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service_stateful,
    )

    new_message = types.Content(
        role="user", parts=[types.Part(text="Com o que o usuário trabalha atualmente?")]
    )

    # Usar run_async ao invés de run
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=new_message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(f"Resposta Final: {event.content.parts[0].text}")

    print("==== Explorando Eventos da Sessão ====")
    
    # Obter sessão com await
    session = await session_service_stateful.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    # Log final Session state
    print("=== Estado Final da Sessão ===")
    for key, value in session.state.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
