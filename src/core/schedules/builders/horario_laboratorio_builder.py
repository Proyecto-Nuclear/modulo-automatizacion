from .horario_builder_base import HorarioBuilderBase
from ..horario_clase import HorarioLaboratorio
from ..horario_base import HorarioBase

class HorarioLaboratorioBuilder(HorarioBuilderBase):
    """
    Builder concreto para crear horarios de laboratorio.
    """

    def validate_build_data(self) -> str | None:
        """
        Valida que todos los datos necesarios estén presentes para un laboratorio.
        Para laboratorios, todos los campos son requeridos.
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
            raise ValueError(f"Error en construcción de horario laboratorio: {validation_error}")
        self._validate_laboratorio_requirements()
        try:
            horario = HorarioLaboratorio(
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
            raise ValueError(f"Error al construir horario laboratorio: {str(e)}")

    def _validate_laboratorio_requirements(self) -> None:
        # El aula debe ser de tipo laboratorio
        aula_tipo = self._aula.get('tipo', '').lower()
        if aula_tipo != 'laboratorio':
            raise ValueError("El aula debe ser de tipo 'laboratorio' para un horario de laboratorio")
        # La asignatura debe permitir laboratorio
        if not self._asignatura.get('permite_laboratorio', True):
            raise ValueError("La asignatura no permite laboratorios")
        # Duración mínima y máxima
        start_hour, start_min = map(int, self._start_time.split(':'))
        end_hour, end_min = map(int, self._end_time.split(':'))
        duration_minutes = (end_hour * 60 + end_min) - (start_hour * 60 + start_min)
        if duration_minutes < 60:
            raise ValueError("Los laboratorios deben durar al menos 60 minutos")
        if duration_minutes > 240:
            raise ValueError("Los laboratorios no pueden durar más de 4 horas")

    def get_tipo(self) -> str:
        return 'laboratorio'