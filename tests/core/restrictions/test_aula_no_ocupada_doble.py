import unittest

from src.core.restrictions.aulas.aula_no_ocupada_doble_handler import AulaNoOcupadaDobleHandler

class AulaNoOcupadaDobleHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.handler = AulaNoOcupadaDobleHandler()

    def test_aula_sin_solapamiento(self):
        """
        No hay solapamiento de schedules en la misma aula.
        Debe retornar None (válido).
        """
        context = {
            "schedules": [
                {"id": "H1", "aula": "AU001", "start_time": "08:00", "end_time": "10:00"},
                {"id": "H2", "aula": "AU001", "start_time": "10:00", "end_time": "12:00"},
                {"id": "H3", "aula": "AU002", "start_time": "09:00", "end_time": "11:00"}
            ]
        }
        result = self.handler.validate(context)
        if result is not None:
            print("Error inesperado:", result)
        self.assertIsNone(result)

    def test_aula_con_solapamiento(self):
        """
        Hay solapamiento de schedules en la misma aula.
        Debe retornar mensaje de error.
        """
        context = {
            "schedules": [
                {"id": "H1", "aula": "AU001", "start_time": "08:00", "end_time": "10:00"},
                {"id": "H2", "aula": "AU001", "start_time": "09:00", "end_time": "11:00"},  # solapa con H1
                {"id": "H3", "aula": "AU002", "start_time": "09:00", "end_time": "11:00"}
            ]
        }
        result = self.handler.validate(context)
        print(f"\n{result}")
        self.assertIsInstance(result, str)
        self.assertIn("Solapamiento", result)
        self.assertIn("AU001", result)
        self.assertTrue("H1" in result and "H2" in result)

    def test_aulas_diferentes_mismo_horario(self):
        """
        Dos aulas diferentes pueden tener clases al mismo tiempo.
        Debe retornar None.
        """
        context = {
            "schedules": [
                {"id": "H1", "aula": "AU001", "start_time": "08:00", "end_time": "10:00"},
                {"id": "H2", "aula": "AU002", "start_time": "08:00", "end_time": "10:00"}
            ]
        }
        result = self.handler.validate(context)
        if result is not None:
            print("Error inesperado:", result)
        self.assertIsNone(result)

    def test_mismo_horario_misma_aula_misma_clase(self):
        """
        Si es exactamente la misma clase (mismo id), no debe reportar error aunque los schedules sean iguales.
        """
        context = {
            "schedules": [
                {"id": "H1", "aula": "AU001", "start_time": "08:00", "end_time": "10:00"},
                {"id": "H1", "aula": "AU001", "start_time": "08:00", "end_time": "10:00"}
            ]
        }
        result = self.handler.validate(context)
        if result is not None:
            print("Error inesperado:", result)
        self.assertIsNone(result)

    def test_solapamiento_en_aula_diferente(self):
        """
        Solapamiento en horario, pero en aulas diferentes es válido.
        """
        context = {
            "schedules": [
                {"id": "H1", "aula": "AU001", "start_time": "09:00", "end_time": "11:00"},
                {"id": "H2", "aula": "AU002", "start_time": "10:00", "end_time": "12:00"}
            ]
        }
        result = self.handler.validate(context)
        if result is not None:
            print("Error inesperado:", result)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
