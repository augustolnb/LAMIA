"""
Ferramenta de Informações de Disco

Este módulo fornece uma ferramenta para coletar informações de disco.
"""

import time
from typing import Any, Dict

import psutil


def get_disk_info() -> Dict[str, Any]:
    """
    Coleta informações de disco incluindo partições e uso.

    Returns:
        Dict[str, Any]: Dicionário com informações de disco estruturado para ADK
    """
    try:
        # Obtém informações de disco
        disk_info = {"partitions": []}
        partitions_over_threshold = []
        total_space = 0
        used_space = 0

        for partition in psutil.disk_partitions():
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)

                # Rastreia partições com alto uso
                if partition_usage.percent > 85:
                    partitions_over_threshold.append(
                        f"{partition.mountpoint} ({partition_usage.percent:.1f}%)"
                    )

                # Adiciona aos totais
                total_space += partition_usage.total
                used_space += partition_usage.used

                disk_info["partitions"].append(
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "filesystem_type": partition.fstype,
                        "total_size": f"{partition_usage.total / (1024 ** 3):.2f} GB",
                        "used": f"{partition_usage.used / (1024 ** 3):.2f} GB",
                        "free": f"{partition_usage.free / (1024 ** 3):.2f} GB",
                        "percentage": f"{partition_usage.percent:.1f}%",
                    }
                )
            except (PermissionError, FileNotFoundError):
                # Algumas partições podem não estar acessíveis
                pass

        # Calcula estatísticas gerais de disco
        overall_usage_percent = (
            (used_space / total_space * 100) if total_space > 0 else 0
        )

        # Formata para estrutura de retorno de ferramenta ADK
        return {
            "result": disk_info,
            "stats": {
                "partition_count": len(disk_info["partitions"]),
                "total_space_gb": total_space / (1024**3),
                "used_space_gb": used_space / (1024**3),
                "overall_usage_percent": overall_usage_percent,
                "partitions_with_high_usage": len(partitions_over_threshold),
            },
            "additional_info": {
                "data_format": "dictionary",
                "collection_timestamp": time.time(),
                "high_usage_partitions": (
                    partitions_over_threshold if partitions_over_threshold else None
                ),
            },
        }
    except Exception as e:
        return {
            "result": {"error": f"Falha ao coletar informações de disco: {str(e)}"},
            "stats": {"success": False},
            "additional_info": {"error_type": str(type(e).__name__)},
        }
