"""
Exemplo de Callbacks Before e After do Agente

Este exemplo demonstra como usar tanto before_agent_callback quanto after_agent_callback 
para fins de logging.
"""

from datetime import datetime
from typing import Optional

from google.adk.models.lite_llm import LiteLlm 
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types


def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Callback simples que registra quando o agente começa a processar uma requisição.

    Args:
        callback_context: Contém informações de estado e contexto

    Returns:
        None para continuar com o processamento normal do agente
    """
    # Obtém o estado da sessão
    state = callback_context.state

    # Registra o timestamp
    timestamp = datetime.now()

    # Define o nome do agente se não estiver presente
    if "agent_name" not in state:
        state["agent_name"] = "SimpleChatBot"

    # Inicializa o contador de requisições
    if "request_counter" not in state:
        state["request_counter"] = 1
    else:
        state["request_counter"] += 1

    # Armazena o horário de início para cálculo de duração no after_agent_callback
    # Converte para string ISO para serialização JSON
    state["request_start_time"] = timestamp.isoformat()

    # Registra a requisição
    print("=== EXECUÇÃO DO AGENTE INICIADA ===")
    print(f"Requisição #: {state['request_counter']}")
    print(f"Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

    # Imprime no console
    print(f"\n[BEFORE CALLBACK] Agente processando requisição #{state['request_counter']}")

    return None


def after_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Callback simples que registra quando o agente termina de processar uma requisição.

    Args:
        callback_context: Contém informações de estado e contexto

    Returns:
        None para continuar com o processamento normal do agente
    """
    # Obtém o estado da sessão
    state = callback_context.state

    # Calcula a duração da requisição se o horário de início estiver disponível
    timestamp = datetime.now()
    duration = None
    if "request_start_time" in state:
        # Converte a string ISO de volta para datetime
        start_time = datetime.fromisoformat(state["request_start_time"])
        duration = (timestamp - start_time).total_seconds()

    # Registra a conclusão
    print("=== EXECUÇÃO DO AGENTE CONCLUÍDA ===")
    print(f"Requisição #: {state.get('request_counter', 'Desconhecido')}")
    if duration is not None:
        print(f"Duração: {duration:.2f} segundos")

    # Imprime no console
    print(
        f"[AFTER CALLBACK] Agente concluiu requisição #{state.get('request_counter', 'Desconhecido')}"
    )
    if duration is not None:
        print(f"[AFTER CALLBACK] Processamento levou {duration:.2f} segundos")

    return None


# Cria o Agente
root_agent = LlmAgent(
    name="before_after_agent",
    #model="gemini-2.0-flash",
    model=LiteLlm(model="anthropic/claude-haiku-4-5-20251001"),
    description="A basic agent that demonstrates before and after agent callbacks",
    instruction="""
    You are a friendly greeting agent. Your name is {agent_name}.
    
    Your job is to:
    - Greet users politely
    - Respond to basic questions
    - Keep your responses friendly and concise
    """,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
)
