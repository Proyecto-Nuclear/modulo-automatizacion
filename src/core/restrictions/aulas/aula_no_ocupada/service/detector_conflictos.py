from typing import Dict, List, Optional, Any
from .time_utils import horarios_solapan
from .validador_estructura_bloque import ValidadorEstructuraBloque


class DetectorConflictos:
    """Detecta conflictos de solapamiento en horarios."""

    def __init__(self):
        self.validador = ValidadorEstructuraBloque()

    def buscar_conflictos_en_aula(self, horarios_aula: List[Dict]) -> Optional[tuple]:
        """
        Busca conflictos de solapamiento en los horarios de una aula específica.

        :return: Tupla (h1, h2) si hay conflicto, None si no hay conflictos
        """
        horarios_validos = [h for h in horarios_aula if self.validador.validar(h)]
        horarios_ordenados = sorted(horarios_validos, key=lambda x: (x.get('dia', ''), x.get('hora_inicio', '')))

        n = len(horarios_ordenados)
        for i in range(n):
            h1 = horarios_ordenados[i]
            for j in range(i + 1, n):
                h2 = horarios_ordenados[j]

                if (h1.get('id') != h2.get('id') and
                        h1.get('asignatura_id') != h2.get('asignatura_id') and
                        horarios_solapan(h1, h2)):
                    return (h1, h2)

        return None

    def tiene_conflicto_con_existentes(self, nuevo_bloque: Dict, horarios_existentes: List[Dict]) -> Optional[Dict]:
        """
        Verifica si un nuevo bloque tiene conflicto con horarios existentes.

        :return: Horario en conflicto si existe, None si no hay conflictos
        """
        if not self.validador.validar(nuevo_bloque):
            return None

        aula_id = nuevo_bloque["aula_id"]

        for horario_existente in horarios_existentes:
            if not self.validador.validar(horario_existente):
                continue

            if horario_existente.get("aula_id") == aula_id:
                if horarios_solapan(nuevo_bloque, horario_existente):
                    return horario_existente

        return None