from typing import Dict, Any, Optional, List
from src.core.restrictions.restriction_handler import RestrictionHandler

class IntegridadEntidadesHandler(RestrictionHandler):
    """
    Restricción: Toda asignación debe involucrar entidades que existan y estén en un estado activo.

    Invariante: Para cada asignación, aula, docente, asignatura y sede deben existir y estar activos.
    """

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Valida que los ID de aula, docente, asignatura y sede existan y tengan estado "activo".

        Soporta:
        - Validación individual: 'aula', 'docente', 'asignatura', 'sede'
        - Validación global: 'schedules' (lista de asignaciones)
        - Compatibilidad directa: 'schedule' (lista de asignaciones)

        :param context: Dict con las claves:
            - 'aula', 'docente', 'asignatura', 'sede': Dicts de entidades (opcional)
            - 'schedules' o 'schedule': Lista de asignaciones (opcional)
        :return: None si todas las entidades existen y están activas, mensaje de error (str) si no se cumple la invariante.
        """
        # Validación global (lista de asignaciones)
        if "schedules" in context or "schedule" in context:
            return self._validar_asignaciones_globales(context)
        # Validación individual
        return self._validar_asignacion_individual(context)

    def _validar_asignacion_individual(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Valida una sola asignación.
        """
        entidades = [
            ('aula', context.get('aula', {})),
            ('docente', context.get('docente', {})),
            ('asignatura', context.get('asignatura', {})),
            ('sede', context.get('sede', {}))
        ]
        for nombre, entidad in entidades:
            if not entidad:
                return f"Error: La entidad '{nombre}' no está definida en la asignación."
            if entidad.get('estado', '').lower() != 'activo':
                return (f"Error: La entidad '{nombre}' con ID '{entidad.get('id', '')}' "
                        f"no está activa (estado: '{entidad.get('estado', '')}').")
        return None

    def _validar_asignaciones_globales(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Valida una lista de asignaciones (schedules).
        """
        schedules: List[Dict] = context.get("schedules") or context.get("schedule", [])
        errores = []
        for idx, asignacion in enumerate(schedules):
            # Permite que cada asignación tenga sus entidades como dicts anidados
            entidades = [
                ('aula', asignacion.get('aula', {})),
                ('docente', asignacion.get('docente', {})),
                ('asignatura', asignacion.get('asignatura', {})),
                ('sede', asignacion.get('sede', {}))
            ]
            for nombre, entidad in entidades:
                if not entidad:
                    errores.append(
                        f"Error: La entidad '{nombre}' no está definida en la asignación {asignacion.get('id', idx)}."
                    )
                elif entidad.get('estado', '').lower() != 'activo':
                    errores.append(
                        f"Error: La entidad '{nombre}' con ID '{entidad.get('id', '')}' "
                        f"no está activa (estado: '{entidad.get('estado', '')}') en la asignación {asignacion.get('id', idx)}."
                    )
        if errores:
            return "\n".join(errores)
        return None

    def entidades_faltantes_o_inactivas(self, context: Dict[str, Any]) -> List[str]:
        """
        Devuelve una lista de nombres de entidades faltantes o inactivas en una asignación.
        """
        entidades = [
            ('aula', context.get('aula', {})),
            ('docente', context.get('docente', {})),
            ('asignatura', context.get('asignatura', {})),
            ('sede', context.get('sede', {}))
        ]
        faltantes = []
        for nombre, entidad in entidades:
            if not entidad or entidad.get('estado', '').lower() != 'activo':
                faltantes.append(nombre)
        return faltantes