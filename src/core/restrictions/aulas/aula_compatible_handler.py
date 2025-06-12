from typing import Dict, Optional, Any, List

from src.core.restrictions.aulas.aula_compatible.buscador_aulas_compatibles import BuscadorAulasCompatibles
from src.core.restrictions.aulas.aula_compatible.validador_compatibilidad import ValidadorCompatibilidad
from src.core.restrictions.restriction_handler import RestrictionHandler

class AulaCompatibleHandler(RestrictionHandler):
    """
    Restricción: Una asignatura de laboratorio solo puede ser asignada a aulas de tipo laboratorio.
    """

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        validator = ValidadorCompatibilidad()
        return validator.validar(context)

    def get_aulas_compatibles(self, context: Dict[str, Any]) -> List[Dict]:
        buscador = BuscadorAulasCompatibles()
        return buscador.get_aulas_compatibles(context)