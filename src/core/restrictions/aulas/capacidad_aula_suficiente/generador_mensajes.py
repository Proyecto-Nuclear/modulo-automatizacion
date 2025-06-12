from typing import Dict, List

class GeneradorMensajesCapacidad:
    """Genera mensajes descriptivos para capacidad insuficiente."""

    @staticmethod
    def mensaje_capacidad_insuficiente(aula: Dict, numero_estudiantes: int, asignatura_nombre: str, recomendaciones: List[str]) -> str:
        capacidad_aula = aula.get("capacidad", 0)
        msg = (
            f"No se puede asignar el aula '{aula.get('nombre', aula.get('id', 'desconocida'))}' "
            f"(capacidad: {capacidad_aula}) a la asignatura '{asignatura_nombre}' "
            f"porque la cantidad de estudiantes es {numero_estudiantes}."
        )
        if recomendaciones:
            msg += "\nAulas recomendadas con capacidad suficiente: " + "; ".join(recomendaciones)
        else:
            msg += "\nNo se encontraron otras aulas con capacidad suficiente."
        return msg