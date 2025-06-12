import json
import os
from typing import Dict, Any

def load_json(filename: str) -> Dict[str, Any]:
    """Helper para cargar archivos JSON desde el directorio de datos."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, '../../../../data'))
    try:
        with open(os.path.join(data_dir, filename), encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

class BuilderTestData:
    """Clase helper que proporciona datos de prueba consistentes para todos los tests."""

    @classmethod
    def get_test_data(cls):
        """Retorna datos de prueba para los builders."""
        # Intentar cargar datos reales, usar fallback si no están disponibles
        asignaturas = load_json("asignaturas.json") or [
            {"id": "ASG001", "nombre": "Álgebra Lineal", "estado": "activo", "permite_laboratorio": True},
            {"id": "ASG002", "nombre": "Física I", "estado": "activo", "permite_laboratorio": True, "solo_laboratorio": False},
            {"id": "ASG003", "nombre": "Laboratorio Química", "estado": "activo", "permite_laboratorio": True, "solo_laboratorio": True},
            {"id": "BLQ001", "nombre": "Mantenimiento", "estado": "activo", "tipo": "bloqueo"}
        ]

        aulas = load_json("aulas.json") or [
            {"id": "AU001", "nombre": "Aula 101", "tipo": "aula", "estado": "activo", "capacidad": 30},
            {"id": "AU002", "nombre": "Aula 102", "tipo": "teorica", "estado": "activo", "capacidad": 40},
            {"id": "LAB001", "nombre": "Lab Química", "tipo": "laboratorio", "estado": "activo", "capacidad": 20},
            {"id": "LAB002", "nombre": "Lab Física", "tipo": "laboratorio", "estado": "activo", "capacidad": 25}
        ]

        docentes = load_json("docentes.json") or [
            {"id": "DOC001", "nombre": "Laura", "apellido": "García", "estado": "activo"},
            {"id": "DOC002", "nombre": "Carlos", "apellido": "Rodríguez", "estado": "activo"},
            {"id": "DOC003", "nombre": "Ana", "apellido": "Martínez", "estado": "activo"}
        ]

        sedes = load_json("sedes.json") or [
            {"id": "SEDE001", "nombre": "Campus Principal", "estado": "activo"},
            {"id": "SEDE002", "nombre": "Campus Norte", "estado": "activo"}
        ]

        return {
            'asignaturas': asignaturas,
            'aulas': aulas,
            'docentes': docentes,
            'sedes': sedes
        }

    @classmethod
    def get_valid_horario_data(cls):
        """Retorna datos válidos para crear un horario."""
        data = cls.get_test_data()
        return {
            'docente': data['docentes'][0],
            'aula': data['aulas'][0],
            'asignatura': data['asignaturas'][0],
            'start_time': '08:00',
            'end_time': '10:00',
            'dia': 'Lunes',
            'sede': data['sedes'][0],
            'id': 'H001'
        }

    @classmethod
    def get_laboratorio_data(cls):
        """Retorna datos válidos para crear un horario de laboratorio."""
        data = cls.get_test_data()
        # Buscar específicamente un aula de laboratorio
        laboratorio_aula = next((aula for aula in data['aulas'] if aula['tipo'] == 'laboratorio'), None)
        if laboratorio_aula is None:
            # Si no hay laboratorio en los datos, crear uno
            laboratorio_aula = {"id": "LAB001", "nombre": "Lab Química", "tipo": "laboratorio", "estado": "activo", "capacidad": 20}

        return {
            'docente': data['docentes'][0],
            'aula': laboratorio_aula,
            'asignatura': data['asignaturas'][1],
            'start_time': '14:00',
            'end_time': '16:00',
            'dia': 'Miércoles',
            'sede': data['sedes'][0],
            'id': 'LAB001'
        }

    @classmethod
    def get_virtual_data(cls):
        """Retorna datos válidos para crear un horario virtual."""
        data = cls.get_test_data()
        return {
            'docente': data['docentes'][1],
            'aula': None,
            'asignatura': data['asignaturas'][0],
            'start_time': '10:00',
            'end_time': '11:30',
            'dia': 'Viernes',
            'sede': None,
            'id': 'VIR001'
        }

    @classmethod
    def get_bloqueo_data(cls):
        """Retorna datos válidos para crear un horario de bloqueo."""
        data = cls.get_test_data()
        return {
            'docente': None,
            'aula': data['aulas'][0],
            'asignatura': data['asignaturas'][4],  # Bloqueo
            'start_time': '12:00',
            'end_time': '13:00',
            'dia': 'Martes',
            'sede': data['sedes'][0],
            'id': 'BLQ001'
        }