from typing import Dict, Optional, Any
from src.core.restrictions.restriction_handler import RestrictionHandler

class AulaCompatibleHandler(RestrictionHandler):
    """
    Restricción: Una asignatura de laboratorio solo puede ser asignada a aulas de tipo laboratorio.

    Invariante: self.asignatura.tipo = "Laboratorio" implies self.aula.tipo = "Laboratorio"

    Esta restricción también puede extenderse para otros tipos de compatibilidad:
    - Asignaturas virtuales requieren aulas con equipos de videoconferencia
    """

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Verifica la compatibilidad entre el tipo de asignatura y el tipo de aula.

        :param context: Dict con las claves:
            - 'aula': Dict con los datos del aula seleccionada
                - 'tipo': str (ej: "laboratorio", "aula_regular", "taller", "virtual")
                - 'nombre': str
                - 'id': str/int
            - 'asignatura': Dict con los datos de la asignatura seleccionada
                - 'tipo': str (ej: "laboratorio", "teorica", "taller", "virtual")
                - 'nombre': str
                - 'id': str/int
        :return: None si es válido, mensaje de error (str) si no se cumple la invariante.
        """
        # Validar que existan los datos requeridos
        aula = context.get("aula", {})
        asignatura = context.get("asignatura", {})

        if not aula or not asignatura:
            return "Error: Faltan datos de aula o asignatura para validar compatibilidad."

        # Obtener tipos normalizados (lowercase para comparación)
        tipo_asignatura = asignatura.get("tipo", "").lower().strip()
        tipo_aula = aula.get("tipo", "").lower().strip()

        # Validar que los tipos no estén vacíos
        if not tipo_asignatura or not tipo_aula:
            return (
                f"Error: Tipo de asignatura ('{asignatura.get('tipo', 'N/A')}') o "
                f"tipo de aula ('{aula.get('tipo', 'N/A')}') no están definidos."
            )

        # Reglas de compatibilidad
        incompatibilidades = self._verificar_incompatibilidades(tipo_asignatura, tipo_aula)

        if incompatibilidades:
            return (
                f"Incompatibilidad detectada: La asignatura '{asignatura.get('nombre', 'Sin nombre')}' "
                f"(tipo: '{asignatura.get('tipo', '')}') no es compatible con el aula "
                f"'{aula.get('nombre', 'Sin nombre')}' (tipo: '{aula.get('tipo', '')}').\n"
                f"Motivo: {incompatibilidades}"
            )

        return None

    def _verificar_incompatibilidades(self, tipo_asignatura: str, tipo_aula: str) -> Optional[str]:
        """
        Verifica las reglas específicas de incompatibilidad entre tipos.

        :param tipo_asignatura: Tipo de la asignatura (normalizado)
        :param tipo_aula: Tipo del aula (normalizado)
        :return: Mensaje de incompatibilidad o None si son compatibles
        """
        # Regla principal: Laboratorios solo en aulas de laboratorio
        if tipo_asignatura == "laboratorio" and tipo_aula != "laboratorio":
            return "Las asignaturas de laboratorio requieren aulas de tipo laboratorio."

        # Regla: Asignaturas virtuales requieren aulas con capacidad virtual
        if tipo_asignatura == "virtual" and tipo_aula not in ["virtual", "hibrida"]:
            return "Las asignaturas virtuales requieren aulas virtuales o híbridas."

        # Regla: Talleres requieren espacios de taller
        if tipo_asignatura == "taller" and tipo_aula not in ["taller", "laboratorio"]:
            return "Las asignaturas de taller requieren espacios de taller o laboratorio."

        # Regla: Asignaturas teóricas no pueden usar laboratorios especializados
        # (opcional, para optimizar uso de recursos)
        if (tipo_asignatura in ["teorica", "magistral"] and
                tipo_aula in ["laboratorio_especializado", "quirofano", "laboratorio_quimica"]):
            return (
                "Las asignaturas teóricas no deberían usar laboratorios especializados "
                "para optimizar el uso de recursos."
            )

        # Si llegamos aquí, son compatibles
        return None

    def get_aulas_compatibles(self, context: Dict[str, Any]) -> list:
        """
        Método auxiliar que retorna las aulas compatibles con una asignatura.
        Útil para el sistema de generación automática de horarios.

        :param context: Dict con las claves:
            - 'asignatura': Dict con los datos de la asignatura
            - 'todas_aulas': List[Dict] con todas las aulas disponibles
        :return: Lista de aulas compatibles
        """
        asignatura = context.get("asignatura", {})
        todas_aulas = context.get("todas_aulas", [])

        if not asignatura or not todas_aulas:
            return []

        aulas_compatibles = []

        for aula in todas_aulas:
            # Crear contexto temporal para validar cada aula
            temp_context = {
                "aula": aula,
                "asignatura": asignatura
            }

            # Si la validación retorna None, el aula es compatible
            if self.validate(temp_context) is None:
                aulas_compatibles.append(aula)

        return aulas_compatibles