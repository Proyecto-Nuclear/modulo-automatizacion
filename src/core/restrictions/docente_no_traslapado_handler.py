"""
Restricción: Un profesor no puede tener dos clases asignadas al mismo tiempo (sin superposición de horarios).
"""

from typing import List, Dict, Optional, Any

from .restriction_handler import RestrictionHandler

class DocenteNoTraslapadoHandler(RestrictionHandler):
    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        schedules: List[Dict] = context["schedule"]
        new_schedule: Dict = context["new_schedule"]
        docentes: List[Dict] = context.get("docentes", [])
        def get_docente_name(docente_id):
            docente = next((d for d in docentes if d["id"] == docente_id), None)
            return f"{docente['nombre']} {docente['apellido']}" if docente else docente_id

        for schedule in schedules:
            if (
                schedule["docente_id"] == new_schedule["docente_id"] and
                schedule["date"] == new_schedule["date"]
            ):
                if not (
                    schedule["end_time"] <= new_schedule["start_time"] and
                    new_schedule["end_time"] >= schedule["start_time"]
                ):
                    nombre = get_docente_name(schedule["docente_id"])
                    return (
                        f"Conflicto: Docente {nombre} "
                        f"ya tiene una clase de {schedule['start_time']} a {schedule['end_time']} en {schedule['date']}."
                    )
        return None