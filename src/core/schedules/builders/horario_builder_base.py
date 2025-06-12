import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from .horario_builder_interface import IHorarioBuilder
from ..horario_base import HorarioBase


class HorarioBuilderBase(IHorarioBuilder, ABC):
    """
    Clase base abstracta que implementa funcionalidad común para todos los builders.
    """

    def __init__(self):
        """Inicializa el builder con valores por defecto."""
        self._metadatos = None
        self._id = None
        self._sede = None
        self._dia = None
        self._end_time = None
        self._start_time = None
        self._asignatura = None
        self._aula = None
        self._docente = None
        self.reset()

    def reset(self) -> 'HorarioBuilderBase':
        """
        Reinicia todos los campos del builder.

        :return: Self para method chaining
        """
        self._docente: Optional[Dict[str, Any]] = None
        self._aula: Optional[Dict[str, Any]] = None
        self._asignatura: Optional[Dict[str, Any]] = None
        self._start_time: Optional[str] = None
        self._end_time: Optional[str] = None
        self._dia: Optional[str] = None
        self._sede: Optional[Dict[str, Any]] = None
        self._id: Optional[str] = None
        self._metadatos: Dict[str, Any] = {}
        return self

    def set_docente(self, docente: Dict[str, Any]) -> 'HorarioBuilderBase':
        """
        Establece el docente con validación básica.

        :param docente: Diccionario con información del docente
        :return: Self para method chaining
        :raises ValueError: Si el docente no tiene los campos requeridos
        """
        if not isinstance(docente, dict):
            raise ValueError("El docente debe ser un diccionario")

        required_fields = ['id', 'nombre']
        missing_fields = [field for field in required_fields if field not in docente]
        if missing_fields:
            raise ValueError(f"El docente debe tener los campos: {missing_fields}")

        self._docente = docente.copy()
        return self

    def set_aula(self, aula: Dict[str, Any]) -> 'HorarioBuilderBase':
        """
        Establece el aula con validación básica.

        :param aula: Diccionario con información del aula
        :return: Self para method chaining
        :raises ValueError: Si el aula no tiene los campos requeridos
        """
        if not isinstance(aula, dict):
            raise ValueError("El aula debe ser un diccionario")

        required_fields = ['id', 'nombre']
        missing_fields = [field for field in required_fields if field not in aula]
        if missing_fields:
            raise ValueError(f"El aula debe tener los campos: {missing_fields}")

        self._aula = aula.copy()
        return self

    def set_asignatura(self, asignatura: Dict[str, Any]) -> 'HorarioBuilderBase':
        """
        Establece la asignatura con validación básica.

        :param asignatura: Diccionario con información de la asignatura
        :return: Self para method chaining
        :raises ValueError: Si la asignatura no tiene los campos requeridos
        """
        if not isinstance(asignatura, dict):
            raise ValueError("La asignatura debe ser un diccionario")

        required_fields = ['id', 'nombre']
        missing_fields = [field for field in required_fields if field not in asignatura]
        if missing_fields:
            raise ValueError(f"La asignatura debe tener los campos: {missing_fields}")

        self._asignatura = asignatura.copy()
        return self

    def set_tiempo(self, start_time: str, end_time: str) -> 'HorarioBuilderBase':
        """
        Establece los tiempos con validación de formato.

        :param start_time: Hora de inicio (formato HH:MM)
        :param end_time: Hora de fin (formato HH:MM)
        :return: Self para method chaining
        :raises ValueError: Si el formato de tiempo es inválido
        """
        if not self._is_valid_time_format(start_time):
            raise ValueError(f"Formato de hora de inicio inválido: {start_time}. Use HH:MM")

        if not self._is_valid_time_format(end_time):
            raise ValueError(f"Formato de hora de fin inválido: {end_time}. Use HH:MM")

        if start_time >= end_time:
            raise ValueError("La hora de inicio debe ser anterior a la hora de fin")

        self._start_time = start_time
        self._end_time = end_time
        return self

    def set_dia(self, dia: str) -> 'HorarioBuilderBase':
        """
        Establece el día con validación.

        :param dia: Día de la semana
        :return: Self para method chaining
        :raises ValueError: Si el día no es válido
        """
        dias_validos = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

        if dia not in dias_validos:
            raise ValueError(f"Día inválido: {dia}. Días válidos: {dias_validos}")

        self._dia = dia
        return self

    def set_sede(self, sede: Dict[str, Any]) -> 'HorarioBuilderBase':
        """
        Establece la sede con validación básica.

        :param sede: Diccionario con información de la sede
        :return: Self para method chaining
        :raises ValueError: Si la sede no tiene los campos requeridos
        """
        if not isinstance(sede, dict):
            raise ValueError("La sede debe ser un diccionario")

        required_fields = ['id', 'nombre']
        missing_fields = [field for field in required_fields if field not in sede]
        if missing_fields:
            raise ValueError(f"La sede debe tener los campos: {missing_fields}")

        self._sede = sede.copy()
        return self

    def set_id(self, horario_id: str) -> 'HorarioBuilderBase':
        """
        Establece el ID del horario.

        :param horario_id: Identificador único del horario
        :return: Self para method chaining
        :raises ValueError: Si el ID es inválido
        """
        if not horario_id or not isinstance(horario_id, str):
            raise ValueError("El ID del horario debe ser una cadena no vacía")

        self._id = horario_id
        return self

    def set_metadatos(self, **metadatos) -> 'HorarioBuilderBase':
        """
        Establece metadatos adicionales.

        :param metadatos: Metadatos adicionales
        :return: Self para method chaining
        """
        # Agregar timestamp si no existe
        if 'created_at' not in metadatos:
            metadatos['created_at'] = datetime.now().isoformat()

        # Agregar estado por defecto si no existe
        if 'estado' not in metadatos:
            metadatos['estado'] = 'tentativo'

        self._metadatos.update(metadatos)
        return self

    def validate_build_data(self) -> Optional[str]:
        """
        Valida que todos los datos requeridos estén presentes.

        :return: None si es válido, mensaje de error si no es válido
        """
        required_fields = {
            'docente': self._docente,
            'aula': self._aula,
            'asignatura': self._asignatura,
            'start_time': self._start_time,
            'end_time': self._end_time,
            'dia': self._dia,
            'sede': self._sede,
            'id': self._id
        }

        missing_fields = [field for field, value in required_fields.items() if value is None]

        if missing_fields:
            return f"Faltan los siguientes campos requeridos: {missing_fields}"

        return None

    def _is_valid_time_format(self, time: str) -> bool:
        """
        Valida si el formato de tiempo es HH:MM.
        """
        pattern = re.compile(r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$")
        return bool(pattern.match(time))

    def _get_build_data(self) -> Dict[str, Any]:
        """
        Retorna todos los datos de construcción en un diccionario.

        :return: Diccionario con todos los datos
        """
        data = {
            'docente': self._docente,
            'aula': self._aula,
            'asignatura': self._asignatura,
            'start_time': self._start_time,
            'end_time': self._end_time,
            'dia': self._dia,
            'sede': self._sede,
            'id': self._id
        }

        # Agregar metadatos
        data.update(self._metadatos)

        return data

    @abstractmethod
    def build(self) -> HorarioBase:
        """
        Método abstracto que debe ser implementado por las subclases.

        :return: Instancia del horario construido
        """
        pass

    @abstractmethod
    def get_tipo(self) -> str:
        """
        Método abstracto que debe ser implementado por las subclases.

        :return: Tipo de horario
        """
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(tipo={self.get_tipo()})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(docente={self._docente}, aula={self._aula})"