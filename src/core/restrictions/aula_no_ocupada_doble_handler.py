from typing import List, Dict, Optional, Any
from .restriction_handler import RestrictionHandler

def horarios_solapan(h1: Dict, h2: Dict) -> bool:
    """
    Devuelve True si los horarios h1 y h2 se solapan.
    """
    inicio1, fin1 = h1['start_time'], h1['end_time']
    inicio2, fin2 = h2['start_time'], h2['end_time']
    return not (fin1 <= inicio2 or fin2 <= inicio1)

class AulaNoOcupadaDobleHandler(RestrictionHandler):
    """
    Restricción: El aula asignada no debe estar ocupada por otra asignatura en el mismo horario.
    """

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Verifica que un aula no tenga dos asignaturas asignadas en horarios solapados.

        :param context: Dict con las claves:
            - 'horarios': Lista de dicts con los datos de los horarios asignados, cada uno incluyendo al menos 'aula', 'start_time' y 'end_time'.
        :return: None si es válido, mensaje de error (str) si se detecta solapamiento de horarios en el aula.
        """
        horarios: List[Dict] = context.get("horarios", [])

        # Agrupar horarios por aula
        aulas: Dict[Any, List[Dict]] = {}
        for h in horarios:
            aula_id = h['aula']
            aulas.setdefault(aula_id, []).append(h)

        # Revisar solapamientos en cada aula
        for aula_id, hs in aulas.items():
            hs = sorted(hs, key=lambda x: x['start_time'])
            n = len(hs)
            for i in range(n):
                h1 = hs[i]
                for j in range(i + 1, n):
                    h2 = hs[j]
                    # Si los horarios tienen ID distintos y se solapan, reportar conflicto
                    if h1.get('id') != h2.get('id') and horarios_solapan(h1, h2):
                        return (
                            f"Conflicto: Solapamiento de clases en el aula {aula_id}: "
                            f"horarios {h1.get('id', h1)} ({h1['start_time']}-{h1['end_time']}) y "
                            f"{h2.get('id', h2)} ({h2['start_time']}-{h2['end_time']})."
                        )
        return None