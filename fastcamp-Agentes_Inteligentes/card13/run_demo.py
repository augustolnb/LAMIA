"""CLI de demonstração: roda o pipeline de agentes clínicos sobre uma amostra do mtsamples."""

from __future__ import annotations

import json
import logging
import os
import warnings

from dotenv import load_dotenv

# Ruído interno do ADK 2.7.1: flag de feature experimental (llm_request.py:273).
# Filtro estreito — qualquer outro UserWarning continua visível.
warnings.filterwarnings(
    "ignore", message=r".*JSON_SCHEMA_FOR_FUNC_DECL.*", category=UserWarning
)

from src.data_prep import load_sample
from src.pipeline import run_case

SYNTHETIC_CASE = {
    "description": "Caso sintético para demonstrar interação medicamentosa não explícita no texto.",
    "medical_specialty": "Cardiovascular / Pulmonary (sintético)",
    "transcription": (
        "SUBJECTIVE: Paciente de 68 anos, em uso contínuo de Warfarin para fibrilação atrial, "
        "relata dor torácica leve nos últimos dois dias. Nega falta de ar. "
        "OBJECTIVE: Sinais vitais estáveis. ECG sem alterações agudas. "
        "PLAN: Iniciado Aspirin 100mg ao dia para controle sintomático da dor torácica."
    ),
}


def main() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
    csv_path = os.environ.get("DATA_CSV_PATH", "data/mtsamples.csv")
    n_total = int(os.environ.get("N_CASOS_AMOSTRA", "20"))

    sample = load_sample(csv_path, n_total=n_total)
    cases = sample.to_dict(orient="records")
    cases.append(SYNTHETIC_CASE)

    for i, case in enumerate(cases, start=1):
        print(f"\n{'=' * 80}\nCaso {i}/{len(cases)} — {case['medical_specialty']}\n{'=' * 80}")
        result = run_case(case)
        if result["erro_execucao"]:
            print(f"\n!!! Falha na execução do agente: {result['erro_execucao']}")

        print("\n--- Extração ---")
        print(json.dumps(result["extracted"], ensure_ascii=False, indent=2))

        print("\n--- Segurança ---")
        print(json.dumps(result["safety_report"], ensure_ascii=False, indent=2))

        print("\n--- RELATÓRIO ---")
        print(result["relatorio"])


if __name__ == "__main__":
    main()
