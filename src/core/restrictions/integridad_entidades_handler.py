from typing import Dict, Any, Optional
from .restriction_handler import RestrictionHandler

class IntegridadEntidadesHandler(RestrictionHandler):
    """
    Restricción: Toda asignación debe involucrar entidades que exista y estén en un estado activo.
    """

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Verifica que los ID de aula, docente, asignatura y sede existan y tengan estado "activo".

        :param context: Dict con las claves:
            - 'aula': Dict con los datos del aula seleccionada (de aulas.json)
            - 'docente': Dict con los datos del docente seleccionado (de docentes.json)
            - 'asignatura': Dict con los datos de la asignatura seleccionada (de asignaturas.json)
            - 'sede': Dict con los datos de la sede seleccionada (de sedes.json)
        :return: None si todas las entidades existen y están activas, mensaje de error (str) si no se cumple la invariante.
        """
        entidades = [
            ('aula', context.get('aula', {})),
            ('docente', context.get('docente', {})),
            ('asignatura', context.get('asignatura', {})),
            ('sede', context.get('sede', {}))
        ]

        for nombre, entidad in entidades:
            if not entidad:
                return f"Error: La entidad '{nombre}' no esta definida en la asignación."
            if entidad.get('estado', '').lower() != 'activo':
                return (f"Error: La entidad '{nombre}' con ID '{entidad.get('id', '')}' "
                        f"no está activa (estado: '{entidad.get('estado', '')}').")
        return None