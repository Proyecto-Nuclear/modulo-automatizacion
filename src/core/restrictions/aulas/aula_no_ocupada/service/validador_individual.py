from typing import Dict, Optional, Any
from .detector_conflictos import DetectorConflictos
from .generador_mensajes_conflicto import GeneradorMensajesConflicto


class ValidadorIndividual:
    """Valida un nuevo bloque contra horarios existentes."""

    def __init__(self):
        self.detector = DetectorConflictos()
        self.generador_mensajes = GeneradorMensajesConflicto()

    def validar(self, context: Dict[str, Any]) -> Optional[str]:
        """Valida un nuevo bloque contra los horarios existentes."""
        nuevo_bloque = context["nuevo_bloque"]
        horarios_existentes = context.get("horarios_existentes", [])

        if not self.detector.validador.validar(nuevo_bloque):
            return "El nuevo bloque no tiene la estructura requerida (aula_id, dia, hora_inicio, hora_fin)."

        horario_conflicto = self.detector.tiene_conflicto_con_existentes(nuevo_bloque, horarios_existentes)

        if horario_conflicto:
            return self.generador_mensajes.generar_mensaje_individual(
                nuevo_bloque, horario_conflicto, context
            )

        return None