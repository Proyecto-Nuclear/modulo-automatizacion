from typing import List, Dict, Any
import json
import os

from src.core.restrictions.aulas.aula_compatible_handler import AulaCompatibleHandler
from src.core.restrictions.aulas.aula_no_ocupada_doble_handler import AulaNoOcupadaDobleHandler
from src.core.restrictions.aulas.capacidad_aula_suficiente_handler import CapacidadAulaSuficienteHandler


class AulaDisponibleService:
    """
    Servicio para determinar qué aulas están disponibles para una asignatura
    basándose en las restricciones definidas.
    """

    def __init__(self):
        self.data_dir = self._get_data_dir()
        self._setup_restriction_chain()

    def _get_data_dir(self) -> str:
        """Obtiene el directorio de datos igual que en los tests."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.abspath(os.path.join(base_dir, '../../data'))
        return data_dir

    def _setup_restriction_chain(self):
        """Configura la cadena de restricciones."""
        # Crear handlers
        self.capacidad_handler = CapacidadAulaSuficienteHandler()
        self.compatibilidad_handler = AulaCompatibleHandler()
        self.ocupacion_handler = AulaNoOcupadaDobleHandler()

        # Configurar cadena
        self.capacidad_handler.set_next(self.compatibilidad_handler)
        self.compatibilidad_handler.set_next(self.ocupacion_handler)

    def _load_json_data(self, filename: str) -> List[Dict[str, Any]]:
        """Carga datos desde archivo JSON."""
        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def get_aulas_disponibles(
            self,
            asignatura_id: str,
            hora_inicio: str,
            hora_fin: str,
            dia: str,
            cantidad_estudiantes: int,
            semestre: int
    ) -> Dict[str, Any]:
        """
        Obtiene las aulas disponibles para una asignatura específica.

        Args:
            asignatura_id: ID de la asignatura
            hora_inicio: Hora de inicio (formato HH:MM)
            hora_fin: Hora de fin (formato HH:MM)
            dia: Día de la semana
            cantidad_estudiantes: Número de estudiantes
            semestre: Semestre académico

        Returns:
            Dict con aulas disponibles y no disponibles con sus razones
        """
        # Cargar datos
        aulas = self._load_json_data('aulas.json')
        asignaturas = self._load_json_data('asignaturas.json')
        horarios_existentes = self._load_json_data('horarios.json')

        # Buscar la asignatura
        asignatura = next((a for a in asignaturas if a['id'] == asignatura_id), None)
        if not asignatura:
            return {
                'error': f'Asignatura con ID {asignatura_id} no encontrada',
                'aulas_disponibles': [],
                'aulas_no_disponibles': []
            }

        # Filtrar horarios existentes para el mismo día y horario
        horarios_conflicto = [
            h for h in horarios_existentes
            if h.get('dia') == dia and self._horarios_solapan(
                {'start_time': hora_inicio, 'end_time': hora_fin},
                {'start_time': h.get('start_time'), 'end_time': h.get('end_time')}
            )
        ]

        aulas_disponibles = []
        aulas_no_disponibles = []

        # Evaluar cada aula
        for aula in aulas:
            if aula.get('estado', '').lower() != 'activo':
                continue

            # Crear contexto para las restricciones
            context = {
                'aula': aula,
                'asignatura': asignatura,
                'numero_estudiantes': cantidad_estudiantes,
                'aulas': aulas,
                'schedules': horarios_conflicto + [{
                    'aula': aula['id'],
                    'start_time': hora_inicio,
                    'end_time': hora_fin,
                    'dia': dia,
                    'id': 'temp_schedule'
                }],
                'dia': dia,
                'hora_inicio': hora_inicio,
                'hora_fin': hora_fin
            }

            # Aplicar restricciones
            error = self.capacidad_handler.handle(context)

            if error is None:
                # Verificar ocupación específica para esta aula
                aula_ocupada = any(
                    h.get('aula_id') == aula['id'] for h in horarios_conflicto
                )

                if not aula_ocupada:
                    aulas_disponibles.append({
                        'id': aula['id'],
                        'nombre': aula['nombre'],
                        'tipo': aula.get('tipo', ''),
                        'capacidad': aula.get('capacidad', 0),
                        'sede': aula.get('id_sede', ''),
                        'recursos': aula.get('id_recursos', [])
                    })
                else:
                    aulas_no_disponibles.append({
                        'id': aula['id'],
                        'nombre': aula['nombre'],
                        'razon': f'Aula ocupada en el horario {hora_inicio}-{hora_fin} el {dia}'
                    })
            else:
                aulas_no_disponibles.append({
                    'id': aula['id'],
                    'nombre': aula['nombre'],
                    'razon': error
                })

        return {
            'asignatura': {
                'id': asignatura['id'],
                'nombre': asignatura['nombre'],
                'tipo': asignatura.get('tipo', 'teorica')
            },
            'horario_solicitado': {
                'dia': dia,
                'hora_inicio': hora_inicio,
                'hora_fin': hora_fin,
                'cantidad_estudiantes': cantidad_estudiantes,
                'semestre': semestre
            },
            'aulas_disponibles': aulas_disponibles,
            'aulas_no_disponibles': aulas_no_disponibles,
            'total_disponibles': len(aulas_disponibles),
            'total_no_disponibles': len(aulas_no_disponibles)
        }

    def _horarios_solapan(self, h1: Dict, h2: Dict) -> bool:
        """Verifica si dos horarios se solapan."""
        if not all(k in h1 for k in ['start_time', 'end_time']) or \
                not all(k in h2 for k in ['start_time', 'end_time']):
            return False

        inicio1, fin1 = h1['start_time'], h1['end_time']
        inicio2, fin2 = h2['start_time'], h2['end_time']
        return not (fin1 <= inicio2 or fin2 <= inicio1)