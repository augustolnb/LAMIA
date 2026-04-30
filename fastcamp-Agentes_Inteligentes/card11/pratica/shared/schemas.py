from pydantic import BaseModel
from typing import Optional

class TutoringRequest(BaseModel):
    materia: str  # Ex: Física, Matemática
    topico: str   # Ex: Eletromagnetismo, Cálculo I
    nivel: str    # Ex: Ensino Médio, Superior (Engenharia)
    foco: str     # Ex: Teoria, Resolução de Exercícios, Preparação para Prova
    user_id: Optional[str] = "lucas_prof"
