from typing import List, Dict, Optional, Any
from src.core.restrictions.restriction_handler import RestrictionHandler

class RespetarBloqueosHandler(RestrictionHandler):
    """
    Invariante: Un horario asignado a un aula no puede coincidir con un bloqueo para esa aula.
    """

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Verifica que ningún horario asignado a un aula se solape con un bloqueo de esa aula.

        :param context: Dict con las claves:
            - 'schedules': List[Dict], cada dict representa un horario con 'id', 'aula', 'horaInicio', 'horaFin'
            - 'bloqueos': List[Dict], cada dict representa un bloqueo con 'aula', 'horario' (dict con 'horaInicio', 'horaFin')
        :return: None si es válido, mensaje de error (str) si algún horario coincide con un bloqueo.
        """
        horarios: List[Dict] = context.get("", [])
        bloqueos: List[Dict] = context.get("bloqueos", [])
        errores = []

        for h in horarios:
            aula_h = h['aula']
            inicio_h = h['start_time']
            fin_h = h['end_time']
            id_h = h.get('id', h)

            for b in bloqueos:
                aula_b = b['aula']
                horario_b = b['horario']
                inicio_b = horario_b['start_time']
                fin_b = horario_b['end_time']

                if aula_h == aula_b:
                    if not (fin_h <= inicio_b or fin_b <= inicio_h):
                        errores.append(
                            f"Conflicto: El horario {id_h} ({h['start_time']}-{h['end_time']}) en el aula '{aula_h}' "
                            f"coincide con un bloqueo ({horario_b['start_time']}-{horario_b['end_time']}) para esa aula."
                        )
        if errores:
            return "\n".join(errores)
        return None