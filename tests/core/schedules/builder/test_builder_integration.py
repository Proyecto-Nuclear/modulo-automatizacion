import unittest

from src.core.schedules.builders.builder_factory import BuilderFactory
from src.core.schedules.builders.horario_director import HorarioDirector
from test_builder_base_helper import BuilderTestData


class BuilderIntegrationTestCase(unittest.TestCase):
    """Tests de integración para el patrón Builder completo."""

    def setUp(self):
        """Configuración común para cada test."""
        self.director = HorarioDirector()
        self.test_data = BuilderTestData()

    def test_flujo_completo_clase_normal(self):
        """Test del flujo completo para crear una clase normal."""
        # Crear builder usando factory
        builder = BuilderFactory.create_builder('normal')

        # Usar director para construir
        self.director.set_builder(builder)

        # Datos de prueba
        datos = self.test_data.get_valid_horario_data()

        # Construir horario
        horario = self.director.construct_horario_completo(datos)

        # Verificaciones
        self.assertIsNotNone(horario)
        self.assertEqual(horario.docente, datos['docente'])
        self.assertEqual(horario.aula, datos['aula'])

    def test_flujo_completo_laboratorio(self):
        """Test del flujo completo para crear un laboratorio."""
        builder = BuilderFactory.create_builder('laboratorio')
        self.director.set_builder(builder)

        datos = self.test_data.get_laboratorio_data()
        horario = self.director.construct_horario_completo(datos)

        self.assertIsNotNone(horario)

    def test_flujo_completo_virtual(self):
        """Test del flujo completo para crear una clase virtual."""
        builder = BuilderFactory.create_builder('virtual')
        self.director.set_builder(builder)

        datos = self.test_data.get_virtual_data()
        horario = self.director.construct_horario_completo(datos)

        self.assertIsNotNone(horario)

    def test_flujo_completo_bloqueo(self):
        """Test del flujo completo para crear un bloqueo."""
        builder = BuilderFactory.create_builder('bloqueo')
        self.director.set_builder(builder)

        datos = self.test_data.get_bloqueo_data()
        horario = self.director.construct_horario_completo(datos)

        self.assertIsNotNone(horario)

    def test_cambio_de_builder_en_director(self):
        """Test cambiar de builder en el director."""
        # Crear horario normal
        builder_normal = BuilderFactory.create_builder('normal')
        self.director.set_builder(builder_normal)

        datos_normal = self.test_data.get_valid_horario_data()
        horario_normal = self.director.construct_horario_completo(datos_normal)

        # Cambiar a builder de laboratorio
        builder_lab = BuilderFactory.create_builder('laboratorio')
        self.director.set_builder(builder_lab)

        datos_lab = self.test_data.get_laboratorio_data()
        horario_lab = self.director.construct_horario_completo(datos_lab)

        # Verificar que ambos se crearon correctamente
        self.assertIsNotNone(horario_normal)
        self.assertIsNotNone(horario_lab)

        # Verificar que el director cambió de builder
        self.assertEqual(self.director.get_builder_tipo(), 'laboratorio')


if __name__ == '__main__':
    unittest.main()