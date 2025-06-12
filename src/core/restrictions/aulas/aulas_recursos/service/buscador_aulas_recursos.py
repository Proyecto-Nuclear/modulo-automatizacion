from typing import Dict, List, Any

from src.utils.entity_finder import buscar_entidad_por_id
from src.utils.name_resolver import obtener_nombres_recursos
from .validador_directo import ValidadorDirecto


class BuscadorAulasRecursos:
    """Busca aulas que cumplan con los recursos requeridos."""

    def __init__(self):
        self.validador_directo = ValidadorDirecto()

    def obtener_aulas_con_recursos_suficientes(self, context: Dict[str, Any]) -> List[str]:
        """Retorna las aulas que tienen los recursos necesarios para una asignatura."""
        asignatura_id = context.get("asignatura_id")
        todas_aulas = context.get("todas_aulas", [])
        asignaturas = context.get("asignaturas", [])

        if not asignatura_id:
            return []

        asignatura = buscar_entidad_por_id(asignaturas, asignatura_id)
        if not asignatura:
            return []

        aulas_compatibles = []

        for aula in todas_aulas:
            temp_context = {
                "aula": aula,
                "asignatura": asignatura,
                "recursos": context.get("recursos", [])
            }

            if self.validador_directo.validar(temp_context) is None:
                aulas_compatibles.append(aula.get("id"))

        return aulas_compatibles

    def obtener_recursos_faltantes_por_aula(self, context: Dict[str, Any]) -> Dict[str, List[str]]:
        """Retorna un diccionario con los recursos faltantes por cada aula."""
        asignatura_id = context.get("asignatura_id")
        todas_aulas = context.get("todas_aulas", [])
        asignaturas = context.get("asignaturas", [])

        if not asignatura_id:
            return {}

        asignatura = buscar_entidad_por_id(asignaturas, asignatura_id)
        if not asignatura:
            return {}

        requiere_recursos = set(asignatura.get("requiereRecursos", []))
        recursos_faltantes_por_aula = {}

        for aula in todas_aulas:
            aula_recursos = set(aula.get("id_recursos", []))
            faltantes = requiere_recursos - aula_recursos

            if faltantes:
                nombres_faltantes = obtener_nombres_recursos(list(faltantes), context)
                recursos_faltantes_por_aula[aula.get("id")] = nombres_faltantes

        return recursos_faltantes_por_aula

    def es_aula_compatible_con_asignatura(self, aula_id: str, asignatura_id: str, context: Dict[str, Any]) -> bool:
        """Verifica si un aula específica es compatible con una asignatura específica."""
        aulas = context.get("aulas", [])
        asignaturas = context.get("asignaturas", [])

        aula = buscar_entidad_por_id(aulas, aula_id)
        asignatura = buscar_entidad_por_id(asignaturas, asignatura_id)

        if not aula or not asignatura:
            return False

        temp_context = {
            "aula": aula,
            "asignatura": asignatura,
            "recursos": context.get("recursos", [])
        }

        return self.validador_directo.validar(temp_context) is None