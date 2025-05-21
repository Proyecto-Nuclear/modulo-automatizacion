import unittest
import json
import os

from src.core.restrictions.docente_no_traslapado_handler import DocenteNoTraslapadoHandler

def load_json(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, '../../../data'))
    with open(os.path.join(data_dir, filename), encoding="utf-8") as f:
        return json.load(f)

def get_docente_by_id(docentes, docente_id):
    return next((d for d in docentes if d["id"] == docente_id), None)

class DocenteNoTraslapadoHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.docentes = load_json("docentes.json")
        self.handler = DocenteNoTraslapadoHandler()

    def test_docente_no_traslapado_conflicto(self):
        """Superposición de horarios para el mismo docente: debe ser inválido (conflicto)."""
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
        if result is not None:
            print("")
            print(result)
        self.assertIsInstance(result, str)
        self.assertIn(nombre, result)

    def test_docente_no_traslapado_ok(self):
        """Sin superposición para el mismo docente: debe ser válido (Ninguno)."""
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
        if result is not None:
            print("Error inesperado:", result)
        self.assertIsNone(result)

    def test_docente_diferente_docente(self):
        """Docente diferente, tiempo superpuesto: debería ser válido (Ninguno)."""
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
        if result is not None:
            print("Error inesperado (profesor diferente):", result)
        self.assertIsNone(result)

    def test_docente_diferente_date(self):
        """Mismo profesor, diferente fecha: debe ser válido (Ninguno)."""
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
        if result is not None:
            print("Error inesperado (fecha diferente):", result)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()