from .factories import FactoryClaseNormal, FactoryLaboratorio, FactoryVirtual, FactoryBloqueo
from .horario_factory import HorarioFactory
from typing import Optional, Dict, Any

class SelectorFactory:
    """
    Selector de factories para diferentes tipos de horarios.
    Implementa el patrón Abstract Factory.
    """

    _factories = {
        "normal": FactoryClaseNormal,
        "clase_normal": FactoryClaseNormal,
        "presencial": FactoryClaseNormal,

        "laboratorio": FactoryLaboratorio,
        "lab": FactoryLaboratorio,

        "virtual": FactoryVirtual,
        "online": FactoryVirtual,
        "remoto": FactoryVirtual,

        "bloqueo": FactoryBloqueo,
        "bloqueado": FactoryBloqueo,
        "mantenimiento": FactoryBloqueo
    }

    @classmethod
    def get_horario_factory(cls, tipo: str) -> Optional[HorarioFactory]:
        """
        Obtiene el factory apropiado según el tipo de horario.

        :param tipo: Tipo de horario solicitado
        :return: Factory correspondiente o None si no existe
        """
        tipo_normalizado = tipo.lower().strip()
        factory_class = cls._factories.get(tipo_normalizado)

        if factory_class:
            return factory_class()

        return None

    @classmethod
    def crear_horario(cls, tipo: str, **kwargs) -> tuple:
        """
        Crea un horario directamente usando el factory apropiado.

        :param tipo: Tipo de horario a crear
        :param kwargs: Parámetros para crear el horario
        :return: Tupla (horario_creado, mensaje_error)
        """
        factory = cls.get_horario_factory(tipo)

        if not factory:
            return None, f"Tipo de horario '{tipo}' no soportado"

        return factory.crear_horario_con_validacion(**kwargs)

    @classmethod
    def get_tipos_disponibles(cls) -> list:
        """
        Retorna la lista de tipos de horarios disponibles.
        """
        return list(cls._factories.keys())

    @classmethod
    def es_tipo_valido(cls, tipo: str) -> bool:
        """
        Verifica si un tipo de horario es válido.
        """
        return tipo.lower().strip() in cls._factories


# Función de compatibilidad con el código existente
def get_horario_factory(tipo: str) -> Optional[HorarioFactory]:
    """
    Función de compatibilidad para obtener un factory.

    :param tipo: Tipo de horario
    :return: Factory correspondiente o None
    """
    return SelectorFactory.get_horario_factory(tipo)