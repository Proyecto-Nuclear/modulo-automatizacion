from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

from src.core.schedules.selector_factory import SelectorFactory


class CreadorHorarios:
    """Gestiona la creación de horarios."""

    def __init__(self):
        """Inicializa el creador con configuraciones por defecto."""
        self.default_config = {
            'incluir_metadatos': True,
            'validar_restricciones': True
        }

    def crear_horario(self, tipo: str, validar: bool = True, **kwargs) -> Tuple[Any, Optional[str]]:
        """Crea un horario del tipo especificado con validación opcional."""
        try:
            if self.default_config['incluir_metadatos']:
                kwargs.setdefault('created_at', datetime.now().isoformat())
                kwargs.setdefault('estado', 'tentativo')

            horario, error = SelectorFactory.crear_horario(tipo, **kwargs)

            if error:
                return None, f"Error en creación: {error}"

            return horario, None

        except Exception as e:
            return None, f"Error inesperado: {str(e)}"

    def crear_horarios_lote(self, horarios_data: List[Dict[str, Any]],
                            validar_individual: bool = True,
                            validar_conjunto: bool = True) -> Dict[str, Any]:
        """Crea múltiples horarios en lote con validación individual y de conjunto."""
        resultados = {
            'exitosos': [],
            'fallidos': [],
            'errores': [],
            'resumen': {
                'total': len(horarios_data),
                'exitosos': 0,
                'fallidos': 0
            }
        }

        horarios_creados = []

        for i, horario_data in enumerate(horarios_data):
            tipo = horario_data.pop('tipo', 'normal')
            horario, error = self.crear_horario(tipo, validar=validar_individual, **horario_data)

            if horario:
                horarios_creados.append(horario)
                resultados['exitosos'].append({
                    'indice': i,
                    'horario': horario,
                    'tipo': tipo
                })
                resultados['resumen']['exitosos'] += 1
            else:
                resultados['fallidos'].append({
                    'indice': i,
                    'error': error,
                    'datos': horario_data
                })
                resultados['errores'].append(f"Horario {i}: {error}")
                resultados['resumen']['fallidos'] += 1

        return resultados

    def obtener_tipos_horarios_disponibles(self) -> List[str]:
        """Obtiene los tipos de horarios disponibles."""
        return SelectorFactory.get_tipos_disponibles()

    def es_tipo_horario_valido(self, tipo: str) -> bool:
        """Verifica si un tipo de horario es válido."""
        return SelectorFactory.es_tipo_valido(tipo)