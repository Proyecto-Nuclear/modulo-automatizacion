from .horario_clase import HorarioClaseNormal, HorarioLaboratorio, HorarioVirtual, HorarioBloqueo
from .horario_factory import HorarioFactory

class FactoryClaseNormal(HorarioFactory):
    def crear_horario(self, **kwargs):
        return HorarioClaseNormal(**kwargs)

class FactoryLaboratorio(HorarioFactory):
    def crear_horario(self, **kwargs):
        return HorarioLaboratorio(**kwargs)

class FactoryVirtual(HorarioFactory):
    def crear_horario(self, **kwargs):
        return HorarioVirtual(**kwargs)

class FactoryBloqueo(HorarioFactory):
    def crear_horario(self, **kwargs):
        return HorarioBloqueo(**kwargs)