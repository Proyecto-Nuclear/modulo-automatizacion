from typing import Dict, List, Any
from .detector_conflictos import DetectorConflictos


class BuscadorAulasDisponibles:
    """Busca aulas disponibles para un bloque horario específico."""

    def __init__(self):
        self.detector_conflictos = DetectorConflictos()

    def obtener_aulas_disponibles(self, context: Dict[str, Any]) -> List[str]:
        """
        Retorna las aulas disponibles para un bloque específico.
        """
        bloque_solicitado = context.get("bloque_solicitado", {})
        todas_aulas = context.get("todas_aulas", [])
        horarios_existentes = context.get("horarios_existentes", [])

        aulas_disponibles = []

        for aula in todas_aulas:
            aula_id = aula.get("id")

            nuevo_bloque = {
                **bloque_solicitado,
                "aula_id": aula_id
            }

            if self.detector_conflictos.tiene_conflicto_con_existentes(nuevo_bloque, horarios_existentes) is None:
                aulas_disponibles.append(aula_id)

        return aulas_disponibles