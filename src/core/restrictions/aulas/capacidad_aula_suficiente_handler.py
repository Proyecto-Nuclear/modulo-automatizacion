from typing import List, Dict, Optional, Any
from src.core.restrictions.restriction_handler import RestrictionHandler

class CapacidadAulaSuficienteHandler(RestrictionHandler):
    """
    Restricción: El aula asignada debe tener capacidad suficiente para el número de estudiantes.
    Si no la tiene, recomienda otras aulas que sí la tengan.
    """

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Verifica que el aula seleccionada tenga capacidad suficiente.
        Si no cumple, recomienda otras aulas que sí cumplen.

        :param context: Dict con las claves:
            - 'aula': Dict con los datos del aula seleccionada (de aulas.json)
            - 'numero_estudiantes': int, cantidad de estudiantes
            - 'aulas': List[Dict] con todas las aulas disponibles (de aulas.json)
        :return: None si es válido, mensaje de error (str) si la capacidad es insuficiente, con sugerencias si corresponde.
        """
        aula: Dict = context["aula"]
        capacidad_aula = aula.get("capacidad", 0)
        numero_estudiantes = context.get("numero_estudiantes")
        aulas: List[Dict] = context.get("", [])
        asignatura = context.get("asignatura", {}).get("nombre", "Asignatura desconocida")

        if numero_estudiantes is None:
            return "No se proporcionó el número de estudiantes para la asignación."

        if capacidad_aula < numero_estudiantes:
            msg = (
                f"No se puede asignar el aula '{aula.get('nombre', aula.get('id', 'desconocida'))}' "
                f"(capacidad: {capacidad_aula}) a la asignatura '{asignatura}' "
                f"porque la cantidad de estudiantes es {numero_estudiantes}."
            )

            # Buscar aulas recomendadas (distintas al aula seleccionada y con capacidad suficiente)
            recomendaciones = [
                f"{a['nombre']} (capacidad: {a['capacidad']})"
                for a in aulas
                if a["id"] != aula["id"] and a.get("capacidad", 0) >= numero_estudiantes
            ]

            if recomendaciones:
                msg += "\nAulas recomendadas con capacidad suficiente: " + "; ".join(recomendaciones)
            else:
                msg += "\nNo se encontraron otras aulas con capacidad suficiente."

            return msg

        return None