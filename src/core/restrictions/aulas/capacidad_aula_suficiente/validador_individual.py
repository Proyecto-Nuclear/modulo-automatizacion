from typing import Dict, Optional, Any

from src.utils.entity_finder import buscar_entidad_por_id
from .validador_capacidad import ValidadorCapacidad
from .buscador_aulas import BuscadorAulasCapacidad
from .generador_mensajes import GeneradorMensajesCapacidad

class ValidadorIndividualCapacidad:
    def validar(self, context: Dict[str, Any]) -> Optional[str]:
        nuevo_bloque = context["nuevo_bloque"]
        aulas = context.get("aulas", [])
        asignaturas = context.get("asignaturas", [])

        aula_id = nuevo_bloque.get("aula_id")
        asignatura_id = nuevo_bloque.get("asignatura_id")
        numero_estudiantes = nuevo_bloque.get("numero_estudiantes")

        if not aula_id or not asignatura_id or numero_estudiantes is None:
            return "El nuevo bloque debe tener aula_id, asignatura_id y numero_estudiantes definidos."

        aula = buscar_entidad_por_id(aulas, aula_id)
        asignatura = buscar_entidad_por_id(asignaturas, asignatura_id)
        asignatura_nombre = asignatura.get("nombre", "Asignatura desconocida") if asignatura else "Asignatura desconocida"

        if not aula:
            return f"No se encontró el aula con ID: {aula_id}"
        if not asignatura:
            return f"No se encontró la asignatura con ID: {asignatura_id}"

        if not ValidadorCapacidad.validar_capacidad_aula(aula, numero_estudiantes):
            recomendaciones = BuscadorAulasCapacidad.recomendaciones(aulas, aula_id, numero_estudiantes)
            return GeneradorMensajesCapacidad.mensaje_capacidad_insuficiente(aula, numero_estudiantes, asignatura_nombre, recomendaciones)
        return None