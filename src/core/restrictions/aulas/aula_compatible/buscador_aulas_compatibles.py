from typing import Dict, List, Any, Protocol, Optional
from dataclasses import dataclass


class ValidadorProtocol(Protocol):
    @staticmethod
    def validar(context: Dict[str, Any]) -> Optional[str]:
        ...


@dataclass
class ContextoBusqueda:
    asignatura: Dict[str, Any]
    todas_aulas: List[Dict[str, Any]]

    @classmethod
    def from_dict(cls, context: Dict[str, Any]) -> Optional['ContextoBusqueda']:
        asignatura = context.get("asignatura", {})
        todas_aulas = context.get("todas_aulas", [])

        if not asignatura or not todas_aulas:
            return None

        return cls(asignatura=asignatura, todas_aulas=todas_aulas)


class BuscadorAulasCompatibles:
    """Busca aulas compatibles con una asignatura usando inyección de dependencias."""

    def __init__(self, validador: ValidadorProtocol = None):
        from .validador_compatibilidad import ValidadorCompatibilidad
        self.validador = validador or ValidadorCompatibilidad

    def get_aulas_compatibles(self, context: Dict[str, Any]) -> List[Dict]:
        """
        Busca todas las aulas compatibles con una asignatura.

        :param context: Contexto con asignatura y todas_aulas
        :return: Lista de aulas compatibles
        """
        contexto = ContextoBusqueda.from_dict(context)
        if not contexto:
            return []

        return self._buscar_compatibles(contexto)

    def _buscar_compatibles(self, contexto: ContextoBusqueda) -> List[Dict]:
        """Lógica interna de búsqueda."""
        aulas_compatibles = []
        for aula in contexto.todas_aulas:
            if self._es_aula_compatible(aula, contexto.asignatura):
                aulas_compatibles.append(aula)
        return aulas_compatibles

    def _es_aula_compatible(self, aula: Dict[str, Any], asignatura: Dict[str, Any]) -> bool:
        """Verifica si un aula específica es compatible con una asignatura."""
        temp_context = {"aula": aula, "asignatura": asignatura}
        return self.validador.validar(temp_context) is None