from typing import Dict, Type, List

from .horario_bloqueo_builder import HorarioBloqueoBuilder
from .horario_builder_interface import IHorarioBuilder
from .horario_laboratorio_builder import HorarioLaboratorioBuilder
from .horario_normal_builder import HorarioNormalBuilder
from .horario_virtual_builder import HorarioVirtualBuilder


class BuilderFactory:
    """
    Factory para crear builders de horarios.
    """

    # Registro de builders disponibles
    _builders: Dict[str, Type[IHorarioBuilder]] = {
        'normal': HorarioNormalBuilder,
        'laboratorio': HorarioLaboratorioBuilder,
        'virtual': HorarioVirtualBuilder,
        'bloqueo': HorarioBloqueoBuilder
    }

    @classmethod
    def create_builder(cls, tipo: str) -> IHorarioBuilder:
        """
        Crea un builder del tipo especificado.

        :param tipo: Tipo de builder a crear
        :return: Instancia del builder
        :raises ValueError: Si el tipo no está registrado
        """
        if tipo not in cls._builders:
            available_types = list(cls._builders.keys())
            raise ValueError(f"Tipo de builder '{tipo}' no disponible. "
                             f"Tipos disponibles: {available_types}")

        builder_class = cls._builders[tipo]
        return builder_class()

    @classmethod
    def register_builder(cls, tipo: str, builder_class: Type[IHorarioBuilder]) -> None:
        """
        Registra un nuevo tipo de builder.

        :param tipo: Nombre del tipo de builder
        :param builder_class: Clase del builder
        :raises ValueError: Si el builder no implementa la interfaz correcta
        """
        if not issubclass(builder_class, IHorarioBuilder):
            raise ValueError(f"La clase {builder_class.__name__} debe implementar IHorarioBuilder")

        cls._builders[tipo] = builder_class

    @classmethod
    def get_available_types(cls) -> List[str]:
        """
        Retorna los tipos de builders disponibles.

        :return: Lista de tipos disponibles
        """
        return list(cls._builders.keys())

    @classmethod
    def is_type_available(cls, tipo: str) -> bool:
        """
        Verifica si un tipo de builder está disponible.

        :param tipo: Tipo a verificar
        :return: True si está disponible, False si no
        """
        return tipo in cls._builders