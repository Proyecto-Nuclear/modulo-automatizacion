from typing import Dict, Optional, Any, List

from src.core.restrictions.aulas.aulas_recursos.service.buscador_aulas_recursos import BuscadorAulasRecursos
from src.core.restrictions.aulas.aulas_recursos.service.validador_directo import ValidadorDirecto
from src.core.restrictions.aulas.aulas_recursos.service.validador_global import ValidadorGlobal
from src.core.restrictions.aulas.aulas_recursos.service.validador_individual import ValidadorIndividual
from src.core.restrictions.restriction_handler import RestrictionHandler


class AulaRecursosHandler(RestrictionHandler):
    """
    Restricción: El aula asignada debe tener todos los recursos que requiere la asignatura.

    Invariante: self.aula.recursos -> includesAll(self.asignatura.requiereRecursos)
    """

    def __init__(self):
        self.validador_individual = ValidadorIndividual()
        self.validador_global = ValidadorGlobal()
        self.validador_directo = ValidadorDirecto()
        self.buscador_aulas = BuscadorAulasRecursos()

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Verifica que el aula seleccionada tenga todos los recursos requeridos por la asignatura.
        """
        nuevo_bloque = context.get("nuevo_bloque")
        aula_directa = context.get("aula")

        if nuevo_bloque:
            return self.validador_individual.validar(context)
        elif aula_directa:
            return self.validador_directo.validar(context)
        else:
            return self.validador_global.validar(context)

    def obtener_aulas_con_recursos_suficientes(self, context: Dict[str, Any]) -> List[str]:
        """Retorna las aulas que tienen los recursos necesarios para una asignatura."""
        return self.buscador_aulas.obtener_aulas_con_recursos_suficientes(context)

    def obtener_recursos_faltantes_por_aula(self, context: Dict[str, Any]) -> Dict[str, List[str]]:
        """Retorna un diccionario con los recursos faltantes por cada aula."""
        return self.buscador_aulas.obtener_recursos_faltantes_por_aula(context)

    def es_aula_compatible_con_asignatura(self, aula_id: str, asignatura_id: str, context: Dict[str, Any]) -> bool:
        """Verifica si un aula específica es compatible con una asignatura específica."""
        return self.buscador_aulas.es_aula_compatible_con_asignatura(aula_id, asignatura_id, context)