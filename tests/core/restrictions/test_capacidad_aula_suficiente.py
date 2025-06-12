import unittest
import json
import os

from src.core.restrictions.aulas.capacidad_aula_suficiente_handler import CapacidadAulaSuficienteHandler

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

    # ========== TESTS DE VALIDACIÓN DIRECTA (Compatibilidad con versión anterior) ==========

    def test_aula_con_capacidad_suficiente_directo(self):
        """
        El aula tiene suficiente capacidad para la cantidad de estudiantes (validación directa).
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
        self.assertIsNone(result)

    def test_aula_con_capacidad_exacta_directo(self):
        """
        El aula tiene exactamente la capacidad requerida por la cantidad de estudiantes (validación directa).
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
        self.assertIsNone(result)

    def test_aula_con_capacidad_insuficiente_directo(self):
        """
        El aula NO tiene capacidad suficiente para la cantidad de estudiantes (validación directa).
        Debe retornar un mensaje de error y recomendar aulas con capacidad suficiente.
        """
        asignatura = next(a for a in self.asignaturas if a["id"] == "A001")
        aula = next(a for a in self.aulas if a["id"] == "AU004")  # Aula 201, capacidad 35
        context = {
            "aula": aula,
            "numero_estudiantes": 40,
            "asignatura": asignatura,
            "aulas": self.aulas
        }
        result = self.handler.validate(context)
        print(f"\nValidación directa - capacidad insuficiente: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("capacidad", result.lower())
        self.assertIn("Aula 201", result)
        self.assertIn("Álgebra Lineal", result)
        self.assertIn("40", result)
        self.assertIn("Aula 101", result)  # Recomendación

    def test_falta_numero_estudiantes_directo(self):
        """
        Si no se proporciona el número de estudiantes, debe retornar un mensaje de error (validación directa).
        """
        asignatura = next(a for a in self.asignaturas if a["id"] == "A003")
        aula = next(a for a in self.aulas if a["id"] == "AU001")
        context = {
            "aula": aula,
            "asignatura": asignatura,
            "aulas": self.aulas
        }
        result = self.handler.validate(context)
        print(f"\nValidación directa - falta número de estudiantes: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("no se proporcionó", result.lower())

    # ========== TESTS DE VALIDACIÓN INDIVIDUAL (Enfoque 2) ==========

    def test_validar_bloque_individual_con_capacidad_suficiente(self):
        """
        Validación individual: nuevo bloque con aula que tiene capacidad suficiente.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "aula_id": "AU001",  # Aula 101, capacidad 40
                "asignatura_id": "A003",
                "numero_estudiantes": 30,
                "dia": "lunes",
                "hora_inicio": "08:00",
                "hora_fin": "10:00"
            },
            "aulas": self.aulas,
            "asignaturas": self.asignaturas
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_validar_bloque_individual_con_capacidad_insuficiente(self):
        """
        Validación individual: nuevo bloque con aula que no tiene capacidad suficiente.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "aula_id": "AU004",  # Aula 201, capacidad 35
                "asignatura_id": "A001",
                "numero_estudiantes": 40,
                "dia": "lunes",
                "hora_inicio": "08:00",
                "hora_fin": "10:00"
            },
            "aulas": self.aulas,
            "asignaturas": self.asignaturas
        }
        result = self.handler.validate(context)
        print(f"\nValidación individual - capacidad insuficiente: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("capacidad", result.lower())
        self.assertIn("Aula 201", result)
        self.assertIn("40", result)
        self.assertIn("Aula 101", result)  # Recomendación

    def test_validar_bloque_individual_aula_no_encontrada(self):
        """
        Validación individual: aula no encontrada.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "aula_id": "AU999",  # Aula inexistente
                "asignatura_id": "A001",
                "numero_estudiantes": 30,
                "dia": "lunes",
                "hora_inicio": "08:00",
                "hora_fin": "10:00"
            },
            "aulas": self.aulas,
            "asignaturas": self.asignaturas
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
                "numero_estudiantes": 30,
                "dia": "lunes",
                "hora_inicio": "08:00",
                "hora_fin": "10:00"
            },
            "aulas": self.aulas,
            "asignaturas": self.asignaturas
        }
        result = self.handler.validate(context)
        self.assertIsInstance(result, str)
        self.assertIn("No se encontró la asignatura", result)

    def test_validar_bloque_individual_sin_datos_requeridos(self):
        """
        Validación individual: nuevo bloque sin aula_id, asignatura_id o numero_estudiantes.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "dia": "lunes",
                "hora_inicio": "08:00",
                "hora_fin": "10:00"
                # Faltan aula_id, asignatura_id y numero_estudiantes
            },
            "aulas": self.aulas,
            "asignaturas": self.asignaturas
        }
        result = self.handler.validate(context)
        self.assertIsInstance(result, str)
        self.assertIn("aula_id, asignatura_id y numero_estudiantes", result)

    # ========== TESTS DE VALIDACIÓN GLOBAL (Enfoque 2) ==========

    def test_validar_horarios_globales_todos_validos(self):
        """
        Validación global: todos los horarios tienen capacidad suficiente.
        """
        context = {
            "schedules": [
                {
                    "id": "H1",
                    "aula_id": "AU001",  # Aula 101, capacidad 40
                    "asignatura_id": "A003",
                    "numero_estudiantes": 30,
                    "dia": "lunes",
                    "hora_inicio": "08:00",
                    "hora_fin": "10:00"
                },
                {
                    "id": "H2",
                    "aula_id": "AU002",  # Lab Computo 1, capacidad 25
                    "asignatura_id": "A002",
                    "numero_estudiantes": 20,
                    "dia": "martes",
                    "hora_inicio": "10:00",
                    "hora_fin": "12:00"
                }
            ],
            "aulas": self.aulas,
            "asignaturas": self.asignaturas
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_validar_horarios_globales_con_error(self):
        """
        Validación global: uno de los horarios no tiene capacidad suficiente.
        """
        context = {
            "schedules": [
                {
                    "id": "H1",
                    "aula_id": "AU001",  # Aula 101, capacidad 40
                    "asignatura_id": "A003",
                    "numero_estudiantes": 30,
                    "dia": "lunes",
                    "hora_inicio": "08:00",
                    "hora_fin": "10:00"
                },
                {
                    "id": "H2",
                    "aula_id": "AU004",  # Aula 201, capacidad 35
                    "asignatura_id": "A001",
                    "numero_estudiantes": 40,
                    "dia": "martes",
                    "hora_inicio": "10:00",
                    "hora_fin": "12:00"
                }
            ],
            "aulas": self.aulas,
            "asignaturas": self.asignaturas
        }
        result = self.handler.validate(context)
        print(f"\nValidación global - con error: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("capacidad", result.lower())
        self.assertIn("Aula 201", result)
        self.assertIn("40", result)
        self.assertIn("Aula 101", result)  # Recomendación
        self.assertIn("martes 10:00-12:00", result)  # Info del horario

    # ========== TESTS DE MÉTODOS AUXILIARES ==========

    def test_obtener_aulas_con_capacidad_suficiente(self):
        """
        Test del método auxiliar para obtener aulas con capacidad suficiente.
        """
        context = {
            "numero_estudiantes": 30,
            "todas_aulas": self.aulas
        }
        aulas_compatibles = self.handler.obtener_aulas_con_capacidad_suficiente(context)
        print(f"\nAulas compatibles con 30 estudiantes: {aulas_compatibles}")
        self.assertIsInstance(aulas_compatibles, list)
        self.assertIn("AU001", aulas_compatibles)  # Aula 101 tiene capacidad 40
        self.assertIn("AU003", aulas_compatibles)  # Aula 201 tiene capacidad 35

    def test_es_aula_compatible_con_capacidad(self):
        """
        Test del método auxiliar para verificar compatibilidad específica.
        """
        context = {
            "aulas": self.aulas
        }
        # Aula 101 (capacidad 40) debería ser compatible con 30 estudiantes
        es_compatible = self.handler.es_aula_compatible_con_capacidad("AU001", 30, context)
        self.assertTrue(es_compatible)

        # Aula 201 (capacidad 35) NO debería ser compatible con 40 estudiantes
        es_compatible = self.handler.es_aula_compatible_con_capacidad("AU004", 40, context)
        self.assertFalse(es_compatible)

if __name__ == '__main__':
    unittest.main()