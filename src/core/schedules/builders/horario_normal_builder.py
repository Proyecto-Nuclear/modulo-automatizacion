from typing import Dict, Any
from .horario_builder_base import HorarioBuilderBase
from ..horario_clase import HorarioClaseNormal
from ..horario_base import HorarioBase

class HorarioNormalBuilder(HorarioBuilderBase):
    """
    Builder concreto para crear horarios de clases normales.
    """

    def validate_build_data(self) -> str | None:
        """
        Valida que todos los datos necesarios estén presentes para una clase normal.
        Para clases normales, todos los campos son requeridos.
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

    def build(self) -> HorarioBase:
        validation_error = self.validate_build_data()
        if validation_error:
            raise ValueError(f"Error en construcción de horario normal: {validation_error}")
        self._validate_normal_requirements()
        try:
            horario = HorarioClaseNormal(
                docente=self._docente,
                aula=self._aula,
                asignatura=self._asignatura,
                start_time=self._start_time,
                end_time=self._end_time,
                dia=self._dia,
                sede=self._sede
            )
            return horario
        except Exception as e:
            raise ValueError(f"Error al construir horario normal: {str(e)}")

    def _validate_normal_requirements(self) -> None:
        # El aula debe ser de tipo aula o teorica
        aula_tipo = self._aula.get('tipo', '').lower()
        if aula_tipo not in ['aula', 'teorica']:
            raise ValueError("El aula debe ser de tipo 'aula' o 'teorica' para una clase normal")
        # La asignatura no debe ser solo de laboratorio
        if self._asignatura.get('solo_laboratorio', False):
            raise ValueError("Esta asignatura solo permite laboratorios")
        # Duración mínima y máxima
        start_hour, start_min = map(int, self._start_time.split(':'))
        end_hour, end_min = map(int, self._end_time.split(':'))
        duration_minutes = (end_hour * 60 + end_min) - (start_hour * 60 + start_min)
        if duration_minutes < 50:
            raise ValueError("Las clases normales deben durar al menos 50 minutos")
        if duration_minutes > 180:
            raise ValueError("Las clases normales no pueden durar más de 3 horas")

    def set_recursos_especiales(self, recursos: Dict[str, Any]) -> 'HorarioNormalBuilder':
        """
        Establece recursos especiales necesarios para la clase.

        :param recursos: Diccionario con recursos especiales
        :return: Self para method chaining
        """
        if not isinstance(recursos, dict):
            raise ValueError("Los recursos especiales deben ser un diccionario")
        self._metadatos['recursos_especiales'] = recursos
        return self

    def set_modalidad_hibrida(self, es_hibrida: bool) -> 'HorarioNormalBuilder':
        """
        Establece si la clase es de modalidad híbrida.

        :param es_hibrida: True si es híbrida, False si no
        :return: Self para method chaining
        """
        self._metadatos['modalidad_hibrida'] = es_hibrida
        return self

    def get_tipo(self) -> str:
        return 'normal'