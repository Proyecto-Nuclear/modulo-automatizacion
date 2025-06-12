from abc import abstractmethod, ABC
from typing import Optional

from src.core.schedules.horario_base import HorarioBase


class HorarioFactory(ABC):
    """
    Factory abstracto para crear diferentes tipos de horarios.
    Implementa el patrón Factory Method.
    """

    @abstractmethod
    def crear_horario(self, **kwargs) -> 'HorarioBase':
        """
        Crea un horario específico según el tipo de factory.

        :param kwargs: Parámetros necesarios para crear el horario
        :return: Instancia de HorarioBase
        """
        pass

    def validar_parametros_basicos(self, **kwargs) -> Optional[str]:
        """
        Valida que los parámetros básicos estén presentes.

        :param kwargs: Parámetros a validar
        :return: None si es válido, mensaje de error si no
        """
        required_params = ['start_time', 'end_time', 'dia']
        missing = [param for param in required_params if not kwargs.get(param)]

        if missing:
            return f"Parámetros faltantes: {', '.join(missing)}"
        return None

    def crear_horario_con_validacion(self, **kwargs) -> tuple:
        """
        Crea un horario con validación previa.

        :param kwargs: Parámetros para crear el horario
        :return: Tupla (horario_creado, mensaje_error)
        """
        error = self.validar_parametros_basicos(**kwargs)
        if error:
            return None, error

        try:
            horario = self.crear_horario(**kwargs)
            return horario, None
        except Exception as e:
            return None, f"Error al crear horario: {str(e)}"