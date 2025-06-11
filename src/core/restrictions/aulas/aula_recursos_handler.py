from typing import Dict, Optional, Any
from src.core.restrictions.restriction_handler import RestrictionHandler

class AulaRecursosHandler(RestrictionHandler):
    """
    Restricción: El aula asignada debe tener todos los recursos que requiere la asignatura.
    """

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Verifica que el aula seleccionada tenga todos los recursos requeridos por la asignatura.

        :param context: Dict con las claves:
            - 'aula': Dict con los datos del aula seleccionada (de aulas.json)
            - 'asignatura': Dict con los datos de la asignatura seleccionada (de asignaturas.json)
            - 'recursos': List[Dict] con todos los recursos disponibles (de recursos.json) [opcional, solo si se desea mostrar nombres de recursos faltantes]
        :return: None si es válido, mensaje de error (str) si faltan recursos.
        """
        aula: Dict = context["aula"]
        asignatura: Dict = context["asignatura"]

        aula_recursos = set(aula.get("id_recursos", []))
        requiere_recursos = set(asignatura.get("requiereRecursos", []))

        faltantes = requiere_recursos - aula_recursos

        if faltantes:
            # Opcional: mostrar nombres de recursos faltantes si están en el contexto
            recursos_disponibles = {r["id"]: r.get("nombre", r["id"]) for r in context.get("recursos", [])}
            nombres_faltantes = [recursos_disponibles.get(rid, rid) for rid in faltantes]
            msg = (
                f"El aula '{aula['nombre']}' (ID: {aula['id']}) no cumple con los recursos requeridos por la asignatura "
                f"'{asignatura['nombre']}'. Recursos faltantes: {', '.join(nombres_faltantes)}."
            )
            return msg

        return None