from typing import List, Dict, Optional, Any

from src.core.restrictions.aulas.aula_no_ocupada.service.buscador_aulas_disponibles import BuscadorAulasDisponibles
from src.core.restrictions.aulas.aula_no_ocupada.service.validador_global import ValidadorGlobal
from src.core.restrictions.aulas.aula_no_ocupada.service.validador_individual import ValidadorIndividual
from src.core.restrictions.restriction_handler import RestrictionHandler


class AulaNoOcupadaDobleHandler(RestrictionHandler):
    """
    Restricción: Un aula no puede tener dos clases diferentes al mismo tiempo.

    Invariante: Horario.allInstances() -> forAll(h1, h2 | h1 <> h2 and h1.aula = h2.aula
                implies h1.horaFin <= h2.horaInicio or h2.horaFin <= h1.horaInicio)
    """

    def __init__(self):
        super().__init__()
        self.validador_individual = ValidadorIndividual()
        self.validador_global = ValidadorGlobal()
        self.buscador_aulas = BuscadorAulasDisponibles()

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Verifica que un aula no tenga dos asignaturas asignadas en horarios solapados.

        Soporta dos modos de validación:
        1. Validación individual: Verifica un nuevo bloque contra los existentes
        2. Validación global: Verifica todo el conjunto de horarios asignados
        """
        nuevo_bloque = context.get("nuevo_bloque")

        if nuevo_bloque:
            return self.validador_individual.validar(context)
        else:
            return self.validador_global.validar(context)

    def obtener_aulas_disponibles(self, context: Dict[str, Any]) -> List[str]:
        """
        Método auxiliar que retorna las aulas disponibles para un bloque específico.
        """
        return self.buscador_aulas.obtener_aulas_disponibles(context)