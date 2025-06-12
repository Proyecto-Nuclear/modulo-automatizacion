from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..horario_base import HorarioBase


class IHorarioBuilder(ABC):
    """
    Interfaz que define los métodos para construir horarios.
    """

    @abstractmethod
    def reset(self) -> 'IHorarioBuilder':
        """
        Reinicia el builder para construir un nuevo horario.

        :return: Self para permitir method chaining
        """
        pass

    @abstractmethod
    def set_docente(self, docente: Dict[str, Any]) -> 'IHorarioBuilder':
        """
        Establece el docente del horario.

        :param docente: Diccionario con información del docente
        :return: Self para permitir method chaining
        """
        pass

    @abstractmethod
    def set_aula(self, aula: Dict[str, Any]) -> 'IHorarioBuilder':
        """
        Establece el aula del horario.

        :param aula: Diccionario con información del aula
        :return: Self para permitir method chaining
        """
        pass

    @abstractmethod
    def set_asignatura(self, asignatura: Dict[str, Any]) -> 'IHorarioBuilder':
        """
        Establece la asignatura del horario.

        :param asignatura: Diccionario con información de la asignatura
        :return: Self para permitir method chaining
        """
        pass

    @abstractmethod
    def set_tiempo(self, start_time: str, end_time: str) -> 'IHorarioBuilder':
        """
        Establece los tiempos de inicio y fin del horario.

        :param start_time: Hora de inicio (formato HH:MM)
        :param end_time: Hora de fin (formato HH:MM)
        :return: Self para permitir method chaining
        """
        pass

    @abstractmethod
    def set_dia(self, dia: str) -> 'IHorarioBuilder':
        """
        Establece el día de la semana del horario.

        :param dia: Día de la semana
        :return: Self para permitir method chaining
        """
        pass

    @abstractmethod
    def set_sede(self, sede: Dict[str, Any]) -> 'IHorarioBuilder':
        """
        Establece la sede del horario.

        :param sede: Diccionario con información de la sede
        :return: Self para permitir method chaining
        """
        pass

    @abstractmethod
    def set_id(self, horario_id: str) -> 'IHorarioBuilder':
        """
        Establece el ID del horario.

        :param horario_id: Identificador único del horario
        :return: Self para permitir method chaining
        """
        pass

    @abstractmethod
    def set_metadatos(self, **metadatos) -> 'IHorarioBuilder':
        """
        Establece metadatos adicionales del horario.

        :param metadatos: Metadatos adicionales como created_at, estado, etc.
        :return: Self para permitir method chaining
        """
        pass

    @abstractmethod
    def build(self) -> HorarioBase:
        """
        Construye y retorna el horario final.

        :return: Instancia del horario construido
        :raises ValueError: Si faltan datos requeridos para la construcción
        """
        pass

    @abstractmethod
    def validate_build_data(self) -> Optional[str]:
        """
        Valida que todos los datos requeridos estén presentes para la construcción.

        :return: None si es válido, mensaje de error si no es válido
        """
        pass

    @abstractmethod
    def get_tipo(self) -> str:
        """
        Retorna el tipo de horario que construye este builder.

        :return: Tipo de horario (ej: 'normal', 'laboratorio', 'virtual', 'bloqueo')
        """
        pass