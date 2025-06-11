from typing import Dict, Optional, Any
from .validador_capacidad import ValidadorCapacidad
from .buscador_aulas import BuscadorAulasCapacidad
from .generador_mensajes import GeneradorMensajesCapacidad

class ValidadorDirectoCapacidad:
    def validar(self, context: Dict[str, Any]) -> Optional[str]:
        aula = context["aula"]
        numero_estudiantes = context.get("numero_estudiantes")
        aulas = context.get("aulas", [])
        asignatura = context.get("asignatura", {})
        asignatura_nombre = asignatura.get("nombre", "Asignatura desconocida")

        if numero_estudiantes is None:
            return "No se proporcionó el número de estudiantes para la asignación."

        if not ValidadorCapacidad.validar_capacidad_aula(aula, numero_estudiantes):
            recomendaciones = BuscadorAulasCapacidad.recomendaciones(aulas, aula.get("id"), numero_estudiantes)
            return GeneradorMensajesCapacidad.mensaje_capacidad_insuficiente(aula, numero_estudiantes, asignatura_nombre, recomendaciones)
        return None