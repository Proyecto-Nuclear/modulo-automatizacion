import unittest
import json
import os

from src.core.restrictions.aula_compatible_handler import AulaCompatibleHandler

def load_json(filename):
    """Helper to load JSON from the data directory."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, '../../../data'))
    with open(os.path.join(data_dir, filename), encoding="utf-8") as f:
        return json.load(f)

class AulaCompatibleHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.asignaturas = load_json("asignaturas.json")
        self.aulas = load_json("aulas.json")
        self.handler = AulaCompatibleHandler()

    def test_laboratorio_en_aula_laboratorio(self):
        """
        Una asignatura de laboratorio en aula de tipo laboratorio.
        Debe retornar None (válido).
        """
        # Simulamos que la asignatura es de tipo laboratorio
        asignatura = {"id": "A004", "nombre": "Algoritmos y Lógica Computacional", "tipo": "Laboratorio"}
        aula = {"id": "AU002", "nombre": "Lab Computo 1", "tipo": "laboratorio"}
        context = {
            "aula": aula,
            "asignatura": asignatura
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_laboratorio_en_aula_no_laboratorio(self):
        """
        Una asignatura de laboratorio en aula que NO es laboratorio.
        Debe retornar mensaje de error.
        """
        asignatura = {"id": "A004", "nombre": "Algoritmos y Lógica Computacional", "tipo": "Laboratorio"}
        aula = {"id": "AU001", "nombre": "Aula 101", "tipo": "Teorica"}
        context = {
            "aula": aula,
            "asignatura": asignatura
        }
        result = self.handler.validate(context)
        print(f"\n{result}")
        self.assertIsInstance(result, str)
        self.assertIn("laboratorio", result.lower())
        self.assertIn("Algoritmos y Lógica Computacional", result)
        self.assertIn("Aula 101", result)

    def test_asignatura_no_laboratorio_en_aula_teorica(self):
        """
        Una asignatura teórica en aula teórica.
        Debe retornar None (válido).
        """
        asignatura = {"id": "A001", "nombre": "Álgebra Lineal", "tipo": "Teorica"}
        aula = {"id": "AU001", "nombre": "Aula 101", "tipo": "Teorica"}
        context = {
            "aula": aula,
            "asignatura": asignatura
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_asignatura_no_laboratorio_en_aula_laboratorio(self):
        """
        Una asignatura teórica en aula laboratorio.
        Debe retornar None (válido).
        """
        asignatura = {"id": "A001", "nombre": "Álgebra Lineal", "tipo": "Teorica"}
        aula = {"id": "AU002", "nombre": "Lab Computo 1", "tipo": "laboratorio"}
        context = {
            "aula": aula,
            "asignatura": asignatura
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()