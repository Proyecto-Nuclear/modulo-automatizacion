import unittest
import json
import os

from src.core.restrictions.docente.docente_no_traslapado_handler import DocenteNoTraslapadoHandler

def load_json(filename):
    """Helper to load JSON from the data directory."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, '../../../data'))
    with open(os.path.join(data_dir, filename), encoding="utf-8") as f:
        return json.load(f)

def get_docente_by_id(docentes, docente_id):
    """Helper to get docente by ID."""
    return next((d for d in docentes if d["id"] == docente_id), None)

class DocenteNoTraslapadoHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.docentes = load_json("docentes.json")
        self.handler = DocenteNoTraslapadoHandler()

    # ========== TESTS DE VALIDACIÓN DIRECTA (Compatibilidad con versión anterior) ==========

    def test_docente_no_traslapado_conflicto_directo(self):
        """Superposición de horarios para el mismo docente: debe ser inválido (validación directa)."""
        context = {
            "schedule": [
                {
                    "docente_id": "D001",
                    "date": "2025-05-21",
                    "start_time": "08:00",
                    "end_time": "10:00"
                }
            ],
            "new_schedule": {
                "docente_id": "D001",
                "date": "2025-05-21",
                "start_time": "09:30",
                "end_time": "11:00"
            },
            "docentes": self.docentes
        }
        result = self.handler.validate(context)
        docente = get_docente_by_id(self.docentes, "D001")
        nombre = f"{docente['nombre']} {docente['apellido']}" if docente else "Unknown"
        print(f"\nValidación directa - conflicto: {result}")
        self.assertIsInstance(result, str)
        self.assertIn(nombre, result)
        self.assertIn("conflicto", result.lower())

    def test_docente_no_traslapado_ok_directo(self):
        """Sin superposición para el mismo docente: debe ser válido (validación directa)."""
        context = {
            "schedule": [
                {
                    "docente_id": "D001",
                    "date": "2025-05-21",
                    "start_time": "08:00",
                    "end_time": "10:00"
                }
            ],
            "new_schedule": {
                "docente_id": "D001",
                "date": "2025-05-21",
                "start_time": "10:00",
                "end_time": "12:00"
            },
            "docentes": self.docentes
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_docente_diferente_docente_directo(self):
        """Docente diferente, tiempo superpuesto: debería ser válido (validación directa)."""
        context = {
            "schedule": [
                {
                    "docente_id": "D002",
                    "date": "2025-05-21",
                    "start_time": "09:00",
                    "end_time": "11:00"
                }
            ],
            "new_schedule": {
                "docente_id": "D001",
                "date": "2025-05-21",
                "start_time": "09:30",
                "end_time": "11:00"
            },
            "docentes": self.docentes
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_docente_diferente_fecha_directo(self):
        """Mismo profesor, diferente fecha: debe ser válido (validación directa)."""
        context = {
            "schedule": [
                {
                    "docente_id": "D001",
                    "date": "2025-05-20",
                    "start_time": "09:00",
                    "end_time": "11:00"
                }
            ],
            "new_schedule": {
                "docente_id": "D001",
                "date": "2025-05-21",
                "start_time": "09:30",
                "end_time": "11:00"
            },
            "docentes": self.docentes
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    # ========== TESTS DE VALIDACIÓN INDIVIDUAL (Enfoque 2) ==========

    def test_validar_bloque_individual_con_conflicto(self):
        """Validación individual: nuevo bloque con conflicto de horario."""
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "docente_id": "D001",
                "dia": "lunes",
                "hora_inicio": "09:30",
                "hora_fin": "11:00"
            },
            "horarios_existentes": [
                {
                    "id": "H_EXIST",
                    "docente_id": "D001",
                    "dia": "lunes",
                    "hora_inicio": "08:00",
                    "hora_fin": "10:00"
                }
            ],
            "docentes": self.docentes
        }
        result = self.handler.validate(context)
        print(f"\nValidación individual - con conflicto: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("conflicto", result.lower())
        self.assertIn("lunes", result)

    def test_validar_bloque_individual_sin_conflicto(self):
        """Validación individual: nuevo bloque sin conflicto de horario."""
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "docente_id": "D001",
                "dia": "lunes",
                "hora_inicio": "10:00",
                "hora_fin": "12:00"
            },
            "horarios_existentes": [
                {
                    "id": "H_EXIST",
                    "docente_id": "D001",
                    "dia": "lunes",
                    "hora_inicio": "08:00",
                    "hora_fin": "10:00"
                }
            ],
            "docentes": self.docentes
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_validar_bloque_individual_docente_diferente(self):
        """Validación individual: nuevo bloque con docente diferente (sin conflicto)."""
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "docente_id": "D002",
                "dia": "lunes",
                "hora_inicio": "09:30",
                "hora_fin": "11:00"
            },
            "horarios_existentes": [
                {
                    "id": "H_EXIST",
                    "docente_id": "D001",
                    "dia": "lunes",
                    "hora_inicio": "08:00",
                    "hora_fin": "10:00"
                }
            ],
            "docentes": self.docentes
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_validar_bloque_individual_dia_diferente(self):
        """Validación individual: nuevo bloque en día diferente (sin conflicto)."""
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "docente_id": "D001",
                "dia": "martes",
                "hora_inicio": "09:30",
                "hora_fin": "11:00"
            },
            "horarios_existentes": [
                {
                    "id": "H_EXIST",
                    "docente_id": "D001",
                    "dia": "lunes",
                    "hora_inicio": "08:00",
                    "hora_fin": "10:00"
                }
            ],
            "docentes": self.docentes
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_validar_bloque_individual_datos_faltantes(self):
        """Validación individual: nuevo bloque con datos faltantes."""
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "dia": "lunes",
                "hora_inicio": "09:30"
                # Faltan docente_id y hora_fin
            },
            "horarios_existentes": [],
            "docentes": self.docentes
        }
        result = self.handler.validate(context)
        self.assertIsInstance(result, str)
        self.assertIn("debe tener", result)

    # ========== TESTS DE VALIDACIÓN GLOBAL (Enfoque 2) ==========

    def test_validar_horarios_globales_sin_conflictos(self):
        """Validación global: horarios sin conflictos."""
        context = {
            "schedules": [
                {
                    "id": "H1",
                    "docente_id": "D001",
                    "dia": "lunes",
                    "hora_inicio": "08:00",
                    "hora_fin": "10:00"
                },
                {
                    "id": "H2",
                    "docente_id": "D001",
                    "dia": "lunes",
                    "hora_inicio": "10:00",
                    "hora_fin": "12:00"
                },
                {
                    "id": "H3",
                    "docente_id": "D002",
                    "dia": "lunes",
                    "hora_inicio": "09:00",
                    "hora_fin": "11:00"
                }
            ],
            "docentes": self.docentes
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_validar_horarios_globales_con_conflictos(self):
        """Validación global: horarios con conflictos."""
        context = {
            "schedules": [
                {
                    "id": "H1",
                    "docente_id": "D001",
                    "dia": "lunes",
                    "hora_inicio": "08:00",
                    "hora_fin": "10:00"
                },
                {
                    "id": "H2",
                    "docente_id": "D001",
                    "dia": "lunes",
                    "hora_inicio": "09:30",
                    "hora_fin": "11:30"
                }
            ],
            "docentes": self.docentes
        }
        result = self.handler.validate(context)
        print(f"\nValidación global - con conflictos: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("conflicto", result.lower())

    def test_validar_horarios_globales_vacios(self):
        """Validación global: lista de horarios vacía."""
        context = {
            "schedules": [],
            "docentes": self.docentes
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    # ========== TESTS DE MÉTODOS AUXILIARES ==========

    def test_obtener_docentes_disponibles(self):
        """Test del método auxiliar para obtener docentes disponibles."""
        context = {
            "dia": "lunes",
            "hora_inicio": "14:00",
            "hora_fin": "16:00",
            "todos_docentes": self.docentes,
            "horarios_existentes": [
                {
                    "docente_id": "D001",
                    "dia": "lunes",
                    "hora_inicio": "14:30",
                    "hora_fin": "16:30"
                }
            ]
        }
        docentes_disponibles = self.handler.obtener_docentes_disponibles(context)
        print(f"\nDocentes disponibles lunes 14:00-16:00: {docentes_disponibles}")
        self.assertIsInstance(docentes_disponibles, list)
        self.assertNotIn("D001", docentes_disponibles)  # D001 tiene conflicto

    def test_es_docente_disponible_true(self):
        """Test del método auxiliar para verificar disponibilidad (disponible)."""
        context = {
            "horarios_existentes": [
                {
                    "docente_id": "D001",
                    "dia": "lunes",
                    "hora_inicio": "08:00",
                    "hora_fin": "10:00"
                }
            ]
        }
        # D001 debería estar disponible de 10:00 a 12:00 (no hay conflicto)
        disponible = self.handler.es_docente_disponible("D001", "lunes", "10:00", "12:00", context)
        self.assertTrue(disponible)

    def test_es_docente_disponible_false(self):
        """Test del método auxiliar para verificar disponibilidad (no disponible)."""
        context = {
            "horarios_existentes": [
                {
                    "docente_id": "D001",
                    "dia": "lunes",
                    "hora_inicio": "08:00",
                    "hora_fin": "10:00"
                }
            ]
        }
        # D001 NO debería estar disponible de 09:00 a 11:00 (hay conflicto)
        disponible = self.handler.es_docente_disponible("D001", "lunes", "09:00", "11:00", context)
        self.assertFalse(disponible)

    def test_obtener_conflictos_docente(self):
        """Test del método auxiliar para obtener conflictos por docente."""
        context = {
            "schedules": [
                {
                    "id": "H1",
                    "docente_id": "D001",
                    "dia": "lunes",
                    "hora_inicio": "08:00",
                    "hora_fin": "10:00"
                },
                {
                    "id": "H2",
                    "docente_id": "D001",
                    "dia": "lunes",
                    "hora_inicio": "09:30",
                    "hora_fin": "11:30"
                },
                {
                    "id": "H3",
                    "docente_id": "D002",
                    "dia": "lunes",
                    "hora_inicio": "14:00",
                    "hora_fin": "16:00"
                }
            ],
            "docentes": self.docentes
        }
        conflictos = self.handler.obtener_conflictos_docente(context)
        print(f"\nConflictos por docente: {conflictos}")
        self.assertIsInstance(conflictos, dict)
        self.assertIn("D001", conflictos)  # D001 tiene conflictos
        self.assertNotIn("D002", conflictos)  # D002 no tiene conflictos

    # ========== TESTS DE CASOS EDGE ==========

    def test_horarios_exactamente_consecutivos(self):
        """Test de horarios exactamente consecutivos (sin traslape)."""
        context = {
            "nuevo_bloque": {
                "docente_id": "D001",
                "dia": "lunes",
                "hora_inicio": "10:00",
                "hora_fin": "12:00"
            },
            "horarios_existentes": [
                {
                    "docente_id": "D001",
                    "dia": "lunes",
                    "hora_inicio": "08:00",
                    "hora_fin": "10:00"
                }
            ],
            "docentes": self.docentes
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)  # No debería haber conflicto

    def test_traslape_parcial_inicio(self):
        """Test de traslape parcial al inicio."""
        context = {
            "nuevo_bloque": {
                "docente_id": "D001",
                "dia": "lunes",
                "hora_inicio": "07:30",
                "hora_fin": "08:30"
            },
            "horarios_existentes": [
                {
                    "docente_id": "D001",
                    "dia": "lunes",
                    "hora_inicio": "08:00",
                    "hora_fin": "10:00"
                }
            ],
            "docentes": self.docentes
        }
        result = self.handler.validate(context)
        self.assertIsInstance(result, str)  # Debería haber conflicto

    def test_traslape_parcial_final(self):
        """Test de traslape parcial al final."""
        context = {
            "nuevo_bloque": {
                "docente_id": "D001",
                "dia": "lunes",
                "hora_inicio": "09:30",
                "hora_fin": "10:30"
            },
            "horarios_existentes": [
                {
                    "docente_id": "D001",
                    "dia": "lunes",
                    "hora_inicio": "08:00",
                    "hora_fin": "10:00"
                }
            ],
            "docentes": self.docentes
        }
        result = self.handler.validate(context)
        self.assertIsInstance(result, str)  # Debería haber conflicto

    def test_horario_completamente_contenido(self):
        """Test de horario completamente contenido dentro de otro."""
        context = {
            "nuevo_bloque": {
                "docente_id": "D001",
                "dia": "lunes",
                "hora_inicio": "08:30",
                "hora_fin": "09:30"
            },
            "horarios_existentes": [
                {
                    "docente_id": "D001",
                    "dia": "lunes",
                    "hora_inicio": "08:00",
                    "hora_fin": "10:00"
                }
            ],
            "docentes": self.docentes
        }
        result = self.handler.validate(context)
        self.assertIsInstance(result, str)  # Debería haber conflicto

if __name__ == '__main__':
    unittest.main()