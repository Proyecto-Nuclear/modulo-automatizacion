from typing import Dict, Optional, Any, List
from .detector_conflictos import DetectorConflictos
from .agrupador_horarios import AgrupadorHorarios
from .generador_mensajes_conflicto import GeneradorMensajesConflicto


class ValidadorGlobal:
    """Valida todo el conjunto de horarios para detectar solapamientos."""

    def __init__(self):
        self.detector = DetectorConflictos()
        self.agrupador = AgrupadorHorarios()
        self.generador_mensajes = GeneradorMensajesConflicto()

    def validar(self, context: Dict[str, Any]) -> Optional[str]:
        """Valida todo el conjunto de horarios."""
        horarios = context.get("schedules") or context.get("horarios", [])

        if not horarios:
            return None

        aulas_horarios = self.agrupador.agrupar_por_aula(horarios)

        for aula_id, horarios_aula in aulas_horarios.items():
            conflicto = self.detector.buscar_conflictos_en_aula(horarios_aula)
            if conflicto:
                h1, h2 = conflicto
                return self.generador_mensajes.generar_mensaje_global(h1, h2, context)

        return None