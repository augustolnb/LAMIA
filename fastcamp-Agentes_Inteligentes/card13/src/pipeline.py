"""Orquestração de um caso clínico via extractor_agent + report_agent (ADK), em async.

A checagem de segurança é determinística (src/interactions.py, sem LLM) e roda em Python
entre os dois agentes — ver run_case_async() e _format_report_request().
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import uuid

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import ValidationError

from src.agents import CasoExtraido, build_extractor_agent, build_report_agent
from src.interactions import evaluate_all_pairs

logger = logging.getLogger(__name__)

APP_NAME = "ag-clinico-adk"

_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)
_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def _parse_json_state(raw: str | None, schema: type | None = None) -> dict | None:
    """Faz parse de um valor de session.state como JSON puro (sem ADK output_schema).

    A DeepSeek não suporta o response_format estrito que o ADK usaria para validar
    output_schema nativamente (erro "This response_format type is unavailable now"),
    então os agentes retornam texto livre instruído a ser JSON puro, e o parsing/
    validação acontece aqui, em Python — tolerante a cercas de código markdown e a
    frases de preâmbulo (ex.: "Vou verificar a interação...{...}") que o modelo às
    vezes adiciona apesar da instrução de responder só com JSON.
    """
    if raw is None:
        return None
    text = _CODE_FENCE_RE.sub("", raw).strip()
    match = _JSON_OBJECT_RE.search(text)
    if match:
        text = match.group(0)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    if schema is not None:
        try:
            schema.model_validate(data)
        except ValidationError:
            return None
    return data


def _build_safety_report(extracted: dict | None, raw_alertas: dict | None) -> dict:
    """Monta o relatório de segurança de forma determinística, em Python.

    O cruzamento N*(N-1)/2 NÃO depende do safety_agent: ele é recalculado aqui pelo
    motor local, então uma falha de chamada ao LLM não pode mais zerar a checagem.
    O resultado do agente é usado apenas para registrar divergência (observabilidade).

    Antes de contar fármacos ou gerar pares, a lista extraída passa por
    deduplicate_drugs() (via evaluate_all_pairs): menções repetidas da MESMA
    substância — variação de dose/via ("Prednisone 80mg" x "60mg", "heparin" x
    "Heparin IV") ou sinônimo marca/genérico exato ("Xanax" x "alprazolam") —
    contam como UM fármaco, não dois, evitando alerta artificial de duplicação
    entre grafias da mesma prescrição.
    """
    farmacos = list(extracted["farmacos"]) if extracted else []
    resultado = evaluate_all_pairs(farmacos)
    entidades = resultado["farmacos_normalizados"]
    duplicatas = resultado["duplicatas_removidas"]
    n_entidades = len(entidades)
    n_pares_esperados = n_entidades * (n_entidades - 1) // 2

    if n_entidades < 2:
        motivo = (
            f"Checagem dispensada: {n_entidades} fármaco(s) distinto(s) identificado(s) "
            "(mínimo 2 necessários para cruzar combinações)."
        )
        if duplicatas:
            motivo += (
                f" ({duplicatas} menção(ões) redundante(s) da mesma substância descartada(s) "
                "antes da contagem.)"
            )
        return {
            "checagem_realizada": False,
            "pares_esperados": 0,
            "pares_avaliados": 0,
            "duplicatas_removidas": duplicatas,
            "alertas": [],
            "divergencia_agente": None,
            "motivo": motivo,
        }

    alertas = resultado["alertas"]
    avaliados = resultado["pares_avaliados"]

    if avaliados != n_pares_esperados:  # invariante do motor; não deve ocorrer
        motivo = (
            f"ATENÇÃO: esperava-se {n_pares_esperados} combinação(ões) para {n_entidades} "
            f"fármaco(s) distinto(s), mas {avaliados} foi(ram) avaliada(s)."
        )
    else:
        motivo = (
            f"Verificação determinística concluída: {avaliados} combinação(ões) avaliada(s) "
            f"para {n_entidades} fármaco(s) distinto(s)"
        )
        if duplicatas:
            motivo += (
                f" ({duplicatas} menção(ões) redundante(s) da mesma substância descartada(s) "
                "antes do cruzamento)"
            )
        motivo += f"; {len(alertas)} alerta(s) identificado(s)."

    divergencia = None
    if raw_alertas is not None:
        n_agente = len(raw_alertas.get("alertas", []))
        if n_agente < len(alertas):
            divergencia = (
                f"Divergência: o safety_agent reportou {n_agente} alerta(s), a base local "
                f"identificou {len(alertas)}. Prevalece o resultado determinístico."
            )

    return {
        "checagem_realizada": True,
        "duplicatas_removidas": duplicatas,
        "pares_esperados": n_pares_esperados,
        "pares_avaliados": avaliados,
        "alertas": alertas,
        "divergencia_agente": divergencia,
        "motivo": motivo,
    }


def _format_report_request(caso_texto: str, extracted: dict | None, safety_report: dict) -> str:
    """Monta a mensagem enviada ao report_agent, com o safety_report determinístico embutido
    VERBATIM (json.dumps), sem nenhum LLM intermediário reescrevendo ou resumindo esses dados.

    Antes desta função, report_agent era chamado pelo router_agent como um AgentTool, cujo
    texto de handoff é composto livremente pelo LLM do router — o que podia introduzir
    incoerência entre o JSON de segurança e a Avaliação escrita (ex.: o router parafraseando
    "checagem dispensada" ao lado da lista de alertas de um caso totalmente diferente da
    checagem real). Aqui o Python é quem escreve o handoff, então o texto que report_agent
    recebe é sempre exatamente o safety_report que também aparece no JSON retornado por
    run_case()/run_case_async() — as duas saídas não podem mais divergir.
    """
    return (
        f"Texto original do caso:\n{caso_texto}\n\n"
        f"Dados extraídos (JSON):\n{json.dumps(extracted, ensure_ascii=False)}\n\n"
        "Resultado da checagem de segurança (JSON, calculado deterministicamente em Python — "
        "use exatamente estes dados, não reavalie):\n"
        f"{json.dumps(safety_report, ensure_ascii=False)}"
    )


async def _run_single_agent(agent, message_text: str) -> tuple[dict, str | None]:
    """Executa um único LlmAgent isolado (sessão própria) e devolve seu session.state final.

    Usado no lugar do router_agent para extractor_agent e report_agent: cada um roda como
    uma chamada direta e independente, sem um LLM orquestrador no meio compondo o texto de
    entrada do próximo passo.
    """
    session_service = InMemorySessionService()
    user_id = "demo-user"
    session_id = str(uuid.uuid4())
    await session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
    runner = Runner(app_name=APP_NAME, agent=agent, session_service=session_service)
    message = types.Content(role="user", parts=[types.Part.from_text(text=message_text)])

    erro: str | None = None
    try:
        async for _ in runner.run_async(user_id=user_id, session_id=session_id, new_message=message):
            pass
    except Exception as exc:  # noqa: BLE001 — um caso ruim não pode derrubar o lote
        erro = f"{type(exc).__name__}: {exc}"
        logger.exception("Falha na execução de %r", agent.name)

    session = await session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
    state = session.state if session is not None else {}
    return dict(state), erro


async def run_case_async(case: dict) -> dict:
    """Executa o pipeline de agentes ADK sobre um caso clínico (API async do ADK).

    extractor_agent e report_agent são chamados diretamente (sem router_agent no meio); a
    checagem de segurança é feita deterministicamente em Python (src/interactions.py) entre os
    dois passos, e seu resultado é o mesmo texto embutido no pedido enviado a report_agent —
    ver _format_report_request(). Isso garante que o JSON de segurança retornado e o texto do
    relatório nunca divirjam entre si.

    Args:
        case: dict com "description", "transcription" e "medical_specialty".

    Returns:
        dict com "medical_specialty", "extracted", "safety_report" e "relatorio".
    """
    especialidade = case.get("medical_specialty")
    caso_texto = (
        f"Descrição: {case['description']}\n\n"
        f"Transcrição completa:\n{case['transcription']}"
    )

    extractor_state, erro_extractor = await _run_single_agent(build_extractor_agent(), caso_texto)
    extracted = _parse_json_state(extractor_state.get("extracted"), schema=CasoExtraido)
    if extracted is None:
        logger.warning(
            "extractor_agent não retornou resultado válido para o caso %r", especialidade
        )

    safety_report = _build_safety_report(extracted, None)

    report_message = _format_report_request(caso_texto, extracted, safety_report)
    report_state, erro_report = await _run_single_agent(build_report_agent(), report_message)
    relatorio = report_state.get("relatorio")
    if relatorio is None:
        logger.warning(
            "report_agent não retornou resultado para o caso %r", especialidade
        )

    erro_execucao = erro_extractor or erro_report

    return {
        "medical_specialty": case["medical_specialty"],
        "extracted": extracted,
        "safety_report": safety_report,
        "relatorio": relatorio,
        "erro_execucao": erro_execucao,
    }


def run_case(case: dict) -> dict:
    """Wrapper síncrono de run_case_async, para uso em scripts e notebooks."""
    return asyncio.run(run_case_async(case))
