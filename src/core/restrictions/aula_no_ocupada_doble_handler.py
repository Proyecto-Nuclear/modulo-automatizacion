from typing import List, Dict, Optional, Any
from .restriction_handler import RestrictionHandler

class AulaNoOcupadaDobleHandler(RestrictionHandler):
    """
    Restricción: El aula asignada no debe estar ocupada por otra asignatura en el mismo horario.
    """

    def validate(self, context: Dict[str, Any]) -> Optional[str]:

        horarios: List[Dict] = context.get("horarios", [])

        aulas: Dict[Any, List[Dict]] = {}
        for h in horarios:
            aula_id = h['aula']
            aulas.setdefault(aula_id, []).append(h)

        for aula_id, hs in aulas.items():
            hs = sorted(hs, key=lambda x: x['start_time'])
            for i in range(len(hs)):
                for j in range(i + 1, len(hs)):
                    h1 = hs[i]
                    h2 = hs[j]
                    if h1.get('id') != h2.get('id'):
                        inicio1, fin1 = h1['start_time'], h1['end_time']
                        inicio2, fin2 = h2['start_time'], h2['end_time']

                        if not (fin1 <= inicio2 or fin2 <= inicio1):
                            return (
                                f"Conflicto: Solapamiento de clases en el aula {aula_id}: "
                                f"horarios {h1.get('id', h1)} ({inicio1}-{fin1}) y {h2.get('id', h2)} ({inicio2}-{fin2})."
                            )
        return None