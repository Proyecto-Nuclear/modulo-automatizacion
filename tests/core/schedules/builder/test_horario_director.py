import unittest
from unittest.mock import Mock, patch

from src.core.schedules.builders.horario_director import HorarioDirector
from src.core.schedules.builders.horario_normal_builder import HorarioNormalBuilder
from src.core.schedules.builders.builder_factory import BuilderFactory
from test_builder_base_helper import BuilderTestData


class HorarioDirectorTestCase(unittest.TestCase):

    def setUp(self):
        """Configuración común para cada test."""
        self.director = HorarioDirector()
        self.builder = HorarioNormalBuilder()
        self.test_data = BuilderTestData.get_valid_horario_data()

    def test_set_builder(self):
        """Test establecer builder."""
        self.director.set_builder(self.builder)
        self.assertEqual(self.director._builder, self.builder)

    def test_get_builder_tipo_con_builder(self):
        """Test obtener tipo de builder cuando hay builder configurado."""
        self.director.set_builder(self.builder)
        tipo = self.director.get_builder_tipo()
        self.assertEqual(tipo, 'normal')

    def test_get_builder_tipo_sin_builder(self):
        """Test obtener tipo de builder cuando no hay builder configurado."""
        tipo = self.director.get_builder_tipo()
        self.assertIsNone(tipo)

    def test_construct_horario_completo_exitoso(self):
        """Test construcción completa exitosa."""
        self.director.set_builder(self.builder)

        horario = self.director.construct_horario_completo(self.test_data)

        self.assertIsNotNone(horario)

    def test_construct_horario_completo_sin_builder(self):
        """Test construcción completa sin builder configurado."""
        with self.assertRaises(ValueError) as context:
            self.director.construct_horario_completo(self.test_data)

        self.assertIn("No hay builder configurado", str(context.exception))

    def test_construct_horario_basico_exitoso(self):
        """Test construcción básica exitosa."""
        horario = self.director.construct_horario_basico(
            tipo='normal',
            docente=self.test_data['docente'],
            aula=self.test_data['aula'],
            asignatura=self.test_data['asignatura'],
            start_time='08:00',
            end_time='10:00',
            dia='Lunes',
            sede=self.test_data['sede'],
            horario_id='H001'
        )

        self.assertIsNotNone(horario)

    @patch.object(BuilderFactory, 'create_builder')
    def test_construct_horario_basico_usa_factory(self, mock_create_builder):
        """Test que construcción básica usa el factory."""
        mock_builder = Mock()
        mock_builder.reset.return_value = mock_builder
        mock_builder.set_docente.return_value = mock_builder
        mock_builder.set_aula.return_value = mock_builder
        mock_builder.set_asignatura.return_value = mock_builder
        mock_builder.set_tiempo.return_value = mock_builder
        mock_builder.set_dia.return_value = mock_builder
        mock_builder.set_sede.return_value = mock_builder
        mock_builder.set_id.return_value = mock_builder
        mock_builder.build.return_value = Mock()

        mock_create_builder.return_value = mock_builder

        self.director.construct_horario_basico(
            tipo='normal',
            docente=self.test_data['docente'],
            aula=self.test_data['aula'],
            asignatura=self.test_data['asignatura'],
            start_time='08:00',
            end_time='10:00',
            dia='Lunes',
            sede=self.test_data['sede'],
            horario_id='H001'
        )

        # Verificar que se llamó al factory
        mock_create_builder.assert_called_once_with('normal')

        # Verificar que se llamaron los métodos del builder
        mock_builder.reset.assert_called_once()
        mock_builder.set_docente.assert_called_once_with(self.test_data['docente'])
        mock_builder.build.assert_called_once()

    def test_construct_horario_completo_con_metadatos(self):
        """Test construcción completa con metadatos adicionales."""
        self.director.set_builder(self.builder)

        datos_con_metadatos = self.test_data.copy()
        datos_con_metadatos.update({
            'estado': 'confirmado',
            'observaciones': 'Clase especial',
            'recursos_especiales': {'proyector': True}
        })

        horario = self.director.construct_horario_completo(datos_con_metadatos)

        self.assertIsNotNone(horario)


if __name__ == '__main__':
    unittest.main()