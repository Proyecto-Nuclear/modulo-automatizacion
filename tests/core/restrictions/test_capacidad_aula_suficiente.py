import unittest
import json
import os

from src.core.restrictions.capacidad_aula_suficiente_handler import CapacidadAulaSuficienteHandler

def load_json(filename):
    """Helper to load JSON from the data directory."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, '../../../data'))
    with open(os.path.join(data_dir, filename), encoding="utf-8") as f:
        return json.load(f)

class CapacidadAulaSuficienteHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.asignaturas = load_json("asignaturas.json")
        self.aulas = load_json("aulas.json")
        self.handler = CapacidadAulaSuficienteHandler()

    def test_aula_con_capacidad_suficiente(self):
        """
        El aula tiene suficiente capacidad para la cantidad de estudiantes.
        Debe retornar None (válido).
        """
        asignatura = next(a for a in self.asignaturas if a["id"] == "A003")
        aula = next(a for a in self.aulas if a["id"] == "AU001")  # Aula 101, capacidad 40
        context = {
            "aula": aula,
            "numero_estudiantes": 35,
            "asignatura": asignatura,
            "aulas": self.aulas
        }
        result = self.handler.validate(context)
        if result is not None:
            print("Error inesperado:", result)
        self.assertIsNone(result)

    def test_aula_con_capacidad_exacta(self):
        """
        El aula tiene exactamente la capacidad requerida por la cantidad de estudiantes.
        Debe retornar None (válido).
        """
        asignatura = next(a for a in self.asignaturas if a["id"] == "A002")
        aula = next(a for a in self.aulas if a["id"] == "AU002")  # Lab Computo 1, capacidad 25
        context = {
            "aula": aula,
            "numero_estudiantes": 25,
            "asignatura": asignatura,
            "aulas": self.aulas
        }
        result = self.handler.validate(context)
        if result is not None:
            print("Error inesperado:", result)
        self.assertIsNone(result)

    def test_aula_con_capacidad_insuficiente(self):
        """
        El aula NO tiene capacidad suficiente para la cantidad de estudiantes.
        Debe retornar un mensaje de error y recomendar aulas con capacidad suficiente.
        """
        asignatura = next(a for a in self.asignaturas if a["id"] == "A001")
        aula = next(a for a in self.aulas if a["id"] == "AU003")  # Aula 201, capacidad 35
        context = {
            "aula": aula,
            "numero_estudiantes": 40,
            "asignatura": asignatura,
            "aulas": self.aulas
        }
        result = self.handler.validate(context)
        print(f"\n{result}")
        self.assertIsInstance(result, str)
        self.assertIn("capacidad", result.lower())
        self.assertIn("Aula 201", result)
        self.assertIn("Álgebra Lineal", result)
        self.assertIn("40", result)
        self.assertIn("Aula 101", result)  # Recomendación

    def test_falta_numero_estudiantes(self):
        """
        Si no se proporciona el número de estudiantes, debe retornar un mensaje de error.
        """
        asignatura = next(a for a in self.asignaturas if a["id"] == "A003")
        aula = next(a for a in self.aulas if a["id"] == "AU001")
        context = {
            "aula": aula,
            "asignatura": asignatura,
            "aulas": self.aulas
        }
        result = self.handler.validate(context)
        print(result)
        self.assertIsInstance(result, str)
        self.assertIn("no se proporcionó", result.lower())

if __name__ == '__main__':
    unittest.main()