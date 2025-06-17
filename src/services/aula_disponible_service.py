from typing import List, Dict, Any
import json
import os

from src.core.restrictions.aulas.aula_compatible_handler import AulaCompatibleHandler
from src.core.restrictions.aulas.aula_no_ocupada_doble_handler import AulaNoOcupadaDobleHandler
from src.core.restrictions.aulas.capacidad_aula_suficiente_handler import CapacidadAulaSuficienteHandler

class AulaDisponibleService:
    """
    Servicio para determinar qué aulas están disponibles para una asignatura
    basándose en las restricciones definidas y en las programaciones existentes.
    """

    def __init__(self):
        self.data_dir = self._get_data_dir()
        self._setup_restriction_chain()

    def _get_data_dir(self) -> str:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.abspath(os.path.join(base_dir, '../../data'))
        return data_dir

    def _setup_restriction_chain(self):
        self.capacidad_handler = CapacidadAulaSuficienteHandler()
        self.compatibilidad_handler = AulaCompatibleHandler()
        self.ocupacion_handler = AulaNoOcupadaDobleHandler()
        self.capacidad_handler.set_next(self.compatibilidad_handler)
        self.compatibilidad_handler.set_next(self.ocupacion_handler)

    def _load_json_data(self, filename: str) -> List[Dict[str, Any]]:
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
        # Cargar datos
        aulas = self._load_json_data('aulas.json')
        asignaturas = self._load_json_data('asignaturas.json')
        sedes = self._load_json_data('sedes.json')
        recursos = self._load_json_data('recursos.json')
        programaciones = self._load_json_data('programaciones.json')

        # Buscar la asignatura
        asignatura = next((a for a in asignaturas if a['id'] == asignatura_id), None)
        if not asignatura:
            return {
                'error': f'Asignatura con ID {asignatura_id} no encontrada',
                'aulas_disponibles': [],
                'aulas_no_disponibles': []
            }

        # 1. Filtrar aulas ocupadas o reservadas en ese horario y día (sin importar semestre)
        aulas_ocupadas = set()
        for prog in programaciones:
            if prog.get('estado') in ('reservado', 'ocupado') and prog.get('dia') == dia:
                if self._horarios_solapan(
                        {'start_time': hora_inicio, 'end_time': hora_fin},
                        {'start_time': prog.get('hora_inicio'), 'end_time': prog.get('hora_fin')}
                ):
                    aulas_ocupadas.add(prog['aula_id'])

        aulas_disponibles = []
        aulas_no_disponibles = []

        # Evaluar cada aula
        for aula in aulas:
            if aula.get('estado', '').lower() != 'activo':
                continue

            sede_id = aula.get('id_sede', '')
            sede_nombre = next((s['nombre'] for s in sedes if s['id'] == sede_id), sede_id)

            recursos_ids = aula.get('id_recursos', [])
            recursos_nombres = [
                next((r['nombre'] for r in recursos if r['id'] == rid), rid)
                for rid in recursos_ids
            ]

            # Aplicar restricciones de capacidad y compatibilidad
            context = {
                'aula': aula,
                'asignatura': asignatura,
                'numero_estudiantes': cantidad_estudiantes,
                'aulas': aulas,
                'schedules': [],  # Ya no usamos horarios_conflicto
                'dia': dia,
                'hora_inicio': hora_inicio,
                'hora_fin': hora_fin
            }

            error = self.capacidad_handler.handle(context)

            if error is None:
                if aula['id'] in aulas_ocupadas:
                    aulas_no_disponibles.append({
                        'id': aula['id'],
                        'nombre': aula['nombre'],
                        'razon': f"Aula ocupada o reservada en el horario {hora_inicio}-{hora_fin} el {dia}"
                    })
                else:
                    aulas_disponibles.append({
                        'id': aula['id'],
                        'nombre': aula['nombre'],
                        'tipo': aula.get('tipo', ''),
                        'capacidad': aula.get('capacidad', 0),
                        'sede': {
                            'id': sede_id,
                            'nombre': sede_nombre
                        },
                        'recursos': [
                            {'id': rid, 'nombre': rnombre}
                            for rid, rnombre in zip(recursos_ids, recursos_nombres)
                        ]
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
            'total_no_disponibles': len(aulas_no_disponibles),
            'error': None
        }

    def _horarios_solapan(self, h1: Dict, h2: Dict) -> bool:
        """Verifica si dos horarios se solapan."""
        if not all(k in h1 for k in ['start_time', 'end_time']) or \
                not all(k in h2 for k in ['start_time', 'end_time']):
            return False

        inicio1, fin1 = h1['start_time'], h1['end_time']
        inicio2, fin2 = h2['start_time'], h2['end_time']
        return not (fin1 <= inicio2 or fin2 <= inicio1)