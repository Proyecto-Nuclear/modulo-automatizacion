from typing import Dict, Optional, Any

from src.utils.entity_finder import buscar_entidad_por_id
from .validador_recursos import ValidadorRecursos


class ValidadorIndividual:
    """Valida un nuevo bloque contra los recursos disponibles del aula."""

    def __init__(self):
        self.validador_recursos = ValidadorRecursos()

    def validar(self, context: Dict[str, Any]) -> Optional[str]:
        """Valida un nuevo bloque contra los recursos disponibles del aula."""
        nuevo_bloque = context["nuevo_bloque"]
        aulas = context.get("aulas", [])
        asignaturas = context.get("asignaturas", [])

        aula_id = nuevo_bloque.get("aula_id")
        asignatura_id = nuevo_bloque.get("asignatura_id")

        if not aula_id or not asignatura_id:
            return "El nuevo bloque debe tener aula_id y asignatura_id definidos."

        aula = buscar_entidad_por_id(aulas, aula_id)
        asignatura = buscar_entidad_por_id(asignaturas, asignatura_id)

        if not aula:
            return f"No se encontró el aula con ID: {aula_id}"

        if not asignatura:
            return f"No se encontró la asignatura con ID: {asignatura_id}"

        return self.validador_recursos.validar_recursos_aula_asignatura(aula, asignatura, context)