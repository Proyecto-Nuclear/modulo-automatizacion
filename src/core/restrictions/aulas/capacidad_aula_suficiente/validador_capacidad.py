from typing import Dict, Optional

class ValidadorCapacidad:
    """Valida que el aula tenga capacidad suficiente para el número de estudiantes."""

    @staticmethod
    def validar_capacidad_aula(aula: Dict, numero_estudiantes: int) -> bool:
        capacidad_aula = aula.get("capacidad", 0)
        return capacidad_aula >= numero_estudiantes