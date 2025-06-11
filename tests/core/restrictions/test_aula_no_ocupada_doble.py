import unittest

from src.core.restrictions.aulas.aula_no_ocupada_doble_handler import AulaNoOcupadaDobleHandler

class AulaNoOcupadaDobleHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.handler = AulaNoOcupadaDobleHandler()

    def test_aula_sin_solapamiento_global(self):
        """
        No hay solapamiento de horarios en la misma aula (validación global).
        Debe retornar None (válido).
        """
        context = {
            "schedules": [
                {"id": "H1", "aula_id": "AU001", "dia": "lunes", "hora_inicio": "08:00", "hora_fin": "10:00"},
                {"id": "H2", "aula_id": "AU001", "dia": "lunes", "hora_inicio": "10:00", "hora_fin": "12:00"},
                {"id": "H3", "aula_id": "AU002", "dia": "lunes", "hora_inicio": "09:00", "hora_fin": "11:00"}
            ]
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_aula_con_solapamiento_global(self):
        """
        Hay solapamiento de horarios en la misma aula (validación global).
        Debe retornar mensaje de error.
        """
        context = {
            "schedules": [
                {"id": "H1", "aula_id": "AU001", "dia": "lunes", "hora_inicio": "08:00", "hora_fin": "10:00", "asignatura_id": "A001"},
                {"id": "H2", "aula_id": "AU001", "dia": "lunes", "hora_inicio": "09:00", "hora_fin": "11:00", "asignatura_id": "A002"},  # solapa con H1
                {"id": "H3", "aula_id": "AU002", "dia": "lunes", "hora_inicio": "09:00", "hora_fin": "11:00", "asignatura_id": "A003"}
            ]
        }
        result = self.handler.validate(context)
        print(f"\nResultado: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("solapamiento", result.lower())
        self.assertIn("AU001", result)

    def test_aulas_diferentes_mismo_horario_global(self):
        """
        Dos aulas diferentes pueden tener clases al mismo tiempo (validación global).
        Debe retornar None.
        """
        context = {
            "schedules": [
                {"id": "H1", "aula_id": "AU001", "dia": "lunes", "hora_inicio": "08:00", "hora_fin": "10:00"},
                {"id": "H2", "aula_id": "AU002", "dia": "lunes", "hora_inicio": "08:00", "hora_fin": "10:00"}
            ]
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_mismo_horario_misma_aula_misma_clase_global(self):
        """
        Si es exactamente la misma clase (mismo id), no debe reportar error aunque los horarios sean iguales.
        """
        context = {
            "schedules": [
                {"id": "H1", "aula_id": "AU001", "dia": "lunes", "hora_inicio": "08:00", "hora_fin": "10:00"},
                {"id": "H1", "aula_id": "AU001", "dia": "lunes", "hora_inicio": "08:00", "hora_fin": "10:00"}
            ]
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_solapamiento_en_aula_diferente_global(self):
        """
        Solapamiento en horario, pero en aulas diferentes es válido (validación global).
        """
        context = {
            "schedules": [
                {"id": "H1", "aula_id": "AU001", "dia": "lunes", "hora_inicio": "09:00", "hora_fin": "11:00"},
                {"id": "H2", "aula_id": "AU002", "dia": "lunes", "hora_inicio": "10:00", "hora_fin": "12:00"}
            ]
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_validar_bloque_individual_sin_conflicto(self):
        """
        Validación individual: nuevo bloque no solapa con existentes.
        """
        context = {
            "nuevo_bloque": {
                "id": "H4",
                "aula_id": "AU001",
                "dia": "martes",
                "hora_inicio": "12:00",
                "hora_fin": "14:00",
                "asignatura_id": "A004"
            },
            "horarios_existentes": [
                {"id": "H1", "aula_id": "AU001", "dia": "martes", "hora_inicio": "08:00", "hora_fin": "10:00", "asignatura_id": "A001"},
                {"id": "H2", "aula_id": "AU001", "dia": "martes", "hora_inicio": "10:00", "hora_fin": "12:00", "asignatura_id": "A002"}
            ]
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_validar_bloque_individual_con_conflicto(self):
        """
        Validación individual: nuevo bloque solapa con uno existente.
        """
        context = {
            "nuevo_bloque": {
                "id": "H4",
                "aula_id": "AU001",
                "dia": "martes",
                "hora_inicio": "09:30",
                "hora_fin": "11:00",
                "asignatura_id": "A004"
            },
            "horarios_existentes": [
                {"id": "H1", "aula_id": "AU001", "dia": "martes", "hora_inicio": "08:00", "hora_fin": "10:00", "asignatura_id": "A001"},
                {"id": "H2", "aula_id": "AU001", "dia": "martes", "hora_inicio": "10:00", "hora_fin": "12:00", "asignatura_id": "A002"}
            ]
        }
        result = self.handler.validate(context)
        print(f"\nResultado individual: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("conflicto", result.lower())
        self.assertIn("AU001", result)

    def test_validar_bloque_individual_en_aula_diferente(self):
        """
        Validación individual: nuevo bloque en aula diferente, no debe reportar conflicto.
        """
        context = {
            "nuevo_bloque": {
                "id": "H4",
                "aula_id": "AU002",
                "dia": "martes",
                "hora_inicio": "09:30",
                "hora_fin": "11:00",
                "asignatura_id": "A004"
            },
            "horarios_existentes": [
                {"id": "H1", "aula_id": "AU001", "dia": "martes", "hora_inicio": "08:00", "hora_fin": "10:00", "asignatura_id": "A001"},
                {"id": "H2", "aula_id": "AU001", "dia": "martes", "hora_inicio": "10:00", "hora_fin": "12:00", "asignatura_id": "A002"}
            ]
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()