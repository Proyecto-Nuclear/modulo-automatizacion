from abc import ABC, abstractmethod

class HorarioBase(ABC):
    def __init__(self, docente, aula, asignatura, start_time, end_time, dia, sede):
        self.docente = docente
        self.aula = aula
        self.asignatura = asignatura
        self.start_time = start_time
        self.end_time = end_time
        self.dia = dia
        self.sede = sede

    @abstractmethod
    def description(self):
        pass