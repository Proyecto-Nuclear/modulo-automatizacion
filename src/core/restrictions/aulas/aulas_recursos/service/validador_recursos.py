from typing import Dict, Set, Optional

from src.utils.name_resolver import obtener_nombres_recursos


class ValidadorRecursos:
    """Valida que las aulas tengan los recursos requeridos."""

    @staticmethod
    def validar_recursos_aula_asignatura(aula: Dict, asignatura: Dict, context: Dict) -> Optional[str]:
        """
        Valida que un aula tenga todos los recursos requeridos por una asignatura.
        """
        aula_recursos = set(aula.get("id_recursos", []) or aula.get("recursos", []))
        requiere_recursos = set(asignatura.get("requiereRecursos", []) or asignatura.get("recursos_requeridos", []))

        if not requiere_recursos:
            return None

        faltantes = requiere_recursos - aula_recursos

        if faltantes:
            return ValidadorRecursos._generar_mensaje_recursos_faltantes(
                aula, asignatura, faltantes, context
            )

        return None

    @staticmethod
    def _generar_mensaje_recursos_faltantes(aula: Dict, asignatura: Dict, faltantes: Set[str], context: Dict) -> str:
        """Genera mensaje descriptivo para recursos faltantes."""
        nombres_faltantes = obtener_nombres_recursos(list(faltantes), context)

        aula_nombre = aula.get("nombre", f"Aula {aula.get('id', 'desconocida')}")
        asignatura_nombre = asignatura.get("nombre", f"Asignatura {asignatura.get('id', 'desconocida')}")

        return (
            f"El aula '{aula_nombre}' (ID: {aula.get('id', 'N/A')}) no cumple con los recursos requeridos "
            f"por la asignatura '{asignatura_nombre}'. "
            f"Recursos faltantes: {', '.join(nombres_faltantes)}."
        )