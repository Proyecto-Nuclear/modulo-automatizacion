from typing import List, Dict, Optional, Any
from .restriction_handler import RestrictionHandler

class DocenteNoTraslapadoHandler(RestrictionHandler):
    """
    Restricción: Un profesor no puede tener dos clases asignadas al mismo tiempo (sin superposición de horarios).
    """

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Verifica que un docente no tenga dos clases asignadas que se traslapen en el mismo horario.

        :param context: Dict con las claves:
            - 'schedule': Lista de dicts con los horarios ya asignados, cada uno incluyendo al menos 'docente_id', 'date', 'start_time', y 'end_time'.
            - 'new_schedule': Dict con los datos del nuevo horario a asignar, incluyendo las mismas claves.
            - 'docentes': (Opcional) Lista de dicts con los datos de los docentes, para mostrar el nombre en el mensaje de error.
        :return: None si es válido, mensaje de error (str) si el docente tiene traslape de horarios.
        """
        schedules: List[Dict] = context["schedule"]
        new_schedule: Dict = context["new_schedule"]
        docentes: List[Dict] = context.get("docentes", [])

        def get_docente_name(docente_id):
            docente = next((d for d in docentes if d["id"] == docente_id), None)
            return f"{docente['nombre']} {docente['apellido']}" if docente else docente_id

        for schedule in schedules:
            if (
                schedule["docente_id"] == new_schedule["docente_id"] and
                schedule["date"] == new_schedule["date"] and
                not (
                    schedule["end_time"] <= new_schedule["start_time"] or
                    new_schedule["end_time"] <= schedule["start_time"]
                )
            ):
                nombre = get_docente_name(schedule["docente_id"])
                return (
                    f"Conflicto: Docente {nombre} "
                    f"ya tiene una clase de {schedule['start_time']} a {schedule['end_time']} en {schedule['date']}."
                )
        return None