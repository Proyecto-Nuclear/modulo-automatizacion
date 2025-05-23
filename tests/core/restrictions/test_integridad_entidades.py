import unittest
from src.core.restrictions.integridad_entidades_handler import IntegridadEntidadesHandler

class IntegridadEntidadesHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.handler = IntegridadEntidadesHandler()

        self.valid_context = {
            "aula": {"id": "AU001", "estado": "activo"},
            "docente": {"id": "DOC001", "estado": "activo"},
            "asignatura": {"id": "ASG001", "estado": "activo"},
            "sede": {"id": "SEDE001", "estado": "activo"}
        }

    def test_todas_entidades_activas(self):
        result = self.handler.validate(self.valid_context)
        self.assertIsNone(result, "Debe retornar None si todas las entidades están activas")

    def test_aula_inactiva(self):
        context = self.valid_context.copy()
        context["aula"] = {"id": "AU001", "estado": "inactivo"}
        result = self.handler.validate(context)
        print(f"\n{result}")
        self.assertIsInstance(result, str)
        self.assertIn("aula", result)
        self.assertIn("no está activa", result)

    def test_docente_inactivo(self):
        context = self.valid_context.copy()
        context["docente"] = {"id": "DOC001", "estado": "INACTIVO"}
        result = self.handler.validate(context)
        print(f"\n{result}")
        self.assertIsInstance(result, str)
        self.assertIn("docente", result)
        self.assertIn("no está activa", result)

    def test_asignatura_inactiva(self):
        context = self.valid_context.copy()
        context["asignatura"] = {"id": "ASG001", "estado": "INACTIVO"}
        result = self.handler.validate(context)
        print(f"\n{result}")
        self.assertIsInstance(result, str)
        self.assertIn("asignatura", result)
        self.assertIn("no está activa", result)

    def test_sede_inactiva(self):
        context = self.valid_context.copy()
        context["sede"] = {"id": "SEDE001", "estado": "inactivo"}
        result = self.handler.validate(context)
        print(f"\n{result}")
        self.assertIsInstance(result, str)
        self.assertIn("sede", result)
        self.assertIn("no está activa", result)

    def test_entidad_faltante(self):
        context = self.valid_context.copy()
        del context["docente"]
        result = self.handler.validate(context)
        print(f"\n{result}")
        self.assertIsInstance(result, str)
        self.assertIn("docente", result)
        self.assertIn("no esta definida", result)

if __name__ == '__main__':
    unittest.main()