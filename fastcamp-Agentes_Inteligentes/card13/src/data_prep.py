"""Carregamento e filtragem de amostra do dataset mtsamples."""

from __future__ import annotations

import pandas as pd

DEFAULT_SPECIALTIES = ["Cardiovascular / Pulmonary", "Neurology", "General Medicine"]
REQUIRED_COLUMNS = ["description", "transcription", "medical_specialty"]


def load_sample(
    csv_path: str,
    n_total: int = 30,
    specialties: list[str] | None = None,
    seed: int = 42,
) -> pd.DataFrame:
    """Carrega o CSV mtsamples e retorna uma amostra balanceada por especialidade.

    Args:
        csv_path: Caminho do CSV (colunas description, transcription, medical_specialty).
        n_total: Número total de casos desejado na amostra (dividido entre as especialidades).
        specialties: Especialidades a incluir (default: DEFAULT_SPECIALTIES).
        seed: Semente para amostragem determinística.

    Returns:
        DataFrame com colunas description, transcription, medical_specialty.

    Raises:
        FileNotFoundError: Se csv_path não existir.
    """
    specialties = specialties or DEFAULT_SPECIALTIES
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"CSV de casos clínicos não encontrado em '{csv_path}'. "
            "Configure DATA_CSV_PATH ou salve o arquivo em data/mtsamples.csv."
        ) from exc

    df["medical_specialty"] = df["medical_specialty"].str.strip()
    filtered = df[df["medical_specialty"].isin(specialties)]

    n_per_specialty = max(1, n_total // len(specialties))
    frames = []
    for specialty in specialties:
        subset = filtered[filtered["medical_specialty"] == specialty]
        frames.append(subset.sample(min(len(subset), n_per_specialty), random_state=seed))

    sample = pd.concat(frames, ignore_index=True)
    return sample[REQUIRED_COLUMNS]
