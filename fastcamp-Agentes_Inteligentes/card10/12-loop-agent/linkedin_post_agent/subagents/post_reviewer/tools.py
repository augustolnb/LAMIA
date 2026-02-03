"""
Ferramentas para o Agente Revisor de Posts LinkedIn

Este módulo fornece ferramentas para analisar e validar posts do LinkedIn.
"""

from typing import Any, Dict

from google.adk.tools.tool_context import ToolContext


def count_characters(text: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Ferramenta para contar caracteres no texto fornecido e fornecer feedback baseado no tamanho.
    Atualiza review_status no estado baseado nos requisitos de tamanho.

    Args:
        text: O texto para analisar a contagem de caracteres
        tool_context: Contexto para acessar e atualizar o estado da sessão

    Returns:
        Dict[str, Any]: Dicionário contendo:
            - result: 'fail' ou 'pass'
            - char_count: número de caracteres no texto
            - message: mensagem de feedback sobre o tamanho
    """
    char_count = len(text)
    MIN_LENGTH = 1000
    MAX_LENGTH = 1500

    print("\n----------- DEBUG DA FERRAMENTA -----------")
    print(f"Verificando tamanho do texto: {char_count} caracteres")
    print("-------------------------------------------\n")

    if char_count < MIN_LENGTH:
        chars_needed = MIN_LENGTH - char_count
        tool_context.state["review_status"] = "fail"
        return {
            "result": "fail",
            "char_count": char_count,
            "chars_needed": chars_needed,
            "message": f"Post muito curto. Adicione mais {chars_needed} caracteres para atingir o mínimo de {MIN_LENGTH}.",
        }
    elif char_count > MAX_LENGTH:
        chars_to_remove = char_count - MAX_LENGTH
        tool_context.state["review_status"] = "fail"
        return {
            "result": "fail",
            "char_count": char_count,
            "chars_to_remove": chars_to_remove,
            "message": f"Post muito longo. Remova {chars_to_remove} caracteres para atingir o máximo de {MAX_LENGTH}.",
        }
    else:
        tool_context.state["review_status"] = "pass"
        return {
            "result": "pass",
            "char_count": char_count,
            "message": f"Tamanho do post está bom ({char_count} caracteres).",
        }


def exit_loop(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Chame esta função APENAS quando o post atender todos os requisitos de qualidade,
    sinalizando que o processo iterativo deve terminar.

    Args:
        tool_context: Contexto para execução da ferramenta

    Returns:
        Dicionário vazio
    """
    print("\n----------- SAÍDA DO LOOP ACIONADA -----------")
    print("Revisão do post concluída com sucesso")
    print("O loop será encerrado agora")
    print("----------------------------------------------\n")

    tool_context.actions.escalate = True
    return {}
