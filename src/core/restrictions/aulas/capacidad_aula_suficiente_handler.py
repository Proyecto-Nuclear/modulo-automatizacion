from typing import Dict, Optional, Any, List

from src.core.restrictions.aulas.capacidad_aula_suficiente.buscador_aulas import BuscadorAulasCapacidad
from src.core.restrictions.aulas.capacidad_aula_suficiente.validador_directo import ValidadorDirectoCapacidad
from src.core.restrictions.aulas.capacidad_aula_suficiente.validador_global import ValidadorGlobalCapacidad
from src.core.restrictions.aulas.capacidad_aula_suficiente.validador_individual import ValidadorIndividualCapacidad
from src.core.restrictions.restriction_handler import RestrictionHandler

class CapacidadAulaSuficienteHandler(RestrictionHandler):
    """
    Restricción: El aula asignada debe tener capacidad suficiente para el número de estudiantes.
    """

    def __init__(self):
        self.validador_individual = ValidadorIndividualCapacidad()
        self.validador_global = ValidadorGlobalCapacidad()
        self.validador_directo = ValidadorDirectoCapacidad()
        self.buscador_aulas = BuscadorAulasCapacidad()

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        nuevo_bloque = context.get("nuevo_bloque")
        aula_directa = context.get("aula")

        if nuevo_bloque:
            return self.validador_individual.validar(context)
        elif aula_directa:
            return self.validador_directo.validar(context)
        else:
            return self.validador_global.validar(context)

    def obtener_aulas_con_capacidad_suficiente(self, context: Dict[str, Any]) -> List[str]:
        numero_estudiantes = context.get("numero_estudiantes")
        todas_aulas = context.get("todas_aulas", [])
        if numero_estudiantes is None:
            return []
        return self.buscador_aulas.obtener_aulas_con_capacidad_suficiente(numero_estudiantes, todas_aulas)

    def es_aula_compatible_con_capacidad(self, aula_id: str, numero_estudiantes: int, context: Dict[str, Any]) -> bool:
        aulas = context.get("aulas", [])
        aula = next((a for a in aulas if a.get("id") == aula_id), None)
        if not aula:
            return False
        return self.buscador_aulas.obtener_aulas_con_capacidad_suficiente(numero_estudiantes, [aula]) == [aula_id]