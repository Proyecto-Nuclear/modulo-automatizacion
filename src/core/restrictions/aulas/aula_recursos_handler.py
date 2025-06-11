from typing import Dict, Optional, Any, List, Set
from src.core.restrictions.restriction_handler import RestrictionHandler

class AulaRecursosHandler(RestrictionHandler):
    """
    Restricción: El aula asignada debe tener todos los recursos que requiere la asignatura.

    Invariante: self.aula.recursos -> includesAll(self.asignatura.requiereRecursos)

    Interpretación: El aula asignada debe tener todos los recursos que requiere la asignatura.

    Esta restricción es esencial para el Enfoque 2 ya que:
    - Valida cada nuevo bloque contra los recursos disponibles del aula
    - Permite filtrar aulas compatibles durante la generación automática
    - Soporta tanto validación individual como validación global del horario completo
    - Facilita la selección automática de aulas con recursos adecuados
    """

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Verifica que el aula seleccionada tenga todos los recursos requeridos por la asignatura.

        Soporta dos modos de validación:
        1. Validación individual: Verifica un nuevo bloque contra recursos del aula
        2. Validación global: Verifica todo el conjunto de horarios asignados

        :param context: Dict con las claves:
            Para validación individual:
            - 'nuevo_bloque': Dict con el nuevo bloque a validar
                - 'aula_id': ID del aula
                - 'asignatura_id': ID de la asignatura
            - 'aulas': Lista de aulas disponibles
            - 'asignaturas': Lista de asignaturas
            - 'recursos': Lista de recursos (opcional, para nombres descriptivos)

            Para validación global:
            - 'schedules' o 'horarios': Lista completa de horarios a validar
            - 'aulas': Lista de aulas disponibles
            - 'asignaturas': Lista de asignaturas
            - 'recursos': Lista de recursos (opcional)

            Para validación directa (compatibilidad con versión anterior):
            - 'aula': Dict con datos del aula
            - 'asignatura': Dict con datos de la asignatura
            - 'recursos': Lista de recursos (opcional)

        :return: None si es válido, mensaje de error (str) si faltan recursos
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
        Valida un nuevo bloque contra los recursos disponibles del aula.

        Este método es especialmente útil para el Enfoque 2 durante la generación
        automática, ya que permite validar cada bloque antes de agregarlo al horario.

        :param context: Contexto con nuevo_bloque, aulas y asignaturas
        :return: None si es válido, mensaje de error si faltan recursos
        """
        nuevo_bloque = context["nuevo_bloque"]
        aulas = context.get("aulas", [])
        asignaturas = context.get("asignaturas", [])

        # Validar datos del nuevo bloque
        aula_id = nuevo_bloque.get("aula_id")
        asignatura_id = nuevo_bloque.get("asignatura_id")

        if not aula_id or not asignatura_id:
            return "El nuevo bloque debe tener aula_id y asignatura_id definidos."

        # Buscar aula y asignatura
        aula = self._buscar_entidad_por_id(aulas, aula_id)
        asignatura = self._buscar_entidad_por_id(asignaturas, asignatura_id)

        if not aula:
            return f"No se encontró el aula con ID: {aula_id}"

        if not asignatura:
            return f"No se encontró la asignatura con ID: {asignatura_id}"

        # Validar recursos
        return self._validar_recursos_aula_asignatura(aula, asignatura, context)

    def _validar_horarios_globales(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Valida todo el conjunto de horarios para verificar recursos.

        Útil para validación final del horario completo generado automáticamente.

        :param context: Contexto con schedules/horarios, aulas y asignaturas
        :return: None si es válido, mensaje de error si hay problemas de recursos
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

            if not aula_id or not asignatura_id:
                continue  # Saltar horarios incompletos

            # Buscar entidades
            aula = self._buscar_entidad_por_id(aulas, aula_id)
            asignatura = self._buscar_entidad_por_id(asignaturas, asignatura_id)

            if not aula or not asignatura:
                continue  # Saltar si no se encuentran las entidades

            # Validar recursos para este horario
            error = self._validar_recursos_aula_asignatura(aula, asignatura, context)
            if error:
                # Agregar información del horario al error
                horario_info = f" (Horario: {horario.get('dia', 'N/A')} {horario.get('hora_inicio', 'N/A')}-{horario.get('hora_fin', 'N/A')})"
                return error + horario_info

        return None

    def _validar_directo(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Validación directa con aula y asignatura proporcionadas directamente.

        Mantiene compatibilidad con la versión anterior del handler.

        :param context: Contexto con aula y asignatura directas
        :return: None si es válido, mensaje de error si faltan recursos
        """
        aula = context["aula"]
        asignatura = context["asignatura"]

        return self._validar_recursos_aula_asignatura(aula, asignatura, context)

    def _validar_recursos_aula_asignatura(self, aula: Dict, asignatura: Dict, context: Dict[str, Any]) -> Optional[str]:
        """
        Valida que un aula tenga todos los recursos requeridos por una asignatura.

        :param aula: Datos del aula
        :param asignatura: Datos de la asignatura
        :param context: Contexto con recursos opcionales
        :return: None si es válido, mensaje de error si faltan recursos
        """
        # Obtener recursos del aula y requerimientos de la asignatura
        aula_recursos = set(aula.get("id_recursos", []) or aula.get("recursos", []))
        requiere_recursos = set(asignatura.get("requiereRecursos", []) or asignatura.get("recursos_requeridos", []))

        # Si la asignatura no requiere recursos, es válida
        if not requiere_recursos:
            return None

        # Calcular recursos faltantes
        faltantes = requiere_recursos - aula_recursos

        if faltantes:
            return self._generar_mensaje_recursos_faltantes(aula, asignatura, faltantes, context)

        return None

    def _generar_mensaje_recursos_faltantes(self, aula: Dict, asignatura: Dict, faltantes: Set[str], context: Dict[str, Any]) -> str:
        """
        Genera un mensaje descriptivo para recursos faltantes.

        :param aula: Datos del aula
        :param asignatura: Datos de la asignatura
        :param faltantes: Set de IDs de recursos faltantes
        :param context: Contexto con recursos opcionales
        :return: Mensaje de error descriptivo
        """
        # Obtener nombres de recursos faltantes
        recursos_disponibles = {r["id"]: r.get("nombre", r["id"]) for r in context.get("recursos", [])}
        nombres_faltantes = [recursos_disponibles.get(rid, rid) for rid in faltantes]

        aula_nombre = aula.get("nombre", f"Aula {aula.get('id', 'desconocida')}")
        asignatura_nombre = asignatura.get("nombre", f"Asignatura {asignatura.get('id', 'desconocida')}")

        return (
            f"El aula '{aula_nombre}' (ID: {aula.get('id', 'N/A')}) no cumple con los recursos requeridos "
            f"por la asignatura '{asignatura_nombre}'. "
            f"Recursos faltantes: {', '.join(nombres_faltantes)}."
        )

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

    def obtener_aulas_con_recursos_suficientes(self, context: Dict[str, Any]) -> List[str]:
        """
        Método auxiliar que retorna las aulas que tienen los recursos necesarios para una asignatura.

        Útil para el sistema de generación automática de horarios del Enfoque 2.

        :param context: Dict con las claves:
            - 'asignatura_id': ID de la asignatura
            - 'todas_aulas': Lista de todas las aulas
            - 'asignaturas': Lista de asignaturas
            - 'recursos': Lista de recursos (opcional)
        :return: Lista de IDs de aulas que tienen los recursos necesarios
        """
        asignatura_id = context.get("asignatura_id")
        todas_aulas = context.get("todas_aulas", [])
        asignaturas = context.get("asignaturas", [])

        if not asignatura_id:
            return []

        # Buscar la asignatura
        asignatura = self._buscar_entidad_por_id(asignaturas, asignatura_id)
        if not asignatura:
            return []

        aulas_compatibles = []

        for aula in todas_aulas:
            # Crear contexto temporal para validar esta aula
            temp_context = {
                "aula": aula,
                "asignatura": asignatura,
                "recursos": context.get("recursos", [])
            }

            # Si la validación retorna None, el aula tiene los recursos necesarios
            if self._validar_directo(temp_context) is None:
                aulas_compatibles.append(aula.get("id"))

        return aulas_compatibles

    def obtener_recursos_faltantes_por_aula(self, context: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Retorna un diccionario con los recursos faltantes por cada aula para una asignatura específica.

        Útil para mostrar al usuario qué recursos faltan en cada aula.

        :param context: Dict con asignatura_id, todas_aulas, asignaturas, recursos
        :return: Dict con aula_id como clave y lista de recursos faltantes como valor
        """
        asignatura_id = context.get("asignatura_id")
        todas_aulas = context.get("todas_aulas", [])
        asignaturas = context.get("asignaturas", [])
        recursos_disponibles = {r["id"]: r.get("nombre", r["id"]) for r in context.get("recursos", [])}

        if not asignatura_id:
            return {}

        # Buscar la asignatura
        asignatura = self._buscar_entidad_por_id(asignaturas, asignatura_id)
        if not asignatura:
            return {}

        requiere_recursos = set(asignatura.get("requiereRecursos", []))
        recursos_faltantes_por_aula = {}

        for aula in todas_aulas:
            aula_recursos = set(aula.get("id_recursos", []))
            faltantes = requiere_recursos - aula_recursos

            if faltantes:
                nombres_faltantes = [recursos_disponibles.get(rid, rid) for rid in faltantes]
                recursos_faltantes_por_aula[aula.get("id")] = nombres_faltantes

        return recursos_faltantes_por_aula

    def es_aula_compatible_con_asignatura(self, aula_id: str, asignatura_id: str, context: Dict[str, Any]) -> bool:
        """
        Verifica si un aula específica es compatible con una asignatura específica.

        Método de conveniencia para validaciones rápidas durante la generación automática.

        :param aula_id: ID del aula
        :param asignatura_id: ID de la asignatura
        :param context: Contexto con aulas, asignaturas y recursos
        :return: True si es compatible, False en caso contrario
        """
        aulas = context.get("aulas", [])
        asignaturas = context.get("asignaturas", [])

        aula = self._buscar_entidad_por_id(aulas, aula_id)
        asignatura = self._buscar_entidad_por_id(asignaturas, asignatura_id)

        if not aula or not asignatura:
            return False

        return self._validar_recursos_aula_asignatura(aula, asignatura, context) is None