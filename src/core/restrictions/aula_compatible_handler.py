from typing import Dict, Optional, Any
from .restriction_handler import RestrictionHandler

class AulaCompatibleHandler(RestrictionHandler):
    """
    Restricción: Una asignatura de laboratorio solo puede ser asignada a aulas de tipo laboratorio.
    """

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Verifica que si la asignatura es de laboratorio, el aula asignada sea también de tipo laboratorio.

        :param context: Dict con las claves:
            - 'aula': Dict con los datos del aula seleccionada (de aulas.json)
            - 'asignatura': Dict con los datos de la asignatura seleccionada (de asignaturas.json)
        :return: None si es válido, mensaje de error (str) si no se cumple la invariante.
        """
        aula = context.get("aula", {})
        asignatura = context.get("asignatura", {})

        tipo_asignatura = asignatura.get("tipo", "").lower()
        tipo_aula = aula.get("tipo", "").lower()

        if tipo_asignatura == "laboratorio" and tipo_aula != "laboratorio":
            return (
                f"La asignatura '{asignatura.get('nombre', '')}' es de tipo laboratorio, "
                f"pero el aula seleccionada ('{aula.get('nombre', '')}') es de tipo '{aula.get('tipo', '')}'. "
                "Debe asignarse a un aula de tipo laboratorio."
            )

        return None