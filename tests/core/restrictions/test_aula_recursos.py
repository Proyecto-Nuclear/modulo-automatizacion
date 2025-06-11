import unittest
import json
import os

from src.core.restrictions.aulas.aula_recursos_handler import AulaRecursosHandler

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

    # ========== TESTS DE VALIDACIÓN DIRECTA (Compatibilidad con versión anterior) ==========

    def test_aula_con_todos_los_recursos_directo(self):
        """
        El aula tiene todos los recursos requeridos por la asignatura (validación directa).
        Debe retornar None (válido).
        """
        # Estructura de Datos requiere ["R001", "R003"]
        asignatura = next(a for a in self.asignaturas if a["id"] == "A003")
        # Creamos un aula de prueba con todos los recursos necesarios
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
        self.assertIsNone(result)

    def test_aula_faltan_recursos_directo(self):
        """
        El aula no tiene todos los recursos requeridos por la asignatura (validación directa).
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
        print(f"\nValidación directa - recursos faltantes: {result}")
        self.assertIsInstance(result, str)
        self.assertTrue("faltante" in result.lower() or "falta" in result.lower())
        self.assertIn("Video Beam", result)  # R001 es Video Beam

    def test_aula_sin_recursos_requeridos_directo(self):
        """
        La asignatura no requiere recursos (validación directa). El aula puede ser cualquiera.
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
        self.assertIsNone(result)

    def test_recursos_faltantes_por_id_directo(self):
        """
        Si no se pasan los nombres de los recursos, debe mostrar los ID faltantes (validación directa).
        """
        asignatura = next(a for a in self.asignaturas if a["id"] == "A003")
        aula = next(a for a in self.aulas if a["id"] == "AU001")
        context = {
            "aula": aula,
            "asignatura": asignatura,
            # No se pasan los recursos para nombres
        }
        result = self.handler.validate(context)
        print(f"\nMensaje con IDs: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("R003", result)

    # ========== TESTS DE VALIDACIÓN INDIVIDUAL (Enfoque 2) ==========

    def test_validar_bloque_individual_con_recursos_suficientes(self):
        """
        Validación individual: nuevo bloque con aula que tiene recursos suficientes.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "aula_id": "AU002",  # Lab Computo 1 tiene ["R003"]
                "asignatura_id": "A002",  # Programación requiere ["R003"]
                "dia": "lunes",
                "hora_inicio": "08:00",
                "hora_fin": "10:00"
            },
            "aulas": self.aulas,
            "asignaturas": self.asignaturas,
            "recursos": self.recursos
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_validar_bloque_individual_con_recursos_insuficientes(self):
        """
        Validación individual: nuevo bloque con aula que no tiene recursos suficientes.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "aula_id": "AU001",  # Aula 101 tiene ["R001", "R002"]
                "asignatura_id": "A003",  # Estructura de Datos requiere ["R001", "R003"]
                "dia": "lunes",
                "hora_inicio": "08:00",
                "hora_fin": "10:00"
            },
            "aulas": self.aulas,
            "asignaturas": self.asignaturas,
            "recursos": self.recursos
        }
        result = self.handler.validate(context)
        print(f"\nValidación individual - recursos insuficientes: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("faltante", result.lower())
        self.assertIn("PCs", result)  # R003 es Computador

    def test_validar_bloque_individual_aula_no_encontrada(self):
        """
        Validación individual: aula no encontrada.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "aula_id": "AU999",  # Aula inexistente
                "asignatura_id": "A001",
                "dia": "lunes",
                "hora_inicio": "08:00",
                "hora_fin": "10:00"
            },
            "aulas": self.aulas,
            "asignaturas": self.asignaturas,
            "recursos": self.recursos
        }
        result = self.handler.validate(context)
        self.assertIsInstance(result, str)
        self.assertIn("No se encontró el aula", result)

    def test_validar_bloque_individual_asignatura_no_encontrada(self):
        """
        Validación individual: asignatura no encontrada.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "aula_id": "AU001",
                "asignatura_id": "A999",  # Asignatura inexistente
                "dia": "lunes",
                "hora_inicio": "08:00",
                "hora_fin": "10:00"
            },
            "aulas": self.aulas,
            "asignaturas": self.asignaturas,
            "recursos": self.recursos
        }
        result = self.handler.validate(context)
        self.assertIsInstance(result, str)
        self.assertIn("No se encontró la asignatura", result)

    # ========== TESTS DE VALIDACIÓN GLOBAL (Enfoque 2) ==========

    def test_validar_horarios_globales_todos_validos(self):
        """
        Validación global: todos los horarios tienen recursos suficientes.
        """
        # Obtener la asignatura "Matemáticas"
        asignatura_matematicas = next(a for a in self.asignaturas if a["id"] == "A001")
        # Asegurarse de que "Matemáticas" solo requiera "R001"
        asignatura_matematicas["requiereRecursos"] = ["R001"]

        context = {
            "schedules": [
                {
                    "id": "H1",
                    "aula_id": "AU002",  # Lab Computo 1 tiene ["R003"]
                    "asignatura_id": "A002",  # Programación requiere ["R003"]
                    "dia": "lunes",
                    "hora_inicio": "08:00",
                    "hora_fin": "10:00"
                },
                {
                    "id": "H2",
                    "aula_id": "AU001",  # Aula 101 tiene ["R001", "R002"]
                    "asignatura_id": "A001",  # Matemáticas requiere ["R001"]
                    "dia": "martes",
                    "hora_inicio": "10:00",
                    "hora_fin": "12:00"
                }
            ],
            "aulas": self.aulas,
            "asignaturas": self.asignaturas,
            "recursos": self.recursos
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    # ========== TESTS DE MÉTODOS AUXILIARES ==========

    def test_obtener_aulas_con_recursos_suficientes(self):
        """
        Test del método auxiliar para obtener aulas compatibles.
        """
        context = {
            "asignatura_id": "A002",  # Programación requiere ["R003"]
            "todas_aulas": self.aulas,
            "asignaturas": self.asignaturas,
            "recursos": self.recursos
        }
        aulas_compatibles = self.handler.obtener_aulas_con_recursos_suficientes(context)
        print(f"\nAulas compatibles con Programación: {aulas_compatibles}")
        self.assertIsInstance(aulas_compatibles, list)
        self.assertIn("AU002", aulas_compatibles)  # Lab Computo 1 tiene R003

    def test_obtener_recursos_faltantes_por_aula(self):
        """
        Test del método auxiliar para obtener recursos faltantes por aula.
        """
        context = {
            "asignatura_id": "A003",  # Estructura de Datos requiere ["R001", "R003"]
            "todas_aulas": self.aulas,
            "asignaturas": self.asignaturas,
            "recursos": self.recursos
        }
        recursos_faltantes = self.handler.obtener_recursos_faltantes_por_aula(context)
        print(f"\nRecursos faltantes por aula para Estructura de Datos: {recursos_faltantes}")
        self.assertIsInstance(recursos_faltantes, dict)
        # AU001 (Aula 101) debería tener faltante "Computador" (R003)
        if "AU001" in recursos_faltantes:
            self.assertIn("PCs", recursos_faltantes["AU001"])

    def test_es_aula_compatible_con_asignatura(self):
        """
        Test del método auxiliar para verificar compatibilidad específica.
        """
        context = {
            "aulas": self.aulas,
            "asignaturas": self.asignaturas,
            "recursos": self.recursos
        }

        # AU002 (Lab Computo 1) debería ser compatible con A002 (Programación)
        es_compatible = self.handler.es_aula_compatible_con_asignatura("AU002", "A002", context)
        self.assertTrue(es_compatible)

        # AU001 (Aula 101) NO debería ser compatible con A003 (Estructura de Datos)
        es_compatible = self.handler.es_aula_compatible_con_asignatura("AU001", "A003", context)
        self.assertFalse(es_compatible)

    def test_bloque_individual_sin_datos_requeridos(self):
        """
        Validación individual: nuevo bloque sin aula_id o asignatura_id.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "dia": "lunes",
                "hora_inicio": "08:00",
                "hora_fin": "10:00"
                # Faltan aula_id y asignatura_id
            },
            "aulas": self.aulas,
            "asignaturas": self.asignaturas,
            "recursos": self.recursos
        }
        result = self.handler.validate(context)
        self.assertIsInstance(result, str)
        self.assertIn("aula_id y asignatura_id", result)

if __name__ == '__main__':
    unittest.main()