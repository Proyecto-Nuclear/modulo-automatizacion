from typing import Dict, Any
from .horario_builder_base import HorarioBuilderBase
from ..horario_clase import HorarioVirtual
from ..horario_base import HorarioBase

class HorarioVirtualBuilder(HorarioBuilderBase):
    """
    Builder concreto para crear horarios virtuales.
    """

    def validate_build_data(self) -> str | None:
        """
        Valida que todos los datos necesarios estén presentes para una clase virtual.
        Para clases virtuales, aula y sede NO son requeridos.
        """
        required_fields = {
            'docente': self._docente,
            'asignatura': self._asignatura,
            'start_time': self._start_time,
            'end_time': self._end_time,
            'dia': self._dia,
            'id': self._id
            # aula y sede NO son requeridos para virtuales
        }
        missing_fields = [field for field, value in required_fields.items() if value is None]
        if missing_fields:
            return f"Faltan los siguientes campos requeridos: {missing_fields}"
        return None

    def build(self) -> HorarioBase:
        validation_error = self.validate_build_data()
        if validation_error:
            raise ValueError(f"Error en construcción de horario virtual: {validation_error}")
        self._validate_virtual_requirements()
        try:
            horario = HorarioVirtual(
                docente=self._docente,
                aula=None,  # No hay aula física
                asignatura=self._asignatura,
                start_time=self._start_time,
                end_time=self._end_time,
                dia=self._dia,
                sede=None  # No hay sede física
            )
            return horario
        except Exception as e:
            raise ValueError(f"Error al construir horario virtual: {str(e)}")

    def _validate_virtual_requirements(self) -> None:
        # No se requiere aula ni sede, pero sí docente y asignatura
        if self._aula is not None:
            raise ValueError("No debe asignarse aula en un horario virtual")
        if self._sede is not None:
            raise ValueError("No debe asignarse sede en un horario virtual")
        # Duración mínima y máxima
        start_hour, start_min = map(int, self._start_time.split(':'))
        end_hour, end_min = map(int, self._end_time.split(':'))
        duration_minutes = (end_hour * 60 + end_min) - (start_hour * 60 + start_min)
        if duration_minutes < 30:
            raise ValueError("Las clases virtuales deben durar al menos 30 minutos")
        if duration_minutes > 180:
            raise ValueError("Las clases virtuales no pueden durar más de 3 horas")

    def get_tipo(self) -> str:
        return 'virtual'