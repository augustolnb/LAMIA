"""Tools de interação medicamentosa expostas ao safety_agent.

O conhecimento farmacológico vive em src/interactions.py.
Nesse doc ficam as assinaturas que o ADK converte em function declarations para o LLM.
"""

from __future__ import annotations

import re

from src.interactions import evaluate_all_pairs, evaluate_pair

_SEM_INTERACAO = "Sem interação conhecida na base local."


def _coerce_drug_list(drugs: list[str] | str | None) -> list[str]:
    """Aceita a lista de fármacos mesmo quando o modelo a envia como string única."""
    if drugs is None:
        return []
    if isinstance(drugs, str):
        return [parte.strip() for parte in re.split(r"[,;\n]", drugs) if parte.strip()]
    return [str(d).strip() for d in drugs if str(d).strip()]


def check_drug_interaction(drug_a: str, drug_b: str) -> dict:
    """Consulta a base local de interações entre DOIS fármacos.

    Args:
        drug_a: Nome do primeiro fármaco (aceita marca comercial ou nome em português).
        drug_b: Nome do segundo fármaco.

    Returns:
        Dicionário com "par", "nivel" (Crítico, Moderado ou Baixo), "mecanismo" e "descricao".
    """
    alerta = evaluate_pair(drug_a, drug_b)
    if alerta is None:
        return {
            "par": f"{drug_a} + {drug_b}",
            "nivel": "Baixo",
            "mecanismo": "Nenhum",
            "descricao": _SEM_INTERACAO,
        }
    return alerta


def check_all_drug_interactions(drugs: list[str]) -> dict:
    """Avalia de uma só vez TODAS as combinações possíveis de uma lista de fármacos.

    Esta é a ferramenta a usar quando há mais de dois fármacos: o pareamento
    N*(N-1)/2 é feito internamente em Python, então nenhuma combinação é perdida,
    independentemente do tamanho da lista.

    Args:
        drugs: Lista completa de fármacos do paciente.

    Returns:
        Dicionário com "pares_esperados", "pares_avaliados" e "alertas" (apenas os
        pares com achado relevante; pares sem interação conhecida são contados mas
        não listados).
    """
    farmacos = _coerce_drug_list(drugs)
    resultado = evaluate_all_pairs(farmacos)
    n = len(resultado["farmacos_normalizados"])
    resultado["pares_esperados"] = n * (n - 1) // 2
    return resultado
