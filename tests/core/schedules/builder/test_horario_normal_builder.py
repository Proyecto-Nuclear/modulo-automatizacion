import unittest

from src.core.schedules.builders.horario_normal_builder import HorarioNormalBuilder
from test_builder_base_helper import BuilderTestData


class HorarioNormalBuilderTestCase(unittest.TestCase):

    def setUp(self):
        """Configuración común para cada test."""
        self.builder = HorarioNormalBuilder()
        self.test_data = BuilderTestData.get_valid_horario_data()

    def test_get_tipo(self):
        """Test que retorna el tipo correcto."""
        self.assertEqual(self.builder.get_tipo(), 'normal')

    def test_build_exitoso(self):
        """Test construcción exitosa de horario normal."""
        # Configurar todos los datos
        horario = (self.builder
                   .set_docente(self.test_data['docente'])
                   .set_aula(self.test_data['aula'])
                   .set_asignatura(self.test_data['asignatura'])
                   .set_tiempo("08:00", "10:00")
                   .set_dia("Lunes")
                   .set_sede(self.test_data['sede'])
                   .set_id("H001")
                   .build())

        self.assertIsNotNone(horario)
        self.assertEqual(horario.docente, self.test_data['docente'])
        self.assertEqual(horario.aula, self.test_data['aula'])

    def test_build_falla_datos_incompletos(self):
        """Test que falla con datos incompletos."""
        # Solo configurar algunos datos
        self.builder.set_docente(self.test_data['docente'])

        with self.assertRaises(ValueError) as context:
            self.builder.build()
        self.assertIn("Error en construcción", str(context.exception))

    def test_build_falla_aula_tipo_incorrecto(self):
        """Test que falla con tipo de aula incorrecto."""
        aula_incorrecta = self.test_data['aula'].copy()
        aula_incorrecta['tipo'] = 'laboratorio'  # Tipo incorrecto para clase normal

        with self.assertRaises(ValueError) as context:
            (self.builder
             .set_docente(self.test_data['docente'])
             .set_aula(aula_incorrecta)
             .set_asignatura(self.test_data['asignatura'])
             .set_tiempo("08:00", "10:00")
             .set_dia("Lunes")
             .set_sede(self.test_data['sede'])
             .set_id("H001")
             .build())

        self.assertIn("aula debe ser de tipo", str(context.exception))

    def test_build_falla_asignatura_solo_laboratorio(self):
        """Test que falla con asignatura que solo permite laboratorio."""
        asignatura_lab = self.test_data['asignatura'].copy()
        asignatura_lab['solo_laboratorio'] = True

        with self.assertRaises(ValueError) as context:
            (self.builder
             .set_docente(self.test_data['docente'])
             .set_aula(self.test_data['aula'])
             .set_asignatura(asignatura_lab)
             .set_tiempo("08:00", "10:00")
             .set_dia("Lunes")
             .set_sede(self.test_data['sede'])
             .set_id("H001")
             .build())

        self.assertIn("solo permite laboratorios", str(context.exception))

    def test_build_falla_duracion_muy_corta(self):
        """Test que falla con duración muy corta."""
        with self.assertRaises(ValueError) as context:
            (self.builder
             .set_docente(self.test_data['docente'])
             .set_aula(self.test_data['aula'])
             .set_asignatura(self.test_data['asignatura'])
             .set_tiempo("08:00", "08:30")  # Solo 30 minutos
             .set_dia("Lunes")
             .set_sede(self.test_data['sede'])
             .set_id("H001")
             .build())

        self.assertIn("al menos 50 minutos", str(context.exception))

    def test_build_falla_duracion_muy_larga(self):
        """Test que falla con duración muy larga."""
        with self.assertRaises(ValueError) as context:
            (self.builder
             .set_docente(self.test_data['docente'])
             .set_aula(self.test_data['aula'])
             .set_asignatura(self.test_data['asignatura'])
             .set_tiempo("08:00", "12:00")  # 4 horas
             .set_dia("Lunes")
             .set_sede(self.test_data['sede'])
             .set_id("H001")
             .build())

        self.assertIn("más de 3 horas", str(context.exception))

    def test_set_recursos_especiales(self):
        """Test establecer recursos especiales."""
        recursos = {"proyector": True, "computadora": True}
        result = self.builder.set_recursos_especiales(recursos)

        self.assertEqual(self.builder._metadatos['recursos_especiales'], recursos)
        self.assertEqual(result, self.builder)  # Method chaining

    def test_set_recursos_especiales_invalido(self):
        """Test establecer recursos especiales inválidos."""
        with self.assertRaises(ValueError):
            self.builder.set_recursos_especiales("no es diccionario")

    def test_set_modalidad_hibrida(self):
        """Test establecer modalidad híbrida."""
        result = self.builder.set_modalidad_hibrida(True)

        self.assertTrue(self.builder._metadatos['modalidad_hibrida'])
        self.assertEqual(result, self.builder)

    def test_reset_limpia_configuraciones_especificas(self):
        """Test que reset limpia configuraciones específicas de clase normal."""
        self.builder.set_recursos_especiales({"proyector": True})
        self.builder.set_modalidad_hibrida(True)

        self.builder.reset()

        self.assertEqual(self.builder._metadatos, {})


if __name__ == '__main__':
    unittest.main()