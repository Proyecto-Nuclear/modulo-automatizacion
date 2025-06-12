from typing import Dict, List, Any


class AgrupadorHorarios:
    """Agrupa horarios por diferentes criterios."""

    @staticmethod
    def agrupar_por_aula(horarios: List[Dict]) -> Dict[Any, List[Dict]]:
        """
        Agrupa los horarios por aula para optimizar la búsqueda de conflictos.
        """
        aulas_horarios = {}
        for horario in horarios:
            aula_id = horario.get('aula_id') or horario.get('aula')
            if aula_id:
                aulas_horarios.setdefault(aula_id, []).append(horario)
        return aulas_horarios