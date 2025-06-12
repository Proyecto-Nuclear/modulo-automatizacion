import unittest
from unittest.mock import Mock

from src.core.schedules.builders.horario_builder_base import HorarioBuilderBase
from test_builder_base_helper import BuilderTestData


class ConcreteBuilderForTesting(HorarioBuilderBase):
    """Builder concreto para testing de la clase base."""

    def build(self):
        return Mock()

    def get_tipo(self):
        return 'test'


class HorarioBuilderBaseTestCase(unittest.TestCase):

    def setUp(self):
        """Configuración común para cada test."""
        self.builder = ConcreteBuilderForTesting()
        self.test_data = BuilderTestData.get_valid_horario_data()

    def test_reset_builder(self):
        """Test que el reset limpia todos los campos."""
        # Configurar algunos datos
        self.builder.set_docente(self.test_data['docente'])
        self.builder.set_aula(self.test_data['aula'])

        # Reset
        result = self.builder.reset()

        # Verificar que se limpiaron los campos
        self.assertIsNone(self.builder._docente)
        self.assertIsNone(self.builder._aula)
        self.assertEqual(self.builder._metadatos, {})

        # Verificar method chaining
        self.assertEqual(result, self.builder)

    def test_set_docente_valido(self):
        """Test establecer docente válido."""
        docente = self.test_data['docente']
        result = self.builder.set_docente(docente)

        self.assertEqual(self.builder._docente, docente)
        self.assertEqual(result, self.builder)  # Method chaining

    def test_set_docente_invalido(self):
        """Test establecer docente inválido."""
        # Docente no es diccionario
        with self.assertRaises(ValueError) as context:
            self.builder.set_docente("no es diccionario")
        self.assertIn("debe ser un diccionario", str(context.exception))

        # Docente sin campos requeridos
        with self.assertRaises(ValueError) as context:
            self.builder.set_docente({"nombre": "Juan"})  # Falta 'id'
        self.assertIn("debe tener los campos", str(context.exception))

    def test_set_aula_valida(self):
        """Test establecer aula válida."""
        aula = self.test_data['aula']
        result = self.builder.set_aula(aula)

        self.assertEqual(self.builder._aula, aula)
        self.assertEqual(result, self.builder)

    def test_set_aula_invalida(self):
        """Test establecer aula inválida."""
        with self.assertRaises(ValueError):
            self.builder.set_aula("no es diccionario")

        with self.assertRaises(ValueError):
            self.builder.set_aula({"nombre": "Aula 1"})  # Falta 'id'

    def test_set_asignatura_valida(self):
        """Test establecer asignatura válida."""
        asignatura = self.test_data['asignatura']
        result = self.builder.set_asignatura(asignatura)

        self.assertEqual(self.builder._asignatura, asignatura)
        self.assertEqual(result, self.builder)

    def test_set_tiempo_valido(self):
        """Test establecer tiempos válidos."""
        result = self.builder.set_tiempo("08:00", "10:00")

        self.assertEqual(self.builder._start_time, "08:00")
        self.assertEqual(self.builder._end_time, "10:00")
        self.assertEqual(result, self.builder)

    def test_set_tiempo_invalido(self):
        """Test establecer tiempos inválidos."""
        # Formato inválido
        with self.assertRaises(ValueError) as context:
            self.builder.set_tiempo("8:00", "10:00")  # Sin cero inicial
        self.assertIn("Formato de hora", str(context.exception))

        # Hora de inicio posterior a hora de fin
        with self.assertRaises(ValueError) as context:
            self.builder.set_tiempo("10:00", "08:00")
        self.assertIn("debe ser anterior", str(context.exception))

        # Horas iguales
        with self.assertRaises(ValueError) as context:
            self.builder.set_tiempo("10:00", "10:00")
        self.assertIn("debe ser anterior", str(context.exception))

    def test_set_dia_valido(self):
        """Test establecer día válido."""
        result = self.builder.set_dia("Lunes")

        self.assertEqual(self.builder._dia, "Lunes")
        self.assertEqual(result, self.builder)

    def test_set_dia_invalido(self):
        """Test establecer día inválido."""
        with self.assertRaises(ValueError) as context:
            self.builder.set_dia("Lunez")  # Día inválido
        self.assertIn("Día inválido", str(context.exception))

    def test_set_sede_valida(self):
        """Test establecer sede válida."""
        sede = self.test_data['sede']
        result = self.builder.set_sede(sede)

        self.assertEqual(self.builder._sede, sede)
        self.assertEqual(result, self.builder)

    def test_set_id_valido(self):
        """Test establecer ID válido."""
        result = self.builder.set_id("H001")

        self.assertEqual(self.builder._id, "H001")
        self.assertEqual(result, self.builder)

    def test_set_id_invalido(self):
        """Test establecer ID inválido."""
        with self.assertRaises(ValueError):
            self.builder.set_id("")  # ID vacío

        with self.assertRaises(ValueError):
            self.builder.set_id(None)  # ID None

    def test_set_metadatos(self):
        """Test establecer metadatos."""
        metadatos = {"estado": "confirmado", "observaciones": "Test"}
        result = self.builder.set_metadatos(**metadatos)

        self.assertIn("estado", self.builder._metadatos)
        self.assertIn("observaciones", self.builder._metadatos)
        self.assertIn("created_at", self.builder._metadatos)  # Se agrega automáticamente
        self.assertEqual(result, self.builder)

    def test_validate_build_data_completo(self):
        """Test validación con todos los datos completos."""
        # Configurar todos los datos
        self.builder.set_docente(self.test_data['docente'])
        self.builder.set_aula(self.test_data['aula'])
        self.builder.set_asignatura(self.test_data['asignatura'])
        self.builder.set_tiempo("08:00", "10:00")
        self.builder.set_dia("Lunes")
        self.builder.set_sede(self.test_data['sede'])
        self.builder.set_id("H001")

        error = self.builder.validate_build_data()
        self.assertIsNone(error)

    def test_validate_build_data_incompleto(self):
        """Test validación con datos faltantes."""
        # Solo configurar algunos datos
        self.builder.set_docente(self.test_data['docente'])
        self.builder.set_aula(self.test_data['aula'])

        error = self.builder.validate_build_data()
        self.assertIsNotNone(error)
        self.assertIn("Faltan los siguientes campos", error)

    def test_is_valid_time_format(self):
        """Test validación de formato de tiempo."""
        # Formatos válidos
        self.assertTrue(self.builder._is_valid_time_format("08:00"))
        self.assertTrue(self.builder._is_valid_time_format("23:59"))
        self.assertTrue(self.builder._is_valid_time_format("00:00"))

        # Formatos inválidos
        self.assertFalse(self.builder._is_valid_time_format("8:00"))  # Sin cero inicial
        self.assertFalse(self.builder._is_valid_time_format("24:00"))  # Hora inválida
        self.assertFalse(self.builder._is_valid_time_format("08:60"))  # Minuto inválido
        self.assertFalse(self.builder._is_valid_time_format("08"))     # Formato incompleto
        self.assertFalse(self.builder._is_valid_time_format(""))       # Cadena vacía

    def test_method_chaining(self):
        """Test que todos los métodos permiten method chaining."""
        result = (self.builder
                  .reset()
                  .set_docente(self.test_data['docente'])
                  .set_aula(self.test_data['aula'])
                  .set_asignatura(self.test_data['asignatura'])
                  .set_tiempo("08:00", "10:00")
                  .set_dia("Lunes")
                  .set_sede(self.test_data['sede'])
                  .set_id("H001")
                  .set_metadatos(estado="tentativo"))

        self.assertEqual(result, self.builder)

        # Verificar que todos los datos se establecieron
        error = self.builder.validate_build_data()
        self.assertIsNone(error)


if __name__ == '__main__':
    unittest.main()