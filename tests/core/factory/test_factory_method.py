import os
import unittest
import json

from src.core.horarios.selector_factory import get_horario_factory

def load_json(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, '../../../data'))
    with open(os.path.join(data_dir, filename), encoding="utf-8") as f:
        return json.load(f)

class FactoryMethodTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.asignaturas = load_json("asignaturas.json")
        cls.aulas = load_json("aulas.json")
        cls.docentes = load_json("docentes.json")
        cls.sedes = load_json("sedes.json")

    def test_factory_clase_normal(self):
        kwargs = {
            "docente": self.docentes[0],
            "aula": self.aulas[0],
            "asignatura": self.asignaturas[0],
            "start_time": "08:00",
            "end_time": "10:00",
            "dia": "Lunes",
            "sede": self.sedes[0]
        }
        factory = get_horario_factory("normal")
        horario = factory.crear_horario(**kwargs)
        print(f"\n{horario.description()}")
        self.assertIn("Álgebra Lineal", horario.description())
        self.assertIn("Aula 101", horario.description())
        self.assertIn("Laura", horario.description())

    def test_factory_clase_laboratorio(self):
        kwargs = {
            "docente": self.docentes[0],
            "aula": self.aulas[0],
            "asignatura": self.asignaturas[0],
            "start_time": "08:00",
            "end_time": "10:00",
            "dia": "Lunes",
            "sede": self.sedes[0]
        }
        factory = get_horario_factory("laboratorio")
        horario = factory.crear_horario(**kwargs)
        print(f"\n{horario.description()}")
        self.assertIn("Álgebra Lineal", horario.description())
        self.assertIn("Aula 101", horario.description())
        self.assertIn("Laura", horario.description())

    def test_factory_clase_virtual(self):
        kwargs = {
            "docente": self.docentes[0],
            "aula": self.aulas[0],
            "asignatura": self.asignaturas[0],
            "start_time": "08:00",
            "end_time": "10:00",
            "dia": "Lunes",
            "sede": self.sedes[0]
        }
        factory = get_horario_factory("virtual")
        horario = factory.crear_horario(**kwargs)
        print(f"\n{horario.description()}")
        self.assertIn("Álgebra Lineal", horario.description())
        self.assertIn("Laura", horario.description())

    def test_factory_clase_bloqueo(self):
        kwargs = {
            "docente": self.docentes[0],
            "aula": self.aulas[0],
            "asignatura": self.asignaturas[0],
            "start_time": "08:00",
            "end_time": "10:00",
            "dia": "Lunes",
            "sede": self.sedes[0]
        }
        factory = get_horario_factory("bloqueo")
        horario = factory.crear_horario(**kwargs)
        print(f"\n{horario.description()}")
        self.assertIn("Álgebra Lineal", horario.description())
        self.assertIn("Aula 101", horario.description())

if __name__ == '__main__':
    unittest.main()