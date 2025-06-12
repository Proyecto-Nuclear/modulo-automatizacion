import os
import unittest
import json

from src.core.schedules.selector_factory import get_horario_factory, SelectorFactory

def load_json(filename):
    """Helper para cargar archivos JSON desde el directorio de datos."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, '../../../data'))
    with open(os.path.join(data_dir, filename), encoding="utf-8") as f:
        return json.load(f)

class FactoryMethodTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Carga los datos de prueba una sola vez para toda la clase."""
        try:
            cls.asignaturas = load_json("asignaturas.json")
            cls.aulas = load_json("aulas.json")
            cls.docentes = load_json("docentes.json")
            cls.sedes = load_json("sedes.json")
        except FileNotFoundError as e:
            print(f"Advertencia: No se pudo cargar archivo JSON: {e}")
            # Datos de fallback para pruebas
            cls.asignaturas = [{"id": "ASG001", "nombre": "Álgebra Lineal", "estado": "activo"}]
            cls.aulas = [{"id": "AU001", "nombre": "Aula 101", "tipo": "aula", "estado": "activo"}]
            cls.docentes = [{"id": "DOC001", "nombre": "Laura", "apellido": "García", "estado": "activo"}]
            cls.sedes = [{"id": "SEDE001", "nombre": "Campus Principal", "estado": "activo"}]

        # Datos específicos para laboratorios
        cls.aula_laboratorio = {"id": "LAB001", "nombre": "Lab Sistemas", "tipo": "laboratorio", "estado": "activo"}

    def setUp(self):
        """Configuración común para cada test."""
        self.kwargs_base = {
            "docente": self.docentes[0],
            "aula": self.aulas[0],
            "asignatura": self.asignaturas[0],
            "start_time": "08:00",
            "end_time": "10:00",
            "dia": "Lunes",
            "sede": self.sedes[0],
            "id": "H001"
        }

    # ========== TESTS DE CREACIÓN EXITOSA ==========

    def test_factory_clase_normal_exitosa(self):
        """Test de creación exitosa de clase normal."""
        factory = get_horario_factory("normal")
        self.assertIsNotNone(factory, "Factory para 'normal' no debe ser None")

        horario, error = factory.crear_horario_con_validacion(**self.kwargs_base)

        print(f"\nClase Normal: {horario.description()}")
        self.assertIsNone(error, f"No debe haber error: {error}")
        self.assertIsNotNone(horario, "Horario no debe ser None")
        self.assertEqual(horario.get_tipo(), "normal")
        self.assertIn("Álgebra Lineal", horario.description())
        self.assertIn("Aula 101", horario.description())
        self.assertIn("Laura", horario.description())

    def test_factory_laboratorio_exitoso(self):
        """Test de creación exitosa de laboratorio."""
        kwargs = self.kwargs_base.copy()
        kwargs["aula"] = self.aula_laboratorio

        factory = get_horario_factory("laboratorio")
        self.assertIsNotNone(factory, "Factory para 'laboratorio' no debe ser None")

        horario, error = factory.crear_horario_con_validacion(**kwargs)

        print(f"\nLaboratorio: {horario.description()}")
        self.assertIsNone(error, f"No debe haber error: {error}")
        self.assertIsNotNone(horario, "Horario no debe ser None")
        self.assertEqual(horario.get_tipo(), "laboratorio")
        self.assertIn("Laboratorio de", horario.description())
        self.assertIn("Lab Sistemas", horario.description())

    def test_factory_virtual_exitosa(self):
        """Test de creación exitosa de clase virtual."""
        kwargs = self.kwargs_base.copy()
        # Las clases virtuales NO deben tener aula
        kwargs["aula"] = {}
        kwargs["plataforma"] = "Teams"
        kwargs["enlace"] = "https://teams.microsoft.com/..."

        factory = get_horario_factory("virtual")
        self.assertIsNotNone(factory, "Factory para 'virtual' no debe ser None")

        horario, error = factory.crear_horario_con_validacion(**kwargs)

        print(f"\nClase Virtual: {horario.description()}")
        self.assertIsNone(error, f"No debe haber error: {error}")
        self.assertIsNotNone(horario, "Horario no debe ser None")
        self.assertEqual(horario.get_tipo(), "virtual")
        self.assertIn("Clase virtual", horario.description())
        self.assertIn("Teams", horario.description())

    def test_factory_bloqueo_exitoso(self):
        """Test de creación exitosa de bloqueo."""
        kwargs = {
            "aula": self.aulas[0],
            "start_time": "12:00",
            "end_time": "13:00",
            "dia": "Lunes",
            "sede": self.sedes[0],
            "motivo": "Mantenimiento programado",
            "tipo_bloqueo": "mantenimiento"
        }

        factory = get_horario_factory("bloqueo")
        self.assertIsNotNone(factory, "Factory para 'bloqueo' no debe ser None")

        horario, error = factory.crear_horario_con_validacion(**kwargs)

        print(f"\nBloqueo: {horario.description()}")
        self.assertIsNone(error, f"No debe haber error: {error}")
        self.assertIsNotNone(horario, "Horario no debe ser None")
        self.assertEqual(horario.get_tipo(), "bloqueo")
        self.assertIn("Bloqueo", horario.description())
        self.assertIn("Mantenimiento", horario.description())

    # ========== TESTS DE VALIDACIÓN Y ERRORES ==========

    def test_factory_clase_normal_sin_docente(self):
        """Test de validación: clase normal sin docente."""
        kwargs = self.kwargs_base.copy()
        kwargs["docente"] = {}

        factory = get_horario_factory("normal")
        horario, error = factory.crear_horario_con_validacion(**kwargs)

        print(f"\nError clase normal sin docente: {error}")
        self.assertIsNone(horario, "Horario debe ser None cuando hay error")
        self.assertIsNotNone(error, "Debe haber mensaje de error")
        self.assertIn("docente", error.lower())

    def test_factory_laboratorio_aula_incorrecta(self):
        """Test de validación: laboratorio con aula que no es laboratorio."""
        kwargs = self.kwargs_base.copy()
        # Usar aula normal en lugar de laboratorio

        factory = get_horario_factory("laboratorio")
        error_validacion = factory.validar_parametros_basicos(**kwargs)

        print(f"\nError laboratorio con aula incorrecta: {error_validacion}")
        self.assertIsNotNone(error_validacion, "Debe haber error de validación")
        self.assertIn("laboratorio", error_validacion.lower())

    def test_factory_virtual_con_aula(self):
        """Test de validación: clase virtual con aula asignada."""
        kwargs = self.kwargs_base.copy()
        # Las clases virtuales NO deben tener aula

        factory = get_horario_factory("virtual")
        error_validacion = factory.validar_parametros_basicos(**kwargs)

        print(f"\nError clase virtual con aula: {error_validacion}")
        self.assertIsNotNone(error_validacion, "Debe haber error de validación")
        self.assertIn("aula", error_validacion.lower())

    def test_factory_bloqueo_con_docente(self):
        """Test de validación: bloqueo con docente asignado."""
        kwargs = self.kwargs_base.copy()
        # Los bloqueos NO deben tener docente

        factory = get_horario_factory("bloqueo")
        error_validacion = factory.validar_parametros_basicos(**kwargs)

        print(f"\nError bloqueo con docente: {error_validacion}")
        self.assertIsNotNone(error_validacion, "Debe haber error de validación")
        self.assertIn("docente", error_validacion.lower())

    def test_parametros_faltantes(self):
        """Test de validación: parámetros básicos faltantes."""
        kwargs_incompletos = {
            "docente": self.docentes[0],
            "aula": self.aulas[0]
            # Faltan start_time, end_time, dia
        }

        factory = get_horario_factory("normal")
        horario, error = factory.crear_horario_con_validacion(**kwargs_incompletos)

        print(f"\nError parámetros faltantes: {error}")
        self.assertIsNone(horario, "Horario debe ser None cuando hay error")
        self.assertIsNotNone(error, "Debe haber mensaje de error")
        self.assertIn("faltantes", error.lower())

    # ========== TESTS DEL SELECTOR FACTORY ==========

    def test_selector_factory_tipos_validos(self):
        """Test de tipos válidos en SelectorFactory."""
        tipos_validos = ["normal", "laboratorio", "virtual", "bloqueo"]

        for tipo in tipos_validos:
            with self.subTest(tipo=tipo):
                factory = SelectorFactory.get_horario_factory(tipo)
                self.assertIsNotNone(factory, f"Factory para '{tipo}' no debe ser None")

    def test_selector_factory_aliases(self):
        """Test de aliases en SelectorFactory."""
        aliases = {
            "clase_normal": "normal",
            "presencial": "normal",
            "lab": "laboratorio",
            "online": "virtual",
            "remoto": "virtual",
            "bloqueado": "bloqueo",
            "mantenimiento": "bloqueo"
        }

        for alias, tipo_esperado in aliases.items():
            with self.subTest(alias=alias):
                factory = SelectorFactory.get_horario_factory(alias)
                self.assertIsNotNone(factory, f"Factory para alias '{alias}' no debe ser None")

    def test_selector_factory_tipo_invalido(self):
        """Test de tipo inválido en SelectorFactory."""
        factory = SelectorFactory.get_horario_factory("tipo_inexistente")
        self.assertIsNone(factory, "Factory para tipo inexistente debe ser None")

    def test_selector_factory_crear_horario_directo(self):
        """Test de creación directa usando SelectorFactory."""
        horario, error = SelectorFactory.crear_horario("normal", **self.kwargs_base)

        print(f"\nCreación directa: {horario.description() if horario else error}")
        self.assertIsNone(error, f"No debe haber error: {error}")
        self.assertIsNotNone(horario, "Horario no debe ser None")
        self.assertEqual(horario.get_tipo(), "normal")

    def test_selector_factory_crear_horario_tipo_invalido(self):
        """Test de creación directa con tipo inválido."""
        horario, error = SelectorFactory.crear_horario("tipo_inexistente", **self.kwargs_base)

        print(f"\nError tipo inválido: {error}")
        self.assertIsNone(horario, "Horario debe ser None para tipo inválido")
        self.assertIsNotNone(error, "Debe haber mensaje de error")
        self.assertIn("no soportado", error)

    def test_get_tipos_disponibles(self):
        """Test de obtener tipos disponibles."""
        tipos = SelectorFactory.get_tipos_disponibles()
        self.assertIsInstance(tipos, list, "Debe retornar una lista")
        self.assertIn("normal", tipos, "Debe incluir 'normal'")
        self.assertIn("laboratorio", tipos, "Debe incluir 'laboratorio'")
        self.assertIn("virtual", tipos, "Debe incluir 'virtual'")
        self.assertIn("bloqueo", tipos, "Debe incluir 'bloqueo'")
        print(f"\nTipos disponibles: {tipos}")

    def test_es_tipo_valido(self):
        """Test de validación de tipos."""
        self.assertTrue(SelectorFactory.es_tipo_valido("normal"))
        self.assertTrue(SelectorFactory.es_tipo_valido("LABORATORIO"))  # Case insensitive
        self.assertTrue(SelectorFactory.es_tipo_valido(" virtual "))  # Con espacios
        self.assertFalse(SelectorFactory.es_tipo_valido("inexistente"))

    # ========== TESTS DE FUNCIONALIDADES ESPECÍFICAS ==========

    def test_horario_to_dict(self):
        """Test de serialización a diccionario."""
        factory = get_horario_factory("normal")
        horario, _ = factory.crear_horario_con_validacion(**self.kwargs_base)

        horario_dict = horario.to_dict()
        print(f"\nHorario serializado: {horario_dict}")

        self.assertIsInstance(horario_dict, dict, "to_dict() debe retornar un diccionario")
        self.assertEqual(horario_dict["tipo"], "normal")
        self.assertEqual(horario_dict["id"], "H001")
        self.assertIn("docente", horario_dict)
        self.assertIn("aula", horario_dict)

    def test_horario_duracion_minutos(self):
        """Test de cálculo de duración."""
        factory = get_horario_factory("normal")
        horario, _ = factory.crear_horario_con_validacion(**self.kwargs_base)

        duracion = horario.get_duracion_minutos()
        print(f"\nDuración calculada: {duracion} minutos")

        self.assertEqual(duracion, 120, "Duración de 08:00 a 10:00 debe ser 120 minutos")

    def test_horario_es_valido(self):
        """Test de validación de horario creado."""
        factory = get_horario_factory("normal")
        horario, _ = factory.crear_horario_con_validacion(**self.kwargs_base)

        es_valido, mensaje = horario.es_valido()
        print(f"\nValidación horario: {es_valido}, mensaje: {mensaje}")

        self.assertTrue(es_valido, f"Horario debe ser válido: {mensaje}")
        self.assertEqual(mensaje, "", "No debe haber mensaje de error")

    # ========== TESTS DE CASOS EDGE ==========

    def test_horario_con_datos_vacios(self):
        """Test con datos vacíos."""
        kwargs_vacios = {
            "docente": {},
            "aula": {},
            "asignatura": {},
            "start_time": "",
            "end_time": "",
            "dia": "",
            "sede": {}
        }

        factory = get_horario_factory("normal")
        horario, error = factory.crear_horario_con_validacion(**kwargs_vacios)

        print(f"\nError con datos vacíos: {error}")
        self.assertIsNone(horario, "Horario debe ser None con datos vacíos")
        self.assertIsNotNone(error, "Debe haber mensaje de error")

    def test_horario_con_horas_invalidas(self):
        """Test con horas inválidas."""
        kwargs = self.kwargs_base.copy()
        kwargs["start_time"] = "10:00"
        kwargs["end_time"] = "08:00"  # Hora fin antes que hora inicio

        factory = get_horario_factory("normal")
        horario, _ = factory.crear_horario_con_validacion(**kwargs)

        if horario:
            es_valido, mensaje = horario.es_valido()
            print(f"\nValidación horas inválidas: {es_valido}, mensaje: {mensaje}")
            self.assertFalse(es_valido, "Horario con horas inválidas no debe ser válido")

    def test_compatibilidad_funcion_original(self):
        """Test de compatibilidad con la función original."""
        # Usar la función original
        factory_original = get_horario_factory("normal")

        # Usar el nuevo SelectorFactory
        factory_nuevo = SelectorFactory.get_horario_factory("normal")

        self.assertEqual(type(factory_original), type(factory_nuevo),
                         "Ambas funciones deben retornar el mismo tipo de factory")

    # ========== TESTS CON DATOS REALES ==========

    def test_con_datos_reales_si_disponibles(self):
        """Test con datos reales de los archivos JSON si están disponibles."""
        if len(self.asignaturas) == 1 and self.asignaturas[0]["id"] == "ASG001":
            self.skipTest("Usando datos de fallback, no datos reales")

        # Usar datos reales
        kwargs_reales = {
            "docente": self.docentes[0],
            "aula": self.aulas[0],
            "asignatura": self.asignaturas[0],
            "start_time": "14:00",
            "end_time": "16:00",
            "dia": "Miércoles",
            "sede": self.sedes[0]
        }

        factory = get_horario_factory("normal")
        horario, error = factory.crear_horario_con_validacion(**kwargs_reales)

        print(f"\nTest con datos reales: {horario.description() if horario else error}")
        self.assertIsNone(error, f"No debe haber error con datos reales: {error}")
        self.assertIsNotNone(horario, "Horario no debe ser None con datos reales")

if __name__ == '__main__':
    # Configurar el runner para mostrar más detalles
    unittest.main(verbosity=2)