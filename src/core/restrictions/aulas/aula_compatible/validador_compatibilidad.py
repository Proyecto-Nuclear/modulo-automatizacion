from typing import Dict, Optional, Any, Protocol
from dataclasses import dataclass

class ReglasCompatibilidadProtocol(Protocol):
    @staticmethod
    def verificar_incompatibilidades(tipo_asignatura: str, tipo_aula: str) -> Optional[str]:
        ...

@dataclass
class ContextoValidacion:
    aula: Dict[str, Any]
    asignatura: Dict[str, Any]

    @classmethod
    def from_dict(cls, context: Dict[str, Any]) -> Optional['ContextoValidacion']:
        aula = context.get("aula")
        asignatura = context.get("asignatura")

        if not aula or not asignatura:
            return None

        return cls(aula=aula, asignatura=asignatura)

class ValidadorCompatibilidad:
    """Valida la compatibilidad entre el tipo de asignatura y el tipo de aula."""

    def __init__(self, reglas: ReglasCompatibilidadProtocol = None):
        from .reglas_compatibilidad import ReglasCompatibilidad
        self.reglas = reglas or ReglasCompatibilidad

    def validar(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Valida la compatibilidad entre el tipo de asignatura y el tipo de aula.

        :param context: Diccionario con los datos del aula y la asignatura.
        :return: None si es válido, mensaje de error si no se cumple la compatibilidad.
        """
        contexto = ContextoValidacion.from_dict(context)
        if not contexto:
            return "Error: Faltan datos de aula o asignatura para validar compatibilidad."

        return self._validar_compatibilidad(contexto)

    def _validar_compatibilidad(self, contexto: ContextoValidacion) -> Optional[str]:
        """
        Lógica interna de validación.

        :param contexto: Objeto de contexto con los datos del aula y la asignatura.
        :return: None si es válido, mensaje de error si no se cumple la compatibilidad.
        """
        tipo_asignatura = contexto.asignatura.get("tipo", "").lower().strip()
        tipo_aula = contexto.aula.get("tipo", "").lower().strip()

        if not tipo_asignatura or not tipo_aula:
            return (
                f"Error: Tipo de asignatura ('{contexto.asignatura.get('tipo', 'N/A')}') o "
                f"tipo de aula ('{contexto.aula.get('tipo', 'N/A')}') no están definidos."
            )

        incompatibilidad = self.reglas.verificar_incompatibilidades(tipo_asignatura, tipo_aula)
        if incompatibilidad:
            return (
                f"Incompatibilidad detectada: La asignatura '{contexto.asignatura.get('nombre', 'Sin nombre')}' "
                f"(tipo: '{contexto.asignatura.get('tipo', '')}') no es compatible con el aula "
                f"'{contexto.aula.get('nombre', 'Sin nombre')}' (tipo: '{contexto.aula.get('tipo', '')}').\n"
                f"Motivo: {incompatibilidad}"
            )
        return None

    """
    TODO: Revisar las clases dentro de las carpetas aula_no_ocupada aula_recursos capacidad_aula_suficiente
    """