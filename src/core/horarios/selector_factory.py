from .factories import FactoryClaseNormal, FactoryLaboratorio, FactoryVirtual, FactoryBloqueo

def get_horario_factory(tipo: str):
    factories = {
        "normal": FactoryClaseNormal(),
        "laboratorio": FactoryLaboratorio(),
        "virtual": FactoryVirtual(),
        "bloqueo": FactoryBloqueo()
    }
    return factories[tipo]