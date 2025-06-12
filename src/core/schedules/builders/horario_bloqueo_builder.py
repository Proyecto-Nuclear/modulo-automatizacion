from typing import Dict, Any
from .horario_builder_base import HorarioBuilderBase
from ..horario_clase import HorarioBloqueo
from ..horario_base import HorarioBase

class HorarioBloqueoBuilder(HorarioBuilderBase):
    """
    Builder concreto para crear bloqueos de horario.
    """

    def validate_build_data(self) -> str | None:
        """
        Valida que todos los datos necesarios estén presentes para un bloqueo.
        Para bloqueos, docente NO es requerido.
        """
        required_fields = {
            'aula': self._aula,
            'asignatura': self._asignatura,
            'start_time': self._start_time,
            'end_time': self._end_time,
            'dia': self._dia,
            'sede': self._sede,
            'id': self._id
            # docente NO es requerido para bloqueos
        }
        missing_fields = [field for field, value in required_fields.items() if value is None]
        if missing_fields:
            return f"Faltan los siguientes campos requeridos: {missing_fields}"
        return None

    def build(self) -> HorarioBase:
        validation_error = self.validate_build_data()
        if validation_error:
            raise ValueError(f"Error en construcción de horario de bloqueo: {validation_error}")
        self._validate_bloqueo_requirements()
        try:
            horario = HorarioBloqueo(
                docente=None,  # No hay docente en un bloqueo
                aula=self._aula,
                asignatura=self._asignatura,
                start_time=self._start_time,
                end_time=self._end_time,
                dia=self._dia,
                sede=self._sede
            )
            return horario
        except Exception as e:
            raise ValueError(f"Error al construir horario de bloqueo: {str(e)}")

    def _validate_bloqueo_requirements(self) -> None:
        # El aula y la sede deben estar presentes
        if self._aula is None:
            raise ValueError("Debe especificar un aula para el bloqueo")
        if self._sede is None:
            raise ValueError("Debe especificar una sede para el bloqueo")
        # La asignatura debe ser de tipo 'bloqueo'
        if self._asignatura.get('tipo', '').lower() != 'bloqueo':
            raise ValueError("La asignatura debe ser de tipo 'bloqueo' para un horario de bloqueo")
        # Duración mínima y máxima
        start_hour, start_min = map(int, self._start_time.split(':'))
        end_hour, end_min = map(int, self._end_time.split(':'))
        duration_minutes = (end_hour * 60 + end_min) - (start_hour * 60 + start_min)
        if duration_minutes < 15:
            raise ValueError("El bloqueo debe durar al menos 15 minutos")
        if duration_minutes > 480:
            raise ValueError("El bloqueo no puede durar más de 8 horas")

    def get_tipo(self) -> str:
        return 'bloqueo'