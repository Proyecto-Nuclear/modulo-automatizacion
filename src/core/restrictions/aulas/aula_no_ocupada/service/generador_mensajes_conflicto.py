from typing import Dict, Any

from src.utils.name_resolver import obtener_nombre_aula, obtener_nombre_asignatura


class GeneradorMensajesConflicto:
    """Genera mensajes descriptivos para conflictos de horarios."""

    def generar_mensaje_individual(self, nuevo_bloque: Dict, horario_existente: Dict, context: Dict[str, Any]) -> str:
        """Genera mensaje para conflictos en validación individual."""
        aula_nombre = obtener_nombre_aula(nuevo_bloque.get("aula_id"), context)
        asignatura_nueva = obtener_nombre_asignatura(nuevo_bloque.get("asignatura_id"), context)
        asignatura_existente = obtener_nombre_asignatura(horario_existente.get("asignatura_id"), context)

        return (
            f"Conflicto de horario detectado en {aula_nombre}: "
            f"La asignatura '{asignatura_nueva}' "
            f"({nuevo_bloque.get('dia')} {nuevo_bloque.get('hora_inicio')}-{nuevo_bloque.get('hora_fin')}) "
            f"se solapa con '{asignatura_existente}' "
            f"({horario_existente.get('dia')} {horario_existente.get('hora_inicio')}-{horario_existente.get('hora_fin')})."
        )

    def generar_mensaje_global(self, h1: Dict, h2: Dict, context: Dict[str, Any]) -> str:
        """Genera mensaje para conflictos en validación global."""
        aula_id = h1.get('aula_id') or h1.get('aula')
        aula_nombre = obtener_nombre_aula(aula_id, context)

        asignatura1 = obtener_nombre_asignatura(h1.get("asignatura_id"), context)
        asignatura2 = obtener_nombre_asignatura(h2.get("asignatura_id"), context)

        return (
            f"Conflicto: Solapamiento de clases en {aula_nombre}: "
            f"'{asignatura1}' ({h1.get('dia')} {h1.get('hora_inicio')}-{h1.get('hora_fin')}) "
            f"se solapa con '{asignatura2}' ({h2.get('dia')} {h2.get('hora_inicio')}-{h2.get('hora_fin')})."
        )