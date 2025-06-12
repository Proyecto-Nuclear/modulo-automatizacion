import unittest
import json
import os
from unittest.mock import patch, MagicMock

from src.core.schedules.facade.horario_facade import HorarioFacade
from src.core.schedules.selector_factory import SelectorFactory

def load_json(filename):
    """Helper para cargar archivos JSON desde el directorio de datos."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, '../../../data'))
    with open(os.path.join(data_dir, filename), encoding="utf-8") as f:
        return json.load(f)

class HorarioFacadeTestCase(unittest.TestCase):
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

    def setUp(self):
        """Configuración común para cada test."""
        self.facade = HorarioFacade()
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

    def test_crear_horario_exitoso(self):
        with patch.object(self.facade.validador, 'validar_horario', return_value=(True, None)), \
                patch.object(self.facade.estadisticas, 'obtener_estadisticas', return_value={'estadisticas': {'horarios_creados': 1, 'validaciones_exitosas': 1}}):
            horario, error = self.facade.crear_horario("normal", **self.kwargs_base)
            self.assertIsNotNone(horario, "El horario no debe ser None")
            self.assertIsNone(error, "No debe haber error")
            self.assertEqual(horario.get_tipo(), "normal")
            stats = self.facade.obtener_estadisticas()
            self.assertEqual(stats['estadisticas']['horarios_creados'], 1)
            self.assertEqual(stats['estadisticas']['validaciones_exitosas'], 1)

    def test_crear_horario_fallido_por_restriccion(self):
        """Test de creación fallida por restricción."""
        # Mock del validador para que falle
        with patch.object(self.facade.validador, 'validar_horario', return_value=(False, "Conflicto simulado")), \
            patch.object(self.facade.estadisticas, 'obtener_estadisticas', return_value={'estadisticas': {'horarios_creados': 0, 'validaciones_fallidas': 1}}):
            horario, error = self.facade.crear_horario("normal", **self.kwargs_base)

            # El horario puede no ser None, pero debe haber error
            self.assertIsNotNone(horario, "El horario debe existir aunque sea inválido")
            self.assertIsNotNone(error, "Debe haber error")
            self.assertIn("Restricción violada", error)

            stats = self.facade.obtener_estadisticas()
            self.assertEqual(stats['estadisticas']['horarios_creados'], 0)
            self.assertEqual(stats['estadisticas']['validaciones_fallidas'], 1)

    def test_crear_horario_fallido_por_factory(self):
        """Test de creación fallida por error en el factory."""
        # Mock del SelectorFactory para que falle
        with patch.object(SelectorFactory, 'crear_horario', return_value=(None, "Error en factory")), \
            patch.object(self.facade.estadisticas, 'obtener_estadisticas', return_value={'estadisticas': {'horarios_creados': 0, 'validaciones_fallidas': 1}}):
            horario, error = self.facade.crear_horario("normal", **self.kwargs_base)

            self.assertIsNone(horario, "El horario debe ser None")
            self.assertIsNotNone(error, "Debe haber error")
            self.assertIn("Error en creación", error)

            # Verificar estadísticas
            stats = self.facade.obtener_estadisticas()
            self.assertEqual(stats['estadisticas']['horarios_creados'], 0)
            self.assertEqual(stats['estadisticas']['validaciones_fallidas'], 1)

    def test_validar_horario_exitoso(self):
        """Test de validación exitosa de horario."""
        # Mock del validador para que sea exitoso
        with patch.object(self.facade.validador, 'validar_horario', return_value=(True, None)):
            es_valido, error = self.facade.validar_horario(self.kwargs_base)

            self.assertTrue(es_valido, "El horario debe ser válido")
            self.assertIsNone(error, "No debe haber error")

            # Verificar que se llamó al validador
            self.facade.validador.validar_horario.assert_called_once_with(self.kwargs_base)

    def test_validar_horario_fallido(self):
        """Test de validación fallida de horario."""
        # Mock del validador para que falle
        with patch.object(self.facade.validador, 'validar_horario', return_value=(False, "Conflicto simulado")):
            es_valido, error = self.facade.validar_horario(self.kwargs_base)

            self.assertFalse(es_valido, "El horario no debe ser válido")
            self.assertIsNotNone(error, "Debe haber error")
            self.assertEqual(error, "Conflicto simulado")

    def test_crear_horarios_lote_exitoso(self):
        """Test de creación en lote exitosa."""
        horarios_data = [
            {**self.kwargs_base, "tipo": "normal"},
            {**self.kwargs_base, "tipo": "normal"}
        ]

        # Mock del creador para que sea exitoso
        mock_resultado = {
            'exitosos': [
                {'indice': 0, 'horario': MagicMock(), 'tipo': 'normal'},
                {'indice': 1, 'horario': MagicMock(), 'tipo': 'normal'}
            ],
            'fallidos': [],
            'errores': [],
            'resumen': {'total': 2, 'exitosos': 2, 'fallidos': 0}
        }

        with patch.object(self.facade.creador, 'crear_horarios_lote', return_value=mock_resultado):
            resultados = self.facade.crear_horarios_lote(horarios_data)

            self.assertEqual(resultados['resumen']['total'], 2)
            self.assertEqual(resultados['resumen']['exitosos'], 2)
            self.assertEqual(resultados['resumen']['fallidos'], 0)
            self.assertEqual(len(resultados['exitosos']), 2)
            self.assertEqual(len(resultados['fallidos']), 0)

    def test_crear_horarios_lote_mixto(self):
        """Test de creación en lote con algunos fallos."""
        horarios_data = [
            {**self.kwargs_base, "tipo": "normal"},
            {**self.kwargs_base, "tipo": "normal"},
            {**self.kwargs_base, "tipo": "normal"}
        ]

        # Mock del creador para que tenga resultados mixtos
        mock_resultado = {
            'exitosos': [
                {'indice': 0, 'horario': MagicMock(), 'tipo': 'normal'},
                {'indice': 2, 'horario': MagicMock(), 'tipo': 'normal'}
            ],
            'fallidos': [
                {'indice': 1, 'error': 'Conflicto simulado', 'datos': self.kwargs_base}
            ],
            'errores': ['Horario 1: Conflicto simulado'],
            'resumen': {'total': 3, 'exitosos': 2, 'fallidos': 1}
        }

        with patch.object(self.facade.creador, 'crear_horarios_lote', return_value=mock_resultado):
            resultados = self.facade.crear_horarios_lote(horarios_data)

            self.assertEqual(resultados['resumen']['total'], 3)
            self.assertEqual(resultados['resumen']['exitosos'], 2)
            self.assertEqual(resultados['resumen']['fallidos'], 1)
            self.assertEqual(len(resultados['exitosos']), 2)
            self.assertEqual(len(resultados['fallidos']), 1)

    def test_buscar_horarios_docente(self):
        """Test de búsqueda de horarios por docente."""
        # Crear mocks de horarios
        horario1 = MagicMock()
        horario2 = MagicMock()
        horarios = [horario1, horario2]

        # Mock del buscador
        with patch.object(self.facade.buscador, 'buscar_horarios_docente', return_value=horarios):
            horarios_docente = self.facade.buscar_horarios_docente(self.docentes[0]['id'], horarios)

            self.assertEqual(len(horarios_docente), 2)
            self.facade.buscador.buscar_horarios_docente.assert_called_once_with(
                self.docentes[0]['id'], horarios
            )

    def test_buscar_horarios_aula(self):
        """Test de búsqueda de horarios por aula."""
        # Crear mocks de horarios
        horario1 = MagicMock()
        horarios = [horario1]

        # Mock del buscador
        with patch.object(self.facade.buscador, 'buscar_horarios_aula', return_value=horarios):
            horarios_aula = self.facade.buscar_horarios_aula(self.aulas[0]['id'], horarios)

            self.assertEqual(len(horarios_aula), 1)
            self.facade.buscador.buscar_horarios_aula.assert_called_once_with(
                self.aulas[0]['id'], horarios
            )

    def test_buscar_horarios_dia(self):
        """Test de búsqueda de horarios por día."""
        # Crear mocks de horarios
        horario1 = MagicMock()
        horarios = [horario1]

        # Mock del buscador
        with patch.object(self.facade.buscador, 'buscar_horarios_dia', return_value=horarios):
            horarios_dia = self.facade.buscar_horarios_dia("Lunes", horarios)

            self.assertEqual(len(horarios_dia), 1)
            self.facade.buscador.buscar_horarios_dia.assert_called_once_with("Lunes", horarios)

    def test_detectar_conflictos(self):
        """Test de detección de conflictos."""
        horarios = [MagicMock(), MagicMock()]
        conflictos_mock = {
            'docentes': ['Conflicto de docente'],
            'aulas': [],
            'otros': []
        }

        # Mock del validador
        with patch.object(self.facade.validador, 'detectar_conflictos', return_value=conflictos_mock):
            conflictos = self.facade.detectar_conflictos(horarios)

            self.assertEqual(len(conflictos['docentes']), 1)
            self.assertEqual(len(conflictos['aulas']), 0)
            self.facade.validador.detectar_conflictos.assert_called_once_with(horarios)

    def test_configurar_y_obtener_configuracion(self):
        """Test de configuración y obtención de configuración."""
        # Mock del configurador
        config_mock = {'validar_restricciones': False, 'incluir_metadatos': False}

        with patch.object(self.facade.configurador, 'configurar') as mock_configurar, \
                patch.object(self.facade.configurador, 'obtener_configuracion', return_value=config_mock):

            self.facade.configurar(validar_restricciones=False, incluir_metadatos=False)
            config = self.facade.obtener_configuracion()

            mock_configurar.assert_called_once_with({
                'validar_restricciones': False,
                'incluir_metadatos': False
            })
            self.assertFalse(config['validar_restricciones'])
            self.assertFalse(config['incluir_metadatos'])

    def test_obtener_estadisticas(self):
        """Test de obtención de estadísticas."""
        stats_mock = {'estadisticas': {'horarios_creados': 1, 'validaciones_exitosas': 1}}

        with patch.object(self.facade.estadisticas, 'obtener_estadisticas', return_value=stats_mock):
            estadisticas = self.facade.obtener_estadisticas()

            self.assertEqual(estadisticas['estadisticas']['horarios_creados'], 1)
            self.facade.estadisticas.obtener_estadisticas.assert_called_once()

    def test_reiniciar_estadisticas(self):
        """Test de reinicio de estadísticas."""
        with patch.object(self.facade.estadisticas, 'reiniciar_estadisticas') as mock_reiniciar:
            self.facade.reiniciar_estadisticas()
            mock_reiniciar.assert_called_once()

    def test_exportar_horarios_json(self):
        """Test de exportación de horarios a JSON."""
        horario = MagicMock()
        horarios_json_mock = '{"horario": "test"}'

        with patch.object(self.facade.exportador, 'exportar_horarios', return_value=horarios_json_mock):
            horarios_json = self.facade.exportar_horarios([horario], formato='json')

            self.assertIsInstance(horarios_json, str)
            self.assertEqual(horarios_json, horarios_json_mock)
            self.facade.exportador.exportar_horarios.assert_called_once_with([horario], 'json')

    def test_exportar_horarios_dict(self):
        """Test de exportación de horarios a diccionario."""
        horario = MagicMock()
        horarios_dict_mock = [{'id': 'H001', 'tipo': 'normal'}]

        with patch.object(self.facade.exportador, 'exportar_horarios', return_value=horarios_dict_mock):
            horarios_dict = self.facade.exportar_horarios([horario], formato='dict')

            self.assertIsInstance(horarios_dict, list)
            self.assertEqual(horarios_dict, horarios_dict_mock)

    def test_obtener_tipos_horarios_disponibles(self):
        """Test de obtener tipos de horarios disponibles."""
        tipos_mock = ["normal", "laboratorio", "virtual"]

        with patch.object(self.facade.creador, 'obtener_tipos_horarios_disponibles', return_value=tipos_mock):
            tipos = self.facade.obtener_tipos_horarios_disponibles()

            self.assertIsInstance(tipos, list)
            self.assertEqual(tipos, tipos_mock)
            self.facade.creador.obtener_tipos_horarios_disponibles.assert_called_once()

    def test_es_tipo_horario_valido(self):
        """Test de verificación de tipo de horario válido."""
        with patch.object(self.facade.creador, 'es_tipo_horario_valido', side_effect=[True, False]):
            self.assertTrue(self.facade.es_tipo_horario_valido("normal"))
            self.assertFalse(self.facade.es_tipo_horario_valido("tipo_invalido"))

    def test_obtener_resumen_sistema(self):
        """Test de obtener resumen del sistema."""
        # Mocks para todos los componentes
        tipos_mock = ["normal", "laboratorio"]
        config_mock = {"validar_restricciones": True}
        stats_mock = {"estadisticas": {"horarios_creados": 5}}
        restricciones_mock = ["IntegridadEntidadesHandler", "AulaNoOcupadaDobleHandler"]

        with patch.object(self.facade.creador, 'obtener_tipos_horarios_disponibles', return_value=tipos_mock), \
                patch.object(self.facade.configurador, 'obtener_configuracion', return_value=config_mock), \
                patch.object(self.facade.estadisticas, 'obtener_estadisticas', return_value=stats_mock), \
                patch.object(self.facade.restricciones, 'obtener_info_restricciones', return_value=restricciones_mock):

            resumen = self.facade.obtener_resumen_sistema()

            self.assertIsInstance(resumen, dict)
            self.assertIn("facade_version", resumen)
            self.assertEqual(resumen["facade_version"], "2.0")
            self.assertEqual(resumen["tipos_horarios_disponibles"], tipos_mock)
            self.assertEqual(resumen["configuracion"], config_mock)
            self.assertEqual(resumen["estadisticas"], stats_mock)
            self.assertEqual(resumen["restricciones_configuradas"], restricciones_mock)

    def test_validar_horarios_conjunto(self):
        """Test de validación de conjunto de horarios."""
        horarios_data = [self.kwargs_base, self.kwargs_base]

        with patch.object(self.facade.validador, 'validar_horarios_conjunto', return_value=(True, None)):
            es_valido, error = self.facade.validar_horarios_conjunto(horarios_data)

            self.assertTrue(es_valido)
            self.assertIsNone(error)
            self.facade.validador.validar_horarios_conjunto.assert_called_once_with(horarios_data)

    def test_str_y_repr(self):
        stats_mock = {'estadisticas': {'horarios_creados': 5, 'validaciones_exitosas': 10}}
        with patch.object(self.facade.estadisticas, 'stats', stats_mock['estadisticas']):
            str_result = str(self.facade)
            self.assertIn("HorarioFacade", str_result)
            self.assertIn("horarios_creados=5", str_result)
            self.assertIn("validaciones_exitosas=10", str_result)
            repr_result = repr(self.facade)
            self.assertIn("HorarioFacade", repr_result)

if __name__ == '__main__':
    unittest.main()