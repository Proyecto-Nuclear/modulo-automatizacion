from abc import abstractmethod, ABC


class HorarioFactory(ABC):
    @abstractmethod
    def crear_horario(self, **kwargs):
        pass