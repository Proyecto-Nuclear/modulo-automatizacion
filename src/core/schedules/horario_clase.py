from .horario_base import HorarioBase
from typing import Dict, Any

class HorarioClaseNormal(HorarioBase):
    """
    Representa una clase normal presencial.
    """

    def get_tipo(self) -> str:
        return "normal"

    def description(self) -> str:
        docente_nombre = self._get_nombre_completo(self.docente)
        asignatura_nombre = self.asignatura.get('nombre', 'Sin asignatura')
        aula_nombre = self.aula.get('nombre', 'Sin aula')
        sede_nombre = self.sede.get('nombre', 'Sin sede')

        return (f"Clase normal de {asignatura_nombre} en {aula_nombre} "
                f"dictada por {docente_nombre} de {self.start_time} a {self.end_time} "
                f"en {sede_nombre} el {self.dia}")

    def es_valido(self) -> tuple:
        """
        Validación específica para clases normales.
        """
        es_valido_base, mensaje_base = super().es_valido()
        if not es_valido_base:
            return False, mensaje_base

        # Validaciones específicas para clase normal
        if not self.docente.get('id'):
            return False, "Clase normal requiere un docente asignado"

        if not self.aula.get('id'):
            return False, "Clase normal requiere un aula asignada"

        if not self.asignatura.get('id'):
            return False, "Clase normal requiere una asignatura asignada"

        return True, ""

    def _get_nombre_completo(self, docente: Dict) -> str:
        """Método auxiliar para obtener el nombre completo del docente."""
        if not docente:
            return "Sin docente"

        nombre = docente.get('nombre', '')
        apellido = docente.get('apellido', '')

        if nombre and apellido:
            return f"{nombre} {apellido}"
        elif nombre:
            return nombre
        elif apellido:
            return apellido
        else:
            return "Sin nombre"


class HorarioLaboratorio(HorarioBase):
    """
    Representa una clase de laboratorio.
    """

    def get_tipo(self) -> str:
        return "laboratorio"

    def description(self) -> str:
        docente_nombre = self._get_nombre_completo(self.docente)
        asignatura_nombre = self.asignatura.get('nombre', 'Sin asignatura')
        aula_nombre = self.aula.get('nombre', 'Sin laboratorio')
        sede_nombre = self.sede.get('nombre', 'Sin sede')

        return (f"Laboratorio de {asignatura_nombre} en {aula_nombre} "
                f"dictado por {docente_nombre} de {self.start_time} a {self.end_time} "
                f"en {sede_nombre} el {self.dia}")

    def es_valido(self) -> tuple:
        """
        Validación específica para laboratorios.
        """
        es_valido_base, mensaje_base = super().es_valido()
        if not es_valido_base:
            return False, mensaje_base

        # Validaciones específicas para laboratorio
        if not self.docente.get('id'):
            return False, "Laboratorio requiere un docente asignado"

        if not self.aula.get('id'):
            return False, "Laboratorio requiere un aula/laboratorio asignado"

        if not self.asignatura.get('id'):
            return False, "Laboratorio requiere una asignatura asignada"

        # Validación específica: el aula debe ser de tipo laboratorio
        if self.aula.get('tipo', '').lower() not in ['laboratorio', 'lab']:
            return False, "El aula asignada debe ser de tipo laboratorio"

        return True, ""

    def _get_nombre_completo(self, docente: Dict) -> str:
        """Método auxiliar para obtener el nombre completo del docente."""
        if not docente:
            return "Sin docente"

        nombre = docente.get('nombre', '')
        apellido = docente.get('apellido', '')

        if nombre and apellido:
            return f"{nombre} {apellido}"
        elif nombre:
            return nombre
        elif apellido:
            return apellido
        else:
            return "Sin nombre"


class HorarioVirtual(HorarioBase):
    """
    Representa una clase virtual (online).
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.modalidad = 'virtual'
        self.plataforma = kwargs.get('plataforma', 'Teams')
        self.enlace = kwargs.get('enlace', '')

    def get_tipo(self) -> str:
        return "virtual"

    def description(self) -> str:
        docente_nombre = self._get_nombre_completo(self.docente)
        asignatura_nombre = self.asignatura.get('nombre', 'Sin asignatura')

        descripcion = (f"Clase virtual de {asignatura_nombre} "
                       f"dictada por {docente_nombre} de {self.start_time} a {self.end_time} "
                       f"el {self.dia}")

        if self.plataforma:
            descripcion += f" via {self.plataforma}"

        return descripcion

    def es_valido(self) -> tuple:
        """
        Validación específica para clases virtuales.
        """
        es_valido_base, mensaje_base = super().es_valido()
        if not es_valido_base:
            return False, mensaje_base

        # Validaciones específicas para clase virtual
        if not self.docente.get('id'):
            return False, "Clase virtual requiere un docente asignado"

        if not self.asignatura.get('id'):
            return False, "Clase virtual requiere una asignatura asignada"

        # Las clases virtuales NO deben tener aula física asignada
        if self.aula.get('id'):
            return False, "Clase virtual no debe tener aula física asignada"

        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        """
        Extiende el método base para incluir datos específicos de clase virtual.
        """
        data = super().to_dict()
        data.update({
            'plataforma': self.plataforma,
            'enlace': self.enlace
        })
        return data

    def _get_nombre_completo(self, docente: Dict) -> str:
        """Método auxiliar para obtener el nombre completo del docente."""
        if not docente:
            return "Sin docente"

        nombre = docente.get('nombre', '')
        apellido = docente.get('apellido', '')

        if nombre and apellido:
            return f"{nombre} {apellido}"
        elif nombre:
            return nombre
        elif apellido:
            return apellido
        else:
            return "Sin nombre"


class HorarioBloqueo(HorarioBase):
    """
    Representa un bloqueo de horario (tiempo no disponible).
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.motivo = kwargs.get('motivo', 'Bloqueo general')
        self.tipo_bloqueo = kwargs.get('tipo_bloqueo', 'mantenimiento')  # mantenimiento, evento, etc.

    def get_tipo(self) -> str:
        return "bloqueo"

    def description(self) -> str:
        aula_nombre = self.aula.get('nombre', 'Sin aula')
        sede_nombre = self.sede.get('nombre', 'Sin sede')

        descripcion = f"Bloqueo en {aula_nombre} de {self.start_time} a {self.end_time} "
        descripcion += f"en {sede_nombre} el {self.dia}"

        if self.motivo:
            descripcion += f" - Motivo: {self.motivo}"

        return descripcion

    def es_valido(self) -> tuple:
        """
        Validación específica para bloqueos.
        """
        es_valido_base, mensaje_base = super().es_valido()
        if not es_valido_base:
            return False, mensaje_base

        # Validaciones específicas para bloqueo
        if not self.aula.get('id'):
            return False, "Bloqueo requiere un aula asignada"

        # Los bloqueos NO deben tener docente ni asignatura
        if self.docente.get('id'):
            return False, "Bloqueo no debe tener docente asignado"

        if self.asignatura.get('id'):
            return False, "Bloqueo no debe tener asignatura asignada"

        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        """
        Extiende el método base para incluir datos específicos de bloqueo.
        """
        data = super().to_dict()
        data.update({
            'motivo': self.motivo,
            'tipo_bloqueo': self.tipo_bloqueo
        })
        return data