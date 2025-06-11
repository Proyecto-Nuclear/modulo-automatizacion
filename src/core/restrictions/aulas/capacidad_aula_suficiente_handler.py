from typing import List, Dict, Optional, Any
from src.core.restrictions.restriction_handler import RestrictionHandler

class CapacidadAulaSuficienteHandler(RestrictionHandler):
    """
    Restricción: El aula asignada debe tener capacidad suficiente para el número de estudiantes.
    Si no la tiene, recomienda otras aulas que sí la tengan.

    Invariante: self.aula.capacidad >= self.numero_estudiantes

    Interpretación: El aula debe tener una capacidad igual o mayor al número de estudiantes.

    Esta restricción es esencial para el Enfoque 2 ya que:
    - Valida cada nuevo bloque contra la capacidad del aula
    - Permite filtrar aulas con capacidad suficiente durante la generación automática
    - Soporta tanto validación individual como validación global del horario completo
    - Facilita la selección automática de aulas con capacidad adecuada
    """

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Verifica que el aula seleccionada tenga capacidad suficiente.
        Si no cumple, recomienda otras aulas que sí cumplen.

        Soporta dos modos de validación:
        1. Validación individual: Verifica un nuevo bloque contra la capacidad del aula
        2. Validación global: Verifica todo el conjunto de horarios asignados

        :param context: Dict con las claves:
            Para validación individual:
            - 'nuevo_bloque': Dict con el nuevo bloque a validar
                - 'aula_id': ID del aula
                - 'asignatura_id': ID de la asignatura
                - 'numero_estudiantes': int, cantidad de estudiantes
            - 'aulas': List[Dict] con todas las aulas disponibles (de aulas.json)
            - 'asignaturas': List[Dict] con todas las asignaturas disponibles (de asignaturas.json)

            Para validación global:
            - 'schedules' o 'horarios': Lista completa de horarios a validar
            - 'aulas': List[Dict] con todas las aulas disponibles (de aulas.json)
            - 'asignaturas': List[Dict] con todas las asignaturas disponibles (de asignaturas.json)

            Para validación directa (compatibilidad con versión anterior):
            - 'aula': Dict con los datos del aula seleccionada (de aulas.json)
            - 'numero_estudiantes': int, cantidad de estudiantes
            - 'aulas': List[Dict] con todas las aulas disponibles (de aulas.json)
            - 'asignatura': Dict con los datos de la asignatura (de asignaturas.json)

        :return: None si es válido, mensaje de error (str) si la capacidad es insuficiente, con sugerencias si corresponde.
        """
        # Determinar modo de validación
        nuevo_bloque = context.get("nuevo_bloque")
        aula_directa = context.get("aula")

        if nuevo_bloque:
            return self._validar_bloque_individual(context)
        elif aula_directa:
            return self._validar_directo(context)
        else:
            return self._validar_horarios_globales(context)

    def _validar_bloque_individual(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Valida un nuevo bloque contra la capacidad del aula.

        Este método es especialmente útil para el Enfoque 2 durante la generación
        automática, ya que permite validar cada bloque antes de agregarlo al horario.

        :param context: Contexto con nuevo_bloque, aulas y asignaturas
        :return: None si es válido, mensaje de error si la capacidad es insuficiente
        """
        nuevo_bloque = context["nuevo_bloque"]
        aulas = context.get("aulas", [])
        asignaturas = context.get("asignaturas", [])

        # Validar datos del nuevo bloque
        aula_id = nuevo_bloque.get("aula_id")
        asignatura_id = nuevo_bloque.get("asignatura_id")
        numero_estudiantes = nuevo_bloque.get("numero_estudiantes")

        if not aula_id or not asignatura_id or numero_estudiantes is None:
            return "El nuevo bloque debe tener aula_id, asignatura_id y numero_estudiantes definidos."

        # Buscar aula y asignatura
        aula = self._buscar_entidad_por_id(aulas, aula_id)
        asignatura = self._buscar_entidad_por_id(asignaturas, asignatura_id)

        if not aula:
            return f"No se encontró el aula con ID: {aula_id}"

        if not asignatura:
            return f"No se encontró la asignatura con ID: {asignatura_id}"

        # Validar capacidad
        return self._validar_capacidad_aula(aula, numero_estudiantes, context)

    def _validar_horarios_globales(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Valida todo el conjunto de horarios para verificar la capacidad de las aulas.

        Útil para validación final del horario completo generado automáticamente.

        :param context: Contexto con schedules/horarios, aulas y asignaturas
        :return: None si es válido, mensaje de error si hay problemas de capacidad
        """
        horarios = context.get("schedules") or context.get("horarios", [])
        aulas = context.get("aulas", [])
        asignaturas = context.get("asignaturas", [])

        if not horarios:
            return None  # No hay horarios que validar

        # Validar cada horario
        for horario in horarios:
            aula_id = horario.get('aula_id') or horario.get('aula')
            asignatura_id = horario.get('asignatura_id') or horario.get('asignatura')
            numero_estudiantes = horario.get('numero_estudiantes')

            if not aula_id or not asignatura_id or numero_estudiantes is None:
                continue  # Saltar horarios incompletos

            # Buscar entidades
            aula = self._buscar_entidad_por_id(aulas, aula_id)
            asignatura = self._buscar_entidad_por_id(asignaturas, asignatura_id)

            if not aula or not asignatura:
                continue  # Saltar si no se encuentran las entidades

            # Validar capacidad para este horario
            error = self._validar_capacidad_aula(aula, numero_estudiantes, context)
            if error:
                # Agregar información del horario al error
                horario_info = f" (Horario: {horario.get('dia', 'N/A')} {horario.get('hora_inicio', 'N/A')}-{horario.get('hora_fin', 'N/A')})"
                return error + horario_info

        return None

    def _validar_directo(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Validación directa con aula y número de estudiantes proporcionados directamente.

        Mantiene compatibilidad con la versión anterior del handler.

        :param context: Contexto con aula y número de estudiantes directos
        :return: None si es válido, mensaje de error si la capacidad es insuficiente
        """
        aula = context["aula"]
        numero_estudiantes = context.get("numero_estudiantes")

        if numero_estudiantes is None:
            return "No se proporcionó el número de estudiantes para la asignación."

        return self._validar_capacidad_aula(aula, numero_estudiantes, context)

    def _validar_capacidad_aula(self, aula: Dict, numero_estudiantes: int, context: Dict[str, Any]) -> Optional[str]:
        """
        Valida que un aula tenga capacidad suficiente para un número de estudiantes.

        :param aula: Datos del aula
        :param numero_estudiantes: Número de estudiantes
        :param context: Contexto con aulas opcionales para recomendaciones
        :return: None si es válido, mensaje de error si la capacidad es insuficiente
        """
        capacidad_aula = aula.get("capacidad", 0)
        asignatura_nombre = context.get("asignatura", {}).get("nombre", "Asignatura desconocida")

        if capacidad_aula < numero_estudiantes:
            msg = (
                f"No se puede asignar el aula '{aula.get('nombre', aula.get('id', 'desconocida'))}' "
                f"(capacidad: {capacidad_aula}) a la asignatura '{asignatura_nombre}' "
                f"porque la cantidad de estudiantes es {numero_estudiantes}."
            )

            # Buscar aulas recomendadas (distintas al aula seleccionada y con capacidad suficiente)
            aulas = context.get("aulas", [])
            recomendaciones = [
                f"{a['nombre']} (capacidad: {a['capacidad']})"
                for a in aulas
                if a["id"] != aula["id"] and a.get("capacidad", 0) >= numero_estudiantes
            ]

            if recomendaciones:
                msg += "\nAulas recomendadas con capacidad suficiente: " + "; ".join(recomendaciones)
            else:
                msg += "\nNo se encontraron otras aulas con capacidad suficiente."

            return msg

        return None

    def _buscar_entidad_por_id(self, entidades: List[Dict], entity_id: Any) -> Optional[Dict]:
        """
        Busca una entidad por su ID en una lista.

        :param entidades: Lista de entidades
        :param entity_id: ID a buscar
        :return: Entidad encontrada o None
        """
        for entidad in entidades:
            if entidad.get("id") == entity_id:
                return entidad
        return None

    def obtener_aulas_con_capacidad_suficiente(self, context: Dict[str, Any]) -> List[str]:
        """
        Método auxiliar que retorna las aulas que tienen capacidad suficiente para un número de estudiantes.

        Útil para el sistema de generación automática de horarios del Enfoque 2.

        :param context: Dict con las claves:
            - 'numero_estudiantes': int, cantidad de estudiantes
            - 'todas_aulas': Lista de todas las aulas
        :return: Lista de IDs de aulas que tienen capacidad suficiente
        """
        numero_estudiantes = context.get("numero_estudiantes")
        todas_aulas = context.get("todas_aulas", [])

        if numero_estudiantes is None:
            return []

        aulas_compatibles = []

        for aula in todas_aulas:
            capacidad_aula = aula.get("capacidad", 0)
            if capacidad_aula >= numero_estudiantes:
                aulas_compatibles.append(aula.get("id"))

        return aulas_compatibles

    def es_aula_compatible_con_capacidad(self, aula_id: str, numero_estudiantes: int, context: Dict[str, Any]) -> bool:
        """
        Verifica si un aula específica es compatible con un número de estudiantes.

        Método de conveniencia para validaciones rápidas durante la generación automática.

        :param aula_id: ID del aula
        :param numero_estudiantes: Número de estudiantes
        :param context: Contexto con aulas
        :return: True si es compatible, False en caso contrario
        """
        aulas = context.get("aulas", [])

        aula = self._buscar_entidad_por_id(aulas, aula_id)

        if not aula:
            return False

        capacidad_aula = aula.get("capacidad", 0)
        return capacidad_aula >= numero_estudiantes