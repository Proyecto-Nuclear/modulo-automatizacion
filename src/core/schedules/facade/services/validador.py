from typing import Dict, List, Any, Tuple, Optional

from src.core.restrictions.aulas.aula_no_ocupada.service.detector_conflictos import DetectorConflictos
from src.core.restrictions.aulas.aula_no_ocupada.service.generador_mensajes_conflicto import GeneradorMensajesConflicto
from src.core.schedules.facade.services.restricciones import GestorRestricciones


class ValidadorHorarios:
    """Gestiona la validación de horarios."""

    def __init__(self):
        """Inicializa el validador con los componentes necesarios."""
        self.detector = DetectorConflictos()
        self.generador_mensajes = GeneradorMensajesConflicto()
        self.gestor_restricciones = GestorRestricciones()

    def validar_horario(self, horario_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Valida un horario sin crearlo."""
        try:
            error = self.gestor_restricciones.restriction_chain.validate(horario_data)

            if error:
                return False, error

            return True, None

        except Exception as e:
            return False, f"Error en validación: {str(e)}"

    def validar_horarios_conjunto(self, horarios_data: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """Valida un conjunto de horarios para detectar conflictos entre ellos."""
        try:
            context = {"schedules": horarios_data}
            error = self.gestor_restricciones.restriction_chain.validate(context)

            if error:
                return False, error

            return True, None

        except Exception as e:
            return False, f"Error en validación de conjunto: {str(e)}"

    def detectar_conflictos(self, horarios: List[Any]) -> Dict[str, List[str]]:
        """Detecta conflictos entre horarios (traslapes de docentes, aulas, etc.)."""
        conflictos = {
            'docentes': [],
            'aulas': [],
            'otros': []
        }

        context = {"schedules": [h.to_dict() if hasattr(h, 'to_dict') else h for h in horarios]}
        error = self.gestor_restricciones.restriction_chain.validate(context)

        if error:
            if 'docente' in error.lower():
                conflictos['docentes'].append(error)
            elif 'aula' in error.lower():
                conflictos['aulas'].append(error)
            else:
                conflictos['otros'].append(error)

        return conflictos