from .horario_clase import HorarioClaseNormal, HorarioLaboratorio, HorarioVirtual, HorarioBloqueo
from .horario_factory import HorarioFactory

class FactoryClaseNormal(HorarioFactory):
    """
    Factory para crear horarios de clases normales.
    """

    def crear_horario(self, **kwargs) -> HorarioClaseNormal:
        return HorarioClaseNormal(**kwargs)

    def validar_parametros_basicos(self, **kwargs) -> str | None:
        """
        Validación específica para clases normales.
        """
        error_base = super().validar_parametros_basicos(**kwargs)
        if error_base:
            return error_base

        required_for_normal = ['docente', 'aula', 'asignatura']
        missing = [param for param in required_for_normal if not kwargs.get(param)]

        if missing:
            return f"Clase normal requiere: {', '.join(missing)}"

        return None


class FactoryLaboratorio(HorarioFactory):
    """
    Factory para crear horarios de laboratorio.
    """

    def crear_horario(self, **kwargs) -> HorarioLaboratorio:
        return HorarioLaboratorio(**kwargs)

    def validar_parametros_basicos(self, **kwargs) -> str | None:
        """
        Validación específica para laboratorios.
        """
        error_base = super().validar_parametros_basicos(**kwargs)
        if error_base:
            return error_base

        required_for_lab = ['docente', 'aula', 'asignatura']
        missing = [param for param in required_for_lab if not kwargs.get(param)]

        if missing:
            return f"Laboratorio requiere: {', '.join(missing)}"

        # Validar que el aula sea de tipo laboratorio
        aula = kwargs.get('aula', {})
        if aula.get('tipo', '').lower() not in ['laboratorio', 'lab']:
            return "Laboratorio requiere un aula de tipo 'laboratorio'"

        return None


class FactoryVirtual(HorarioFactory):
    """
    Factory para crear horarios de clases virtuales.
    """

    def crear_horario(self, **kwargs) -> HorarioVirtual:
        return HorarioVirtual(**kwargs)

    def validar_parametros_basicos(self, **kwargs) -> str | None:
        """
        Validación específica para clases virtuales.
        """
        error_base = super().validar_parametros_basicos(**kwargs)
        if error_base:
            return error_base

        required_for_virtual = ['docente', 'asignatura']
        missing = [param for param in required_for_virtual if not kwargs.get(param)]

        if missing:
            return f"Clase virtual requiere: {', '.join(missing)}"

        # Las clases virtuales NO deben tener aula
        if kwargs.get('aula', {}).get('id'):
            return "Clase virtual no debe tener aula física asignada"

        return None


class FactoryBloqueo(HorarioFactory):
    """
    Factory para crear bloqueos de horario.
    """

    def crear_horario(self, **kwargs) -> HorarioBloqueo:
        return HorarioBloqueo(**kwargs)

    def validar_parametros_basicos(self, **kwargs) -> str | None:
        """
        Validación específica para bloqueos.
        """
        error_base = super().validar_parametros_basicos(**kwargs)
        if error_base:
            return error_base

        required_for_bloqueo = ['aula']
        missing = [param for param in required_for_bloqueo if not kwargs.get(param)]

        if missing:
            return f"Bloqueo requiere: {', '.join(missing)}"

        # Los bloqueos NO deben tener docente ni asignatura
        if kwargs.get('docente', {}).get('id'):
            return "Bloqueo no debe tener docente asignado"

        if kwargs.get('asignatura', {}).get('id'):
            return "Bloqueo no debe tener asignatura asignada"

        return None