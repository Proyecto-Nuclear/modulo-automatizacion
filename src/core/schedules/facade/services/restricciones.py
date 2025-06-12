from typing import List
from src.core.restrictions.docente.docente_no_traslapado_handler import DocenteNoTraslapadoHandler
from src.core.restrictions.horarios.respetar_bloqueos_handler import RespetarBloqueosHandler
from src.core.restrictions.integridad.integridad_entidades_handler import IntegridadEntidadesHandler
from src.core.restrictions.aulas.aula_no_ocupada_doble_handler import AulaNoOcupadaDobleHandler
from src.core.restrictions.aulas.capacidad_aula_suficiente_handler import CapacidadAulaSuficienteHandler
from src.core.restrictions.aulas.aula_compatible_handler import AulaCompatibleHandler
from src.core.restrictions.aulas.aula_recursos_handler import AulaRecursosHandler

class GestorRestricciones:
    """Gestiona la cadena de restricciones."""

    def __init__(self):
        """Inicializa el gestor y configura la cadena de restricciones."""
        self.restriction_chain = self._setup_restriction_chain()

    def _setup_restriction_chain(self):
        """Configura la cadena de restricciones en el orden apropiado."""
        integridad_handler = IntegridadEntidadesHandler()
        bloqueos_handler = RespetarBloqueosHandler()
        aula_ocupada_handler = AulaNoOcupadaDobleHandler()
        capacidad_handler = CapacidadAulaSuficienteHandler()
        aula_compatible_handler = AulaCompatibleHandler()
        recursos_handler = AulaRecursosHandler()
        docente_traslape_handler = DocenteNoTraslapadoHandler()

        integridad_handler.set_next(bloqueos_handler)
        bloqueos_handler.set_next(aula_ocupada_handler)
        aula_ocupada_handler.set_next(capacidad_handler)
        capacidad_handler.set_next(aula_compatible_handler)
        aula_compatible_handler.set_next(recursos_handler)
        recursos_handler.set_next(docente_traslape_handler)

        return integridad_handler

    def obtener_info_restricciones(self) -> List[str]:
        """Obtiene información sobre las restricciones configuradas en la cadena."""
        restrictions = []
        current = self.restriction_chain
        while current:
            restrictions.append(current.__class__.__name__)
            current = getattr(current, '_next_handler', None)
        return restrictions