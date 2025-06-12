import unittest
import json
import os

from src.core.restrictions.horarios.respetar_bloqueos_handler import RespetarBloqueosHandler

def load_json(filename):
    """Helper to load JSON from the data directory."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, '../../../data'))
    with open(os.path.join(data_dir, filename), encoding="utf-8") as f:
        return json.load(f)

class RespetarBloqueosHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.handler = RespetarBloqueosHandler()
        # Cargar datos de prueba si están disponibles
        try:
            self.aulas = load_json("aulas.json")
        except FileNotFoundError:
            self.aulas = []

    # ========== TESTS DE VALIDACIÓN DIRECTA/GLOBAL (Compatibilidad) ==========

    def test_horario_sin_solapamiento_con_bloqueo_global(self):
        """
        Horario no solapa con bloqueo en el aula (validación global).
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
        self.assertIsNone(result)

    def test_horario_con_solapamiento_con_bloqueo_global(self):
        """
        Horario solapa con bloqueo en el aula (validación global).
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
        print(f"\nValidación global - con solapamiento: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("conflicto", result.lower())
        self.assertIn("AU001", result)
        self.assertIn("H1", result)

    def test_horarios_en_aulas_diferentes_global(self):
        """
        Bloqueo y horario están en aulas diferentes (validación global).
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
        self.assertIsNone(result)

    def test_varios_horarios_y_bloqueos_global(self):
        """
        Varios schedules y bloqueos, algunos solapan (validación global).
        Debe retornar mensaje de error por los que solapan.
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
        print(f"\nValidación global - múltiples conflictos: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("conflicto", result.lower())
        # Debería detectar conflictos en H1, H2 y H4
        self.assertTrue(any(horario in result for horario in ["H1", "H2", "H4"]))

    def test_horario_exactamente_antes_del_bloqueo_global(self):
        """
        Horario termina justo cuando inicia el bloqueo (validación global).
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
        self.assertIsNone(result)

    # ========== TESTS DE VALIDACIÓN INDIVIDUAL (Enfoque 2) ==========

    def test_validar_bloque_individual_sin_conflicto(self):
        """
        Validación individual: nuevo bloque sin conflicto con bloqueos.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "aula_id": "AU001",
                "hora_inicio": "08:00",
                "hora_fin": "10:00"
            },
            "bloqueos": [
                {"aula_id": "AU001", "horario": {"hora_inicio": "10:00", "hora_fin": "12:00"}},
                {"aula_id": "AU002", "horario": {"hora_inicio": "08:00", "hora_fin": "10:00"}}
            ]
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_validar_bloque_individual_con_conflicto(self):
        """
        Validación individual: nuevo bloque con conflicto con bloqueo.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "aula_id": "AU001",
                "hora_inicio": "09:00",
                "hora_fin": "11:00"
            },
            "bloqueos": [
                {"aula_id": "AU001", "horario": {"hora_inicio": "10:00", "hora_fin": "12:00"}}
            ]
        }
        result = self.handler.validate(context)
        print(f"\nValidación individual - con conflicto: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("conflicto", result.lower())
        self.assertIn("AU001", result)
        self.assertIn("H1", result)

    def test_validar_bloque_individual_aula_diferente(self):
        """
        Validación individual: nuevo bloque en aula diferente al bloqueo.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "aula_id": "AU002",
                "hora_inicio": "09:00",
                "hora_fin": "11:00"
            },
            "bloqueos": [
                {"aula_id": "AU001", "horario": {"hora_inicio": "09:00", "hora_fin": "11:00"}}
            ]
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_validar_bloque_individual_datos_faltantes(self):
        """
        Validación individual: nuevo bloque con datos faltantes.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "aula_id": "AU001"
                # Faltan hora_inicio y hora_fin
            },
            "bloqueos": [
                {"aula_id": "AU001", "horario": {"hora_inicio": "10:00", "hora_fin": "12:00"}}
            ]
        }
        result = self.handler.validate(context)
        self.assertIsInstance(result, str)
        self.assertIn("debe tener", result)

    def test_validar_bloque_individual_formato_mixto(self):
        """
        Validación individual: soporte para diferentes formatos de campos.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "aula": "AU001",  # Formato alternativo
                "start_time": "09:00",  # Formato alternativo
                "end_time": "11:00"  # Formato alternativo
            },
            "bloqueos": [
                {"aula": "AU001", "start_time": "10:00", "end_time": "12:00"}  # Bloqueo sin sub-horario
            ]
        }
        result = self.handler.validate(context)
        print(f"\nValidación individual - formato mixto: {result}")
        self.assertIsInstance(result, str)
        self.assertIn("conflicto", result.lower())

    # ========== TESTS DE CASOS EDGE ==========

    def test_bloque_exactamente_consecutivo_antes(self):
        """
        Bloque termina exactamente cuando inicia el bloqueo.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "aula_id": "AU001",
                "hora_inicio": "08:00",
                "hora_fin": "10:00"
            },
            "bloqueos": [
                {"aula_id": "AU001", "horario": {"hora_inicio": "10:00", "hora_fin": "12:00"}}
            ]
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_bloque_exactamente_consecutivo_despues(self):
        """
        Bloque inicia exactamente cuando termina el bloqueo.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "aula_id": "AU001",
                "hora_inicio": "12:00",
                "hora_fin": "14:00"
            },
            "bloqueos": [
                {"aula_id": "AU001", "horario": {"hora_inicio": "10:00", "hora_fin": "12:00"}}
            ]
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_bloque_traslape_parcial_inicio(self):
        """
        Bloque traslapa parcialmente al inicio del bloqueo.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "aula_id": "AU001",
                "hora_inicio": "09:30",
                "hora_fin": "10:30"
            },
            "bloqueos": [
                {"aula_id": "AU001", "horario": {"hora_inicio": "10:00", "hora_fin": "12:00"}}
            ]
        }
        result = self.handler.validate(context)
        self.assertIsInstance(result, str)
        self.assertIn("conflicto", result.lower())

    def test_bloque_traslape_parcial_final(self):
        """
        Bloque traslapa parcialmente al final del bloqueo.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "aula_id": "AU001",
                "hora_inicio": "11:30",
                "hora_fin": "12:30"
            },
            "bloqueos": [
                {"aula_id": "AU001", "horario": {"hora_inicio": "10:00", "hora_fin": "12:00"}}
            ]
        }
        result = self.handler.validate(context)
        self.assertIsInstance(result, str)
        self.assertIn("conflicto", result.lower())

    def test_bloque_completamente_contenido_en_bloqueo(self):
        """
        Bloque completamente contenido dentro del bloqueo.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "aula_id": "AU001",
                "hora_inicio": "10:30",
                "hora_fin": "11:30"
            },
            "bloqueos": [
                {"aula_id": "AU001", "horario": {"hora_inicio": "10:00", "hora_fin": "12:00"}}
            ]
        }
        result = self.handler.validate(context)
        self.assertIsInstance(result, str)
        self.assertIn("conflicto", result.lower())

    def test_bloque_contiene_completamente_bloqueo(self):
        """
        Bloque contiene completamente al bloqueo.
        """
        context = {
            "nuevo_bloque": {
                "id": "H1",
                "aula_id": "AU001",
                "hora_inicio": "09:00",
                "hora_fin": "13:00"
            },
            "bloqueos": [
                {"aula_id": "AU001", "horario": {"hora_inicio": "10:00", "hora_fin": "12:00"}}
            ]
        }
        result = self.handler.validate(context)
        self.assertIsInstance(result, str)
        self.assertIn("conflicto", result.lower())

    # ========== TESTS DE MÉTODOS AUXILIARES ==========

    def test_hay_bloqueo_true(self):
        """
        Test del método auxiliar hay_bloqueo (debería retornar True).
        """
        bloqueos = [
            {"aula_id": "AU001", "horario": {"hora_inicio": "10:00", "hora_fin": "12:00"}},
            {"aula_id": "AU002", "horario": {"hora_inicio": "14:00", "hora_fin": "16:00"}}
        ]

        # Debería haber bloqueo para AU001 de 09:30 a 10:30
        hay_bloqueo = self.handler.hay_bloqueo("AU001", "09:30", "10:30", bloqueos)
        self.assertTrue(hay_bloqueo)

    def test_hay_bloqueo_false(self):
        """
        Test del método auxiliar hay_bloqueo (debería retornar False).
        """
        bloqueos = [
            {"aula_id": "AU001", "horario": {"hora_inicio": "10:00", "hora_fin": "12:00"}},
            {"aula_id": "AU002", "horario": {"hora_inicio": "14:00", "hora_fin": "16:00"}}
        ]

        # NO debería haber bloqueo para AU001 de 08:00 a 10:00
        hay_bloqueo = self.handler.hay_bloqueo("AU001", "08:00", "10:00", bloqueos)
        self.assertFalse(hay_bloqueo)

    def test_hay_bloqueo_aula_diferente(self):
        """
        Test del método auxiliar hay_bloqueo con aula diferente.
        """
        bloqueos = [
            {"aula_id": "AU001", "horario": {"hora_inicio": "10:00", "hora_fin": "12:00"}}
        ]

        # NO debería haber bloqueo para AU003 (aula diferente)
        hay_bloqueo = self.handler.hay_bloqueo("AU003", "10:30", "11:30", bloqueos)
        self.assertFalse(hay_bloqueo)

    def test_obtener_bloqueos_conflictivos(self):
        """
        Test del método auxiliar obtener_bloqueos_conflictivos.
        """
        context = {
            "schedules": [
                {"id": "H1", "aula_id": "AU001", "hora_inicio": "09:00", "hora_fin": "11:00"},
                {"id": "H2", "aula_id": "AU001", "hora_inicio": "13:00", "hora_fin": "15:00"},
                {"id": "H3", "aula_id": "AU002", "hora_inicio": "10:00", "hora_fin": "12:00"}
            ],
            "bloqueos": [
                {"aula_id": "AU001", "horario": {"hora_inicio": "10:00", "hora_fin": "12:00"}},
                {"aula_id": "AU003", "horario": {"hora_inicio": "14:00", "hora_fin": "16:00"}}
            ]
        }

        conflictos = self.handler.obtener_bloqueos_conflictivos(context)
        print(f"\nConflictos encontrados: {len(conflictos)}")
        for conflicto in conflictos:
            print(f"- {conflicto['mensaje']}")

        self.assertIsInstance(conflictos, list)
        self.assertEqual(len(conflictos), 1)  # Solo H1 debería tener conflicto
        self.assertEqual(conflictos[0]["horario"]["id"], "H1")

    def test_sin_bloqueos(self):
        """
        Test con lista de bloqueos vacía.
        """
        context = {
            "schedules": [
                {"id": "H1", "aula": "AU001", "start_time": "09:00", "end_time": "11:00"}
            ],
            "bloqueos": []
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

    def test_sin_horarios(self):
        """
        Test con lista de horarios vacía.
        """
        context = {
            "schedules": [],
            "bloqueos": [
                {"aula": "AU001", "horario": {"start_time": "10:00", "end_time": "12:00"}}
            ]
        }
        result = self.handler.validate(context)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()