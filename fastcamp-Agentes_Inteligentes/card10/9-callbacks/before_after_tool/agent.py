"""
Exemplo de Callbacks Before e After de Ferramenta

Este exemplo demonstra o uso de callbacks de ferramenta para modificar o comportamento da ferramenta.
"""

import copy
from typing import Any, Dict, Optional

from google.adk.models.lite_llm import LiteLlm 
from google.adk.agents import LlmAgent
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext


# --- Define uma Função de Ferramenta Simples ---
def get_capital_city(country: str) -> Dict[str, str]:
    """
    Recupera a capital de um determinado país.

    Args:
        country: Nome do país

    Returns:
        Dicionário com o resultado da capital
    """
    print(f"[TOOL] Executando ferramenta get_capital_city com país: {country}")

    country_capitals = {
        "united states": "Washington, D.C.",
        "usa": "Washington, D.C.",
        "canada": "Ottawa",
        "france": "Paris",
        "germany": "Berlin",
        "japan": "Tokyo",
        "Brasil": "Brasília",
        "australia": "Canberra",
        "india": "New Delhi",
    }

    # Usa minúsculas para comparação
    result = country_capitals.get(country.lower(), f"Capital não encontrada para {country}")
    print(f"[TOOL] Resultado: {result}")
    print(f"[TOOL] Retornando: {{'result': '{result}'}}")

    return {"result": result}


# --- Define o Callback Before Tool ---
def before_tool_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """
    Callback simples que modifica os argumentos da ferramenta ou pula a chamada da ferramenta.
    """
    tool_name = tool.name
    print(f"[Callback] Antes da chamada da ferramenta '{tool_name}'")
    print(f"[Callback] Args originais: {args}")

    # Se alguém perguntar sobre 'merica, converte para United States
    if tool_name == "get_capital_city" and args.get("country", "").lower() == "merica":
        print("[Callback] Convertendo 'Merica para 'United States'")
        args["country"] = "United States"
        print(f"[Callback] Args modificados: {args}")
        return None

    # Pula a chamada completamente para países restritos
    if (
        tool_name == "get_capital_city"
        and args.get("country", "").lower() == "restricted"
    ):
        print("[Callback] Bloqueando país restrito")
        return {"result": "O acesso a esta informação foi restrito."}

    print("[Callback] Prosseguindo com chamada normal da ferramenta")
    return None


# --- Define o Callback After Tool ---
def after_tool_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
) -> Optional[Dict]:
    """
    Callback simples que modifica a resposta da ferramenta após a execução.
    """
    tool_name = tool.name
    print(f"[Callback] Após a chamada da ferramenta '{tool_name}'")
    print(f"[Callback] Args usados: {args}")
    print(f"[Callback] Resposta original: {tool_response}")

    original_result = tool_response.get("result", "")
    print(f"[Callback] Resultado extraído: '{original_result}'")

    # Adiciona uma nota para qualquer resposta de capital dos EUA
    if tool_name == "get_capital_city" and "washington" in original_result.lower():
        print("[Callback] DETECTADA CAPITAL DOS EUA - adicionando nota de repúdio!")

        # Cria uma cópia modificada da resposta
        modified_response = copy.deepcopy(tool_response)
        modified_response["result"] = (
            f"{original_result} (Nota: Esta é a capital dos EUA. 🇺🇸)"
        )
        modified_response["note_added_by_callback"] = True

        print(f"[Callback] Resposta modificada: {modified_response}")
        return modified_response

    print("[Callback] Nenhuma modificação necessária, retornando resposta original")
    return None


# Cria o Agente
root_agent = LlmAgent(
    name="tool_callback_agent",
    #model="gemini-2.0-flash",
    model=LiteLlm(model="anthropic/claude-haiku-4-5-20251001"),
    description="An agent that demonstrates tool callbacks by looking up capital cities",
    instruction="""
    You are a helpful geography assistant.
    
    Your job is to:
    - Find capital cities when asked using the get_capital_city tool
    - Use the exact country name provided by the user
    - ALWAYS return the EXACT result from the tool, without changing it
    - When reporting a capital, display it EXACTLY as returned by the tool
    
    Examples:
    - "What is the capital of France?" → Use get_capital_city with country="France"
    - "Tell me the capital city of Japan" → Use get_capital_city with country="Japan"
    """,
    tools=[get_capital_city],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)
