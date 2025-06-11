from typing import List, Dict

class BuscadorAulasCapacidad:
    """Busca aulas con capacidad suficiente."""

    @staticmethod
    def obtener_aulas_con_capacidad_suficiente(numero_estudiantes: int, todas_aulas: List[Dict]) -> List[str]:
        return [
            aula.get("id")
            for aula in todas_aulas
            if aula.get("capacidad", 0) >= numero_estudiantes
        ]

    @staticmethod
    def recomendaciones(aulas: List[Dict], aula_id: str, numero_estudiantes: int) -> List[str]:
        return [
            f"{a['nombre']} (capacidad: {a['capacidad']})"
            for a in aulas
            if a["id"] != aula_id and a.get("capacidad", 0) >= numero_estudiantes
        ]