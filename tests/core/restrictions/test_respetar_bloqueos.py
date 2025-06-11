import unittest
from src.core.restrictions.horarios.respetar_bloqueos_handler import RespetarBloqueosHandler

class RespetarBloqueosHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.handler = RespetarBloqueosHandler()

    def test_horario_sin_solapamiento_con_bloqueo(self):
        """
        Horario no solapa con bloqueo en el aula.
        Debe retornar None (válido).
        """
        context = {
            "schedules": [
                {"id": "H1", "aula": "AU001", "start_time": "08:00", "end_time": "10:00"}
            ],
            "bloqueos": [
                {"aula": "AU001", "horario": {"start_time": "10:00", "end_time": "12:00"}}
            ]
        }
        result = self.handler.validate(context)
        if result is not None:
            print("Error inesperado:", result)
        self.assertIsNone(result)

    def test_horario_con_solapamiento_con_bloqueo(self):
        """
        Horario solapa con bloqueo en el aula.
        Debe retornar mensaje de error.
        """
        context = {
            "schedules": [
                {"id": "H1", "aula": "AU001", "start_time": "09:00", "end_time": "11:00"}
            ],
            "bloqueos": [
                {"aula": "AU001", "horario": {"start_time": "10:00", "end_time": "12:00"}}
            ]
        }
        result = self.handler.validate(context)
        print(f"\n{result}")
        self.assertIsInstance(result, str)
        self.assertIn("bloqueo", result.lower())
        self.assertIn("AU001", result)
        self.assertIn("H1", result)

    def test_horarios_en_aulas_diferentes(self):
        """
        Bloqueo y horario están en aulas diferentes.
        Debe retornar None.
        """
        context = {
            "schedules": [
                {"id": "H1", "aula": "AU002", "start_time": "09:00", "end_time": "11:00"}
            ],
            "bloqueos": [
                {"aula": "AU001", "horario": {"start_time": "09:00", "end_time": "11:00"}}
            ]
        }
        result = self.handler.validate(context)
        if result is not None:
            print("Error inesperado:", result)
        self.assertIsNone(result)

    def test_varios_horarios_y_bloqueos(self):
        """
        Varios schedules y bloqueos, uno solapa.
        Debe retornar mensaje de error por el que solapa.
        """
        context = {
            "schedules": [
                {"id": "H1", "aula": "AU001", "start_time": "07:00", "end_time": "09:00"},
                {"id": "H2", "aula": "AU001", "start_time": "10:00", "end_time": "12:00"},
                {"id": "H3", "aula": "AU002", "start_time": "08:00", "end_time": "10:00"},
                {"id": "H4", "aula": "AU003", "start_time": "12:00", "end_time": "13:00"}
            ],
            "bloqueos": [
                {"aula": "AU001", "horario": {"start_time": "08:00", "end_time": "11:00"}},
                {"aula": "AU003", "horario": {"start_time": "12:00", "end_time": "13:00"}}
            ]
        }
        result = self.handler.validate(context)
        print(f"\n{result}")
        self.assertIsInstance(result, str)
        self.assertIn("bloqueo", result.lower())
        self.assertIn("AU001", result)
        self.assertTrue("H1" in result or "H2" in result or "H3" in result)

    def test_horario_exactamente_antes_del_bloqueo(self):
        """
        Horario termina justo cuando inicia el bloqueo.
        Debe retornar None.
        """
        context = {
            "schedules": [
                {"id": "H1", "aula": "AU003", "start_time": "08:00", "end_time": "10:00"}
            ],
            "bloqueos": [
                {"aula": "AU003", "horario": {"start_time": "10:00", "end_time": "12:00"}}
            ]
        }
        result = self.handler.validate(context)
        if result is not None:
            print("Error inesperado:", result)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()