from typing import Dict, Optional, Any

from src.utils.entity_finder import buscar_entidad_por_id
from src.utils.validation_utils import extraer_horarios_de_context
from .validador_recursos import ValidadorRecursos


class ValidadorGlobal:
    """Valida todo el conjunto de horarios para verificar recursos."""

    def __init__(self):
        self.validador_recursos = ValidadorRecursos()

    def validar(self, context: Dict[str, Any]) -> Optional[str]:
        """Valida todo el conjunto de horarios para verificar recursos."""
        horarios = extraer_horarios_de_context(context)
        aulas = context.get("aulas", [])
        asignaturas = context.get("asignaturas", [])

        if not horarios:
            return None

        for horario in horarios:
            aula_id = horario.get('aula_id') or horario.get('aula')
            asignatura_id = horario.get('asignatura_id') or horario.get('asignatura')

            if not aula_id or not asignatura_id:
                continue

            aula = buscar_entidad_por_id(aulas, aula_id)
            asignatura = buscar_entidad_por_id(asignaturas, asignatura_id)

            if not aula or not asignatura:
                continue

            error = self.validador_recursos.validar_recursos_aula_asignatura(aula, asignatura, context)
            if error:
                horario_info = f" (Horario: {horario.get('dia', 'N/A')} {horario.get('hora_inicio', 'N/A')}-{horario.get('hora_fin', 'N/A')})"
                return error + horario_info

        return None