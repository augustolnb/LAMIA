"""
Exemplo de Callbacks Before e After do Modelo

Este exemplo demonstra o uso de callbacks do modelo 
para filtrar conteúdo e registrar interações com o modelo.
"""

import copy
from datetime import datetime
from typing import Optional

from google.adk.models.lite_llm import LiteLlm 
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types


def before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Este callback é executado antes do modelo processar uma requisição.
    Ele filtra conteúdo inapropriado e registra informações da requisição.

    Args:
        callback_context: Contém informações de estado e contexto
        llm_request: A requisição LLM sendo enviada

    Returns:
        LlmResponse opcional para sobrescrever a resposta do modelo
    """
    # Obtém o estado e o nome do agente
    state = callback_context.state
    agent_name = callback_context.agent_name

    # Extrai a última mensagem do usuário
    last_user_message = ""
    if llm_request.contents and len(llm_request.contents) > 0:
        for content in reversed(llm_request.contents):
            if content.role == "user" and content.parts and len(content.parts) > 0:
                if hasattr(content.parts[0], "text") and content.parts[0].text:
                    last_user_message = content.parts[0].text
                    break

    # Registra a requisição
    print("=== REQUISIÇÃO DO MODELO INICIADA ===")
    print(f"Agente: {agent_name}")
    if last_user_message:
        print(f"Mensagem do usuário: {last_user_message[:100]}...")
        # Armazena para uso posterior
        state["last_user_message"] = last_user_message
    else:
        print("Mensagem do usuário: <vazia>")

    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Verifica conteúdo inapropriado
    if last_user_message and "feiura" in last_user_message.lower():
        print("=== CONTEÚDO INAPROPRIADO BLOQUEADO ===")
        print("Texto bloqueado contendo feiura")

        print("[BEFORE MODEL] ⚠️ Requisição bloqueada devido a conteúdo inapropriado")

        # Retorna uma resposta para pular a chamada do modelo
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text="Eu não posso responder mensagem contendo feiura. "
                        "Por favor, reescreva sua mensagem sem feiura."
                    )
                ],
            )
        )

    # Registra o horário de início para cálculo de duração
    # Converte para string ISO para serialização JSON
    state["model_start_time"] = datetime.now().isoformat()
    print("[BEFORE MODEL] ✓ Requisição aprovada para processamento")

    # Retorna None para prosseguir com a requisição normal do modelo
    return None


def after_model_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """
    Callback simples que substitui palavras negativas por alternativas mais positivas.

    Args:
        callback_context: Contém informações de estado e contexto
        llm_response: A resposta LLM recebida

    Returns:
        LlmResponse opcional para sobrescrever a resposta do modelo
    """
    # Registra a conclusão
    print("[AFTER MODEL] Processando resposta")

    # Pula o processamento se a resposta estiver vazia ou não tiver conteúdo de texto
    if not llm_response or not llm_response.content or not llm_response.content.parts:
        return None

    # Extrai o texto da resposta
    response_text = ""
    for part in llm_response.content.parts:
        if hasattr(part, "text") and part.text:
            response_text += part.text

    if not response_text:
        return None

    # Substituições simples de palavras
    replacements = {
        "problem": "challenge",
        "difficult": "complex",
    }

    # Realiza as substituições
    modified_text = response_text
    modified = False

    for original, replacement in replacements.items():
        if original in modified_text.lower():
            modified_text = modified_text.replace(original, replacement)
            modified_text = modified_text.replace(
                original.capitalize(), replacement.capitalize()
            )
            modified = True

    # Retorna a resposta modificada se houve alterações
    if modified:
        print("[AFTER MODEL] ↺ Texto da resposta modificado")

        modified_parts = [copy.deepcopy(part) for part in llm_response.content.parts]
        for i, part in enumerate(modified_parts):
            if hasattr(part, "text") and part.text:
                modified_parts[i].text = modified_text

        return LlmResponse(content=types.Content(role="model", parts=modified_parts))

    # Retorna None para usar a resposta original
    return None


# Cria o Agente
root_agent = LlmAgent(
    name="content_filter_agent",
    #model="gemini-2.0-flash",
    model=LiteLlm(model="anthropic/claude-haiku-4-5-20251001"),
    description="An agent that demonstrates model callbacks for content filtering and logging",
    instruction="""
    You are a helpful assistant.
    
    Your job is to:
    - Answer user questions concisely
    - Provide factual information
    - Be friendly and respectful
    """,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
