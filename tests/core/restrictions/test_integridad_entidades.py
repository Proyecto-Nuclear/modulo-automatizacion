import unittest
import json
import os

from src.core.restrictions.integridad.integridad_entidades_handler import IntegridadEntidadesHandler

def load_json(filename):
    """Helper to load JSON from the data directory."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, '../../../data'))
    with open(os.path.join(data_dir, filename), encoding="utf-8") as f:
        return json.load(f)

class IntegridadEntidadesHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.handler = IntegridadEntidadesHandler()

        # Cargar datos de prueba si están disponibles
        try:
            self.aulas = load_json("aulas.json")
            self.docentes = load_json("docentes.json")
            self.asignaturas = load_json("asignaturas.json")
            self.sedes = load_json("sedes.json")
        except FileNotFoundError:
            # Datos de fallback si no existen los archivos JSON
            self.aulas = []
            self.docentes = []
            self.asignaturas = []
            self.sedes = []

        # Contexto válido para pruebas
        self.valid_context = {
            "aula": {"id": "AU001", "estado": "activo", "nombre": "Aula 101"},
            "docente": {"id": "DOC001", "estado": "activo", "nombre": "Juan", "apellido": "Pérez"},
            "asignatura": {"id": "ASG001", "estado": "activo", "nombre": "Matemáticas"},
            "sede": {"id": "SEDE001", "estado": "activo", "nombre": "Campus Principal"}
        }

    # ========== TESTS DE VALIDACIÓN INDIVIDUAL ==========

    def test_todas_entidades_activas_individual(self):
        """
        Validación individual: todas las entidades están activas.
        Debe retornar None (válido).
        """
        result = self.handler.validate(self.valid_context)
        self.assertIsNone(result, "Debe retornar None si todas las entidades están activas")

    def test_aula_inactiva_individual(self):
        """
        Validación individual: aula inactiva.
        Debe retornar mensaje de error.
        """
        context = self.valid_context.copy()
        context["aula"] = {"id": "AU001", "estado": "inactivo", "nombre": "Aula 101"}
        result = self.handler.validate(context)
        print(f"\nValidación individual - aula inactiva: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("aula", result)
        self.assertIn("no está activa", result)
        self.assertIn("AU001", result)

    def test_docente_inactivo_individual(self):
        """
        Validación individual: docente inactivo.
        Debe retornar mensaje de error.
        """
        context = self.valid_context.copy()
        context["docente"] = {"id": "DOC001", "estado": "INACTIVO", "nombre": "Juan"}
        result = self.handler.validate(context)
        print(f"\nValidación individual - docente inactivo: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("docente", result)
        self.assertIn("no está activa", result)
        self.assertIn("DOC001", result)

    def test_asignatura_inactiva_individual(self):
        """
        Validación individual: asignatura inactiva.
        Debe retornar mensaje de error.
        """
        context = self.valid_context.copy()
        context["asignatura"] = {"id": "ASG001", "estado": "INACTIVO", "nombre": "Matemáticas"}
        result = self.handler.validate(context)
        print(f"\nValidación individual - asignatura inactiva: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("asignatura", result)
        self.assertIn("no está activa", result)
        self.assertIn("ASG001", result)

    def test_sede_inactiva_individual(self):
        """
        Validación individual: sede inactiva.
        Debe retornar mensaje de error.
        """
        context = self.valid_context.copy()
        context["sede"] = {"id": "SEDE001", "estado": "inactivo", "nombre": "Campus Principal"}
        result = self.handler.validate(context)
        print(f"\nValidación individual - sede inactiva: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("sede", result)
        self.assertIn("no está activa", result)
        self.assertIn("SEDE001", result)

    def test_entidad_faltante_individual(self):
        """
        Validación individual: entidad faltante (docente).
        Debe retornar mensaje de error.
        """
        context = self.valid_context.copy()
        del context["docente"]
        result = self.handler.validate(context)
        print(f"\nValidación individual - entidad faltante: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("docente", result)
        self.assertIn("no está definida", result)

    def test_multiples_entidades_faltantes_individual(self):
        """
        Validación individual: múltiples entidades faltantes.
        Debe retornar mensaje de error por la primera encontrada.
        """
        context = {
            "aula": {"id": "AU001", "estado": "activo"},
            "sede": {"id": "SEDE001", "estado": "activo"}
            # Faltan docente y asignatura
        }
        result = self.handler.validate(context)
        print(f"\nValidación individual - múltiples faltantes: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("no está definida", result)

    def test_entidad_sin_estado_individual(self):
        """
        Validación individual: entidad sin campo 'estado'.
        Debe retornar mensaje de error.
        """
        context = self.valid_context.copy()
        context["aula"] = {"id": "AU001", "nombre": "Aula 101"}  # Sin campo 'estado'
        result = self.handler.validate(context)
        print(f"\nValidación individual - sin estado: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("aula", result)
        self.assertIn("no está activa", result)

    def test_entidad_estado_vacio_individual(self):
        """
        Validación individual: entidad con estado vacío.
        Debe retornar mensaje de error.
        """
        context = self.valid_context.copy()
        context["docente"] = {"id": "DOC001", "estado": "", "nombre": "Juan"}
        result = self.handler.validate(context)
        print(f"\nValidación individual - estado vacío: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("docente", result)
        self.assertIn("no está activa", result)

    # ========== TESTS DE VALIDACIÓN GLOBAL ==========

    def test_validacion_global_todas_activas(self):
        """
        Validación global: todas las asignaciones tienen entidades activas.
        Debe retornar None (válido).
        """
        context = {
            "schedules": [
                {
                    "id": "H1",
                    "aula": {"id": "AU001", "estado": "activo"},
                    "docente": {"id": "DOC001", "estado": "activo"},
                    "asignatura": {"id": "ASG001", "estado": "activo"},
                    "sede": {"id": "SEDE001", "estado": "activo"}
                },
                {
                    "id": "H2",
                    "aula": {"id": "AU002", "estado": "activo"},
                    "docente": {"id": "DOC002", "estado": "activo"},
                    "asignatura": {"id": "ASG002", "estado": "activo"},
                    "sede": {"id": "SEDE001", "estado": "activo"}
                }
            ]
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_validacion_global_con_entidades_inactivas(self):
        """
        Validación global: algunas asignaciones tienen entidades inactivas.
        Debe retornar mensaje de error con todos los problemas.
        """
        context = {
            "schedules": [
                {
                    "id": "H1",
                    "aula": {"id": "AU001", "estado": "inactivo"},  # Inactiva
                    "docente": {"id": "DOC001", "estado": "activo"},
                    "asignatura": {"id": "ASG001", "estado": "activo"},
                    "sede": {"id": "SEDE001", "estado": "activo"}
                },
                {
                    "id": "H2",
                    "aula": {"id": "AU002", "estado": "activo"},
                    "docente": {"id": "DOC002", "estado": "inactivo"},  # Inactivo
                    "asignatura": {"id": "ASG002", "estado": "activo"},
                    "sede": {"id": "SEDE001", "estado": "activo"}
                }
            ]
        }
        result = self.handler.validate(context)
        print(f"\nValidación global - con inactivas: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("H1", result)  # Debería mencionar la asignación H1
        self.assertIn("H2", result)  # Debería mencionar la asignación H2
        self.assertIn("AU001", result)  # Debería mencionar el aula inactiva
        self.assertIn("DOC002", result)  # Debería mencionar el docente inactivo

    def test_validacion_global_con_entidades_faltantes(self):
        """
        Validación global: algunas asignaciones tienen entidades faltantes.
        Debe retornar mensaje de error.
        """
        context = {
            "schedules": [
                {
                    "id": "H1",
                    "aula": {"id": "AU001", "estado": "activo"},
                    "docente": {"id": "DOC001", "estado": "activo"},
                    "asignatura": {"id": "ASG001", "estado": "activo"}
                    # Falta sede
                },
                {
                    "id": "H2",
                    "aula": {"id": "AU002", "estado": "activo"},
                    "asignatura": {"id": "ASG002", "estado": "activo"},
                    "sede": {"id": "SEDE001", "estado": "activo"}
                    # Falta docente
                }
            ]
        }
        result = self.handler.validate(context)
        print(f"\nValidación global - con faltantes: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("H1", result)
        self.assertIn("H2", result)
        self.assertIn("sede", result)
        self.assertIn("docente", result)

    def test_validacion_global_lista_vacia(self):
        """
        Validación global: lista de asignaciones vacía.
        Debe retornar None (válido).
        """
        context = {"schedules": []}
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_validacion_global_compatibilidad_schedule(self):
        """
        Validación global: usando 'schedule' en lugar de 'schedules' (compatibilidad).
        Debe funcionar correctamente.
        """
        context = {
            "schedule": [
                {
                    "id": "H1",
                    "aula": {"id": "AU001", "estado": "activo"},
                    "docente": {"id": "DOC001", "estado": "activo"},
                    "asignatura": {"id": "ASG001", "estado": "activo"},
                    "sede": {"id": "SEDE001", "estado": "activo"}
                }
            ]
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    # ========== TESTS DE CASOS EDGE ==========

    def test_estado_case_insensitive(self):
        """
        Test de que la validación de estado sea case-insensitive.
        """
        context = self.valid_context.copy()
        context["aula"] = {"id": "AU001", "estado": "ACTIVO"}  # Mayúsculas
        context["docente"] = {"id": "DOC001", "estado": "Activo"}  # Capitalizado
        context["asignatura"] = {"id": "ASG001", "estado": "activo"}  # Minúsculas
        context["sede"] = {"id": "SEDE001", "estado": "AcTiVo"}  # Mixto

        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_entidades_vacias(self):
        """
        Test con entidades como diccionarios vacíos.
        """
        context = {
            "aula": {},
            "docente": {},
            "asignatura": {},
            "sede": {}
        }
        result = self.handler.validate(context)
        print(f"\nValidación - entidades vacías: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("no está definida", result)

    def test_entidades_none(self):
        """
        Test con entidades como None.
        """
        context = {
            "aula": None,
            "docente": None,
            "asignatura": None,
            "sede": None
        }
        result = self.handler.validate(context)
        print(f"\nValidación - entidades None: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("no está definida", result)

    # ========== TESTS CON DATOS REALES (si están disponibles) ==========

    def test_con_datos_reales_si_disponibles(self):
        """
        Test con datos reales de los archivos JSON si están disponibles.
        """
        if not (self.aulas and self.docentes and self.asignaturas and self.sedes):
            self.skipTest("Archivos JSON no disponibles para este test")

        # Usar la primera entidad de cada tipo si está activa
        aula_activa = next((a for a in self.aulas if a.get("estado", "").lower() == "activo"), None)
        docente_activo = next((d for d in self.docentes if d.get("estado", "").lower() == "activo"), None)
        asignatura_activa = next((a for a in self.asignaturas if a.get("estado", "").lower() == "activo"), None)
        sede_activa = next((s for s in self.sedes if s.get("estado", "").lower() == "activo"), None)

        if all([aula_activa, docente_activo, asignatura_activa, sede_activa]):
            context = {
                "aula": aula_activa,
                "docente": docente_activo,
                "asignatura": asignatura_activa,
                "sede": sede_activa
            }
            result = self.handler.validate(context)
            print(f"\nTest con datos reales: {result}")
            self.assertIsNone(result)
        else:
            self.skipTest("No se encontraron suficientes entidades activas en los datos reales")

if __name__ == '__main__':
    unittest.main()