from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class HorarioBase(ABC):
    """
    Clase base abstracta para todos los tipos de horarios.
    Define la estructura común y métodos que deben implementar las subclases.
    """

    def __init__(self, docente: Dict = None, aula: Dict = None, asignatura: Dict = None,
                 start_time: str = "", end_time: str = "", dia: str = "", sede: Dict = None, **kwargs):
        # Parámetros obligatorios
        self.start_time = start_time
        self.end_time = end_time
        self.dia = dia

        # Parámetros opcionales (pueden ser None según el tipo de horario)
        self.docente = docente or {}
        self.aula = aula or {}
        self.asignatura = asignatura or {}
        self.sede = sede or {}

        # Parámetros adicionales
        self.id = kwargs.get('id', '')
        self.grupo = kwargs.get('grupo', {})
        self.modalidad = kwargs.get('modalidad', 'presencial')
        self.estado = kwargs.get('estado', 'activo')

        # Metadatos
        self.created_at = kwargs.get('created_at', '')
        self.updated_at = kwargs.get('updated_at', '')

    @abstractmethod
    def description(self) -> str:
        """
        Retorna una descripción textual del horario.
        Debe ser implementado por cada subclase.
        """
        pass

    @abstractmethod
    def get_tipo(self) -> str:
        """
        Retorna el tipo de horario.
        Debe ser implementado por cada subclase.
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el horario a un diccionario.
        Útil para serialización y APIs.
        """
        return {
            'id': self.id,
            'tipo': self.get_tipo(),
            'docente': self.docente,
            'aula': self.aula,
            'asignatura': self.asignatura,
            'sede': self.sede,
            'grupo': self.grupo,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'dia': self.dia,
            'modalidad': self.modalidad,
            'estado': self.estado,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def get_duracion_minutos(self) -> int:
        """
        Calcula la duración del horario en minutos.
        """
        try:
            start_parts = self.start_time.split(':')
            end_parts = self.end_time.split(':')

            start_minutes = int(start_parts[0]) * 60 + int(start_parts[1])
            end_minutes = int(end_parts[0]) * 60 + int(end_parts[1])

            return end_minutes - start_minutes
        except (ValueError, IndexError):
            return 0

    def es_valido(self) -> tuple:
        """
        Valida si el horario tiene los datos mínimos requeridos.

        :return: Tupla (es_valido: bool, mensaje_error: str)
        """
        if not self.start_time or not self.end_time or not self.dia:
            return False, "Faltan datos básicos: start_time, end_time o dia"

        if self.get_duracion_minutos() <= 0:
            return False, "La hora de fin debe ser posterior a la hora de inicio"

        return True, ""

    def __str__(self) -> str:
        return self.description()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self.id}', tipo='{self.get_tipo()}')"