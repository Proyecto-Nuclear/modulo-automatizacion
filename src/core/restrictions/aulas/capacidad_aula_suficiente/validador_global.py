from typing import Dict, Optional, Any

from src.utils.entity_finder import buscar_entidad_por_id
from .validador_capacidad import ValidadorCapacidad
from .buscador_aulas import BuscadorAulasCapacidad
from .generador_mensajes import GeneradorMensajesCapacidad

class ValidadorGlobalCapacidad:
    def validar(self, context: Dict[str, Any]) -> Optional[str]:
        horarios = context.get("schedules") or context.get("horarios", [])
        aulas = context.get("aulas", [])
        asignaturas = context.get("asignaturas", [])

        if not horarios:
            return None

        for horario in horarios:
            aula_id = horario.get('aula_id') or horario.get('aula')
            asignatura_id = horario.get('asignatura_id') or horario.get('asignatura')
            numero_estudiantes = horario.get('numero_estudiantes')

            if not aula_id or not asignatura_id or numero_estudiantes is None:
                continue

            aula = buscar_entidad_por_id(aulas, aula_id)
            asignatura = buscar_entidad_por_id(asignaturas, asignatura_id)
            asignatura_nombre = asignatura.get("nombre", "Asignatura desconocida") if asignatura else "Asignatura desconocida"

            if not aula or not asignatura:
                continue

            if not ValidadorCapacidad.validar_capacidad_aula(aula, numero_estudiantes):
                recomendaciones = BuscadorAulasCapacidad.recomendaciones(aulas, aula_id, numero_estudiantes)
                horario_info = f" (Horario: {horario.get('dia', 'N/A')} {horario.get('hora_inicio', 'N/A')}-{horario.get('hora_fin', 'N/A')})"
                return GeneradorMensajesCapacidad.mensaje_capacidad_insuficiente(aula, numero_estudiantes, asignatura_nombre, recomendaciones) + horario_info
        return None