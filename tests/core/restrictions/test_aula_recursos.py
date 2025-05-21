import unittest
import json
import os

from src.core.restrictions.aula_recursos_handler import AulaRecursosHandler

def load_json(filename):
    """Helper to load JSON from the data directory."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, '../../../data'))
    with open(os.path.join(data_dir, filename), encoding="utf-8") as f:
        return json.load(f)

class AulaDebeTenerRecursosHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.asignaturas = load_json("asignaturas.json")
        self.aulas = load_json("aulas.json")
        self.recursos = load_json("recursos.json")
        self.handler = AulaRecursosHandler()

    def test_aula_con_todos_los_recursos(self):
        """
        El aula tiene todos los recursos requeridos por la asignatura.
        Debe retornar None (válido).
        """
        # Estructura de Datos requiere ["R001", "R003"]
        asignatura = next(a for a in self.asignaturas if a["id"] == "A003")
        # Aula "Lab Computo 1" tiene ["R003"], pero "Aula 101" tiene ["R001", "R002"]
        # Necesitamos un aula que tenga ambos, así que agregamos un aula de prueba:
        aula = {
            "id": "AU_TEST",
            "nombre": "Aula Completa",
            "estado": "disponible",
            "codigo": "A999",
            "descripcion": "Aula de prueba con todos los recursos",
            "tipo": "Teorica",
            "capacidad": 40,
            "id_sede": "S001",
            "id_recursos": ["R001", "R003"]
        }
        context = {
            "aula": aula,
            "asignatura": asignatura,
            "recursos": self.recursos
        }
        result = self.handler.validate(context)
        if result is not None:
            print("Error inesperado:", result)
        self.assertIsNone(result)

    def test_aula_faltan_recursos(self):
        """
        El aula no tiene todos los recursos requeridos por la asignatura.
        Debe retornar mensaje de error indicando los recursos faltantes.
        """
        # Estructura de Datos requiere ["R001", "R003"]
        asignatura = next(a for a in self.asignaturas if a["id"] == "A003")
        # Aula "Lab Computo 1" solo tiene ["R003"] (falta "R001")
        aula = next(a for a in self.aulas if a["id"] == "AU002")
        context = {
            "aula": aula,
            "asignatura": asignatura,
            "recursos": self.recursos
        }
        result = self.handler.validate(context)
        print(f"\n{result}")
        self.assertIsInstance(result, str)
        self.assertIn("falta", result.lower() or "faltante" in result.lower())
        self.assertIn("Video Beam", result)  # R001 es Video Beam

    def test_aula_sin_recursos_requeridos(self):
        """
        La asignatura no requiere recursos. El aula puede ser cualquiera.
        Debe retornar None.
        """
        # Creamos asignatura sin recursos requeridos
        asignatura = {
            "id": "A004",
            "nombre": "Historia",
            "estado": "activa",
            "duracion": "3 meses",
            "semestre": 1,
            "creditos": 2,
            "descripcion": "Historia universal",
            "requiereRecursos": []
        }
        aula = self.aulas[0]
        context = {
            "aula": aula,
            "asignatura": asignatura,
            "recursos": self.recursos
        }
        result = self.handler.validate(context)
        if result is not None:
            print("Error inesperado:", result)
        self.assertIsNone(result)

    def test_recursos_faltantes_por_id(self):
        """
        Si no se pasan los nombres de los recursos, igual debe funcionar mostrando los IDs faltantes.
        """
        asignatura = next(a for a in self.asignaturas if a["id"] == "A003")
        aula = next(a for a in self.aulas if a["id"] == "AU001")
        context = {
            "aula": aula,
            "asignatura": asignatura,
            # No se pasan los recursos para nombres
        }
        result = self.handler.validate(context)
        print(f"\nMensaje con IDs:", result)
        self.assertIsInstance(result, str)
        self.assertIn("R003", result)

if __name__ == '__main__':
    unittest.main()