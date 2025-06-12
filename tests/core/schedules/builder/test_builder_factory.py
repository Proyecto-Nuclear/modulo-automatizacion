import unittest

from src.core.schedules.builders.builder_factory import BuilderFactory
from src.core.schedules.builders.horario_normal_builder import HorarioNormalBuilder
from src.core.schedules.builders.horario_laboratorio_builder import HorarioLaboratorioBuilder
from src.core.schedules.builders.horario_virtual_builder import HorarioVirtualBuilder
from src.core.schedules.builders.horario_bloqueo_builder import HorarioBloqueoBuilder
from src.core.schedules.builders.horario_builder_interface import IHorarioBuilder


class BuilderFactoryTestCase(unittest.TestCase):

    def test_create_builder_normal(self):
        """Test crear builder normal."""
        builder = BuilderFactory.create_builder('normal')

        self.assertIsInstance(builder, HorarioNormalBuilder)
        self.assertIsInstance(builder, IHorarioBuilder)
        self.assertEqual(builder.get_tipo(), 'normal')

    def test_create_builder_laboratorio(self):
        """Test crear builder laboratorio."""
        builder = BuilderFactory.create_builder('laboratorio')

        self.assertIsInstance(builder, HorarioLaboratorioBuilder)
        self.assertEqual(builder.get_tipo(), 'laboratorio')

    def test_create_builder_virtual(self):
        """Test crear builder virtual."""
        builder = BuilderFactory.create_builder('virtual')

        self.assertIsInstance(builder, HorarioVirtualBuilder)
        self.assertEqual(builder.get_tipo(), 'virtual')

    def test_create_builder_bloqueo(self):
        """Test crear builder bloqueo."""
        builder = BuilderFactory.create_builder('bloqueo')

        self.assertIsInstance(builder, HorarioBloqueoBuilder)
        self.assertEqual(builder.get_tipo(), 'bloqueo')

    def test_create_builder_tipo_invalido(self):
        """Test crear builder con tipo inválido."""
        with self.assertRaises(ValueError) as context:
            BuilderFactory.create_builder('tipo_inexistente')

        self.assertIn("no disponible", str(context.exception))
        self.assertIn("Tipos disponibles", str(context.exception))

    def test_get_available_types(self):
        """Test obtener tipos disponibles."""
        tipos = BuilderFactory.get_available_types()

        self.assertIsInstance(tipos, list)
        self.assertIn('normal', tipos)
        self.assertIn('laboratorio', tipos)
        self.assertIn('virtual', tipos)
        self.assertIn('bloqueo', tipos)
        self.assertEqual(len(tipos), 4)

    def test_is_type_available(self):
        """Test verificar si tipo está disponible."""
        self.assertTrue(BuilderFactory.is_type_available('normal'))
        self.assertTrue(BuilderFactory.is_type_available('laboratorio'))
        self.assertFalse(BuilderFactory.is_type_available('tipo_inexistente'))

    def test_register_builder_valido(self):
        """Test registrar nuevo builder válido."""
        # Crear una clase builder de prueba
        class TestBuilder(IHorarioBuilder):
            def reset(self): return self
            def set_docente(self, docente): return self
            def set_aula(self, aula): return self
            def set_asignatura(self, asignatura): return self
            def set_tiempo(self, start_time, end_time): return self
            def set_dia(self, dia): return self
            def set_sede(self, sede): return self
            def set_id(self, horario_id): return self
            def set_metadatos(self, **metadatos): return self
            def build(self): return None
            def validate_build_data(self): return None
            def get_tipo(self): return 'test'

        # Registrar el builder
        BuilderFactory.register_builder('test', TestBuilder)

        # Verificar que se registró
        self.assertTrue(BuilderFactory.is_type_available('test'))

        # Crear instancia
        builder = BuilderFactory.create_builder('test')
        self.assertIsInstance(builder, TestBuilder)

        # Limpiar después del test
        if 'test' in BuilderFactory._builders:
            del BuilderFactory._builders['test']

    def test_register_builder_invalido(self):
        """Test registrar builder inválido."""
        class InvalidBuilder:
            pass

        with self.assertRaises(ValueError) as context:
            BuilderFactory.register_builder('invalid', InvalidBuilder)

        self.assertIn("debe implementar IHorarioBuilder", str(context.exception))


if __name__ == '__main__':
    unittest.main()