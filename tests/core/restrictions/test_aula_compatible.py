import unittest
import json
import os

from src.core.restrictions.aulas.aula_compatible_handler import AulaCompatibleHandler

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
        # Buscar asignatura y aula por id
        asignatura = next(a for a in self.asignaturas if a["id"] == "A004")
        aula = next(a for a in self.aulas if a["id"] == "AU002")
        # Forzar tipo para el test
        asignatura = {**asignatura, "tipo": "laboratorio"}
        aula = {**aula, "tipo": "laboratorio"}
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
        asignatura = next(a for a in self.asignaturas if a["id"] == "A004")
        aula = next(a for a in self.aulas if a["id"] == "AU001")
        # Forzar tipo para el test
        asignatura = {**asignatura, "tipo": "laboratorio"}
        aula = {**aula, "tipo": "teorica"}
        context = {
            "aula": aula,
            "asignatura": asignatura
        }
        result = self.handler.validate(context)
        print(f"\n{result}")
        self.assertIsInstance(result, str)
        self.assertIn("laboratorio", result.lower())
        self.assertIn(asignatura["nombre"], result)
        self.assertIn(aula["nombre"], result)

    def test_asignatura_teorica_en_aula_teorica(self):
        """
        Una asignatura teórica en aula teórica.
        Debe retornar None (válido).
        """
        asignatura = next(a for a in self.asignaturas if a["id"] == "A001")
        aula = next(a for a in self.aulas if a["id"] == "AU001")
        # Forzar tipo para el test
        asignatura = {**asignatura, "tipo": "teorica"}
        aula = {**aula, "tipo": "teorica"}
        context = {
            "aula": aula,
            "asignatura": asignatura
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_asignatura_teorica_en_aula_laboratorio(self):
        """
        Una asignatura teórica en aula laboratorio.
        Debe retornar None (válido).
        """
        asignatura = next(a for a in self.asignaturas if a["id"] == "A001")
        aula = next(a for a in self.aulas if a["id"] == "AU002")
        # Forzar tipo para el test
        asignatura = {**asignatura, "tipo": "teorica"}
        aula = {**aula, "tipo": "laboratorio"}
        context = {
            "aula": aula,
            "asignatura": asignatura
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_error_por_datos_incompletos(self):
        """
        Si falta el aula o la asignatura, debe retornar un mensaje de error.
        """
        context = {"aula": {}, "asignatura": {}}
        result = self.handler.validate(context)
        self.assertIsInstance(result, str)
        self.assertIn("faltan datos", result.lower())

    def test_error_por_tipo_no_definido(self):
        """
        Si falta el tipo en aula o asignatura, debe retornar un mensaje de error.
        """
        asignatura = {"id": "A001", "nombre": "Álgebra Lineal"}
        aula = {"id": "AU001", "nombre": "Aula 101"}
        context = {"aula": aula, "asignatura": asignatura}
        result = self.handler.validate(context)
        self.assertIsInstance(result, str)
        self.assertIn("no están definidos", result.lower())

if __name__ == '__main__':
    unittest.main()