"""
Ferramenta de Informações de CPU

Este módulo fornece uma ferramenta para coletar informações de CPU.
"""

import time
from typing import Any, Dict

import psutil


def get_cpu_info() -> Dict[str, Any]:
    """
    Coleta informações de CPU incluindo contagem de núcleos e uso.

    Returns:
        Dict[str, Any]: Dicionário com informações de CPU estruturado para ADK
    """
    try:
        # Obtém informações de CPU
        cpu_info = {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "cpu_usage_per_core": [
                f"Core {i}: {percentage:.1f}%"
                for i, percentage in enumerate(
                    psutil.cpu_percent(interval=1, percpu=True)
                )
            ],
            "avg_cpu_usage": f"{psutil.cpu_percent(interval=1):.1f}%",
        }

        # Calcula algumas estatísticas para o resumo do resultado
        avg_usage = float(cpu_info["avg_cpu_usage"].strip("%"))
        high_usage = avg_usage > 80

        # Formata para estrutura de retorno de ferramenta ADK
        return {
            "result": cpu_info,
            "stats": {
                "physical_cores": cpu_info["physical_cores"],
                "logical_cores": cpu_info["logical_cores"],
                "avg_usage_percentage": avg_usage,
                "high_usage_alert": high_usage,
            },
            "additional_info": {
                "data_format": "dictionary",
                "collection_timestamp": time.time(),
                "performance_concern": (
                    "Alto uso de CPU detectado" if high_usage else None
                ),
            },
        }
    except Exception as e:
        return {
            "result": {"error": f"Falha ao coletar informações de CPU: {str(e)}"},
            "stats": {"success": False},
            "additional_info": {"error_type": str(type(e).__name__)},
        }
