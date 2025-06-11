from typing import List, Dict, Optional, Any
from datetime import datetime, time
from src.core.restrictions.restriction_handler import RestrictionHandler

def horarios_solapan(h1: Dict, h2: Dict) -> bool:
    """
    Devuelve True si los horarios h1 y h2 se solapan temporalmente.

    Compara tanto el día como las horas de inicio y fin para determinar
    si existe conflicto temporal entre dos bloques horarios.

    :param h1: Primer horario con 'dia', 'hora_inicio', 'hora_fin' o 'start_time', 'end_time'
    :param h2: Segundo horario con 'dia', 'hora_inicio', 'hora_fin' o 'start_time', 'end_time'
    :return: True si los horarios se solapan, False en caso contrario
    """
    # Verificar que sean el mismo día (si aplica)
    dia1 = h1.get('dia')
    dia2 = h2.get('dia')

    # Si ambos tienen día definido, deben ser el mismo día para solaparse
    if dia1 and dia2 and dia1 != dia2:
        return False

    # Obtener horas de inicio y fin (soportar ambos formatos)
    inicio1 = h1.get('hora_inicio') or h1.get('start_time')
    fin1 = h1.get('hora_fin') or h1.get('end_time')
    inicio2 = h2.get('hora_inicio') or h2.get('start_time')
    fin2 = h2.get('hora_fin') or h2.get('end_time')

    # Verificar que todos los datos estén presentes
    if not all([inicio1, fin1, inicio2, fin2]):
        return False

    # Convertir a formato comparable si es necesario
    inicio1 = _normalize_time(inicio1)
    fin1 = _normalize_time(fin1)
    inicio2 = _normalize_time(inicio2)
    fin2 = _normalize_time(fin2)

    # Verificar solapamiento: NO se solapan si uno termina antes de que empiece el otro
    return not (fin1 <= inicio2 or fin2 <= inicio1)

def _normalize_time(time_value: Any) -> str:
    """
    Normaliza diferentes formatos de tiempo a un formato comparable.

    :param time_value: Valor de tiempo en diferentes formatos
    :return: Tiempo en formato string comparable (HH:MM)
    """
    if isinstance(time_value, str):
        return time_value
    elif isinstance(time_value, time):
        return time_value.strftime("%H:%M")
    elif isinstance(time_value, datetime):
        return time_value.strftime("%H:%M")
    else:
        return str(time_value)

class AulaNoOcupadaDobleHandler(RestrictionHandler):
    """
    Restricción: Un aula no puede tener dos clases diferentes al mismo tiempo.

    Invariante: Horario.allInstances() -> forAll(h1, h2 | h1 <> h2 and h1.aula = h2.aula
                implies h1.horaFin <= h2.horaInicio or h2.horaFin <= h1.horaInicio)

    Interpretación: No existe solapamiento temporal de clases en la misma aula.

    Esta restricción es fundamental para el Enfoque 2 ya que:
    - Valida cada nuevo bloque contra los bloques ya asignados
    - Permite la generación automática verificando disponibilidad en tiempo real
    - Soporta tanto validación individual como validación global del horario completo
    """

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Verifica que un aula no tenga dos asignaturas asignadas en horarios solapados.

        Soporta dos modos de validación:
        1. Validación individual: Verifica un nuevo bloque contra los existentes
        2. Validación global: Verifica todo el conjunto de horarios asignados

        :param context: Dict con las claves:
            Para validación individual:
            - 'nuevo_bloque': Dict con el nuevo bloque a validar
                - 'aula_id': ID del aula
                - 'dia': Día de la semana
                - 'hora_inicio': Hora de inicio
                - 'hora_fin': Hora de fin
                - 'asignatura_id': ID de la asignatura
            - 'horarios_existentes': Lista de bloques ya asignados

            Para validación global:
            - 'schedules' o 'horarios': Lista completa de horarios a validar

            Datos adicionales opcionales:
            - 'aulas': Lista de aulas para mostrar nombres en mensajes
            - 'asignaturas': Lista de asignaturas para mostrar nombres en mensajes

        :return: None si es válido, mensaje de error (str) si se detecta solapamiento
        """
        # Determinar modo de validación
        nuevo_bloque = context.get("nuevo_bloque")

        if nuevo_bloque:
            return self._validar_bloque_individual(context)
        else:
            return self._validar_horarios_globales(context)

    def _validar_bloque_individual(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Valida un nuevo bloque contra los horarios existentes.

        Este método es especialmente útil para el Enfoque 2 durante la generación
        automática, ya que permite validar cada bloque antes de agregarlo al horario.

        :param context: Contexto con nuevo_bloque y horarios_existentes
        :return: None si es válido, mensaje de error si hay conflicto
        """
        nuevo_bloque = context["nuevo_bloque"]
        horarios_existentes = context.get("horarios_existentes", [])

        # Validar datos del nuevo bloque
        if not self._validar_estructura_bloque(nuevo_bloque):
            return "El nuevo bloque no tiene la estructura requerida (aula_id, dia, hora_inicio, hora_fin)."

        aula_id = nuevo_bloque["aula_id"]

        # Buscar conflictos con horarios existentes en la misma aula
        for horario_existente in horarios_existentes:
            if not self._validar_estructura_bloque(horario_existente):
                continue  # Saltar horarios con estructura inválida

            # Solo verificar horarios de la misma aula
            if horario_existente.get("aula_id") == aula_id:
                if horarios_solapan(nuevo_bloque, horario_existente):
                    return self._generar_mensaje_conflicto_individual(
                        nuevo_bloque, horario_existente, context
                    )

        return None

    def _validar_horarios_globales(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Valida todo el conjunto de horarios para detectar solapamientos.

        Útil para validación final del horario completo generado automáticamente.

        :param context: Contexto con schedules o horarios
        :return: None si es válido, mensaje de error si hay conflictos
        """
        horarios = context.get("schedules") or context.get("horarios", [])

        if not horarios:
            return None  # No hay horarios que validar

        # Agrupar horarios por aula para optimizar la búsqueda
        aulas_horarios = self._agrupar_por_aula(horarios)

        # Verificar solapamientos en cada aula
        for aula_id, horarios_aula in aulas_horarios.items():
            conflicto = self._buscar_conflictos_en_aula(horarios_aula, context)
            if conflicto:
                return conflicto

        return None

    def _agrupar_por_aula(self, horarios: List[Dict]) -> Dict[Any, List[Dict]]:
        """
        Agrupa los horarios por aula para optimizar la búsqueda de conflictos.

        :param horarios: Lista de horarios
        :return: Diccionario con aula_id como clave y lista de horarios como valor
        """
        aulas_horarios = {}
        for horario in horarios:
            # Buscar el ID del aula en diferentes campos posibles
            aula_id = horario.get('aula_id') or horario.get('aula')
            if aula_id:
                aulas_horarios.setdefault(aula_id, []).append(horario)
        return aulas_horarios

    def _buscar_conflictos_en_aula(self, horarios_aula: List[Dict], context: Dict[str, Any]) -> Optional[str]:
        """
        Busca conflictos de solapamiento en los horarios de una aula específica.

        :param horarios_aula: Lista de horarios de la misma aula
        :param context: Contexto para generar mensajes descriptivos
        :return: Mensaje de error si hay conflicto, None si no hay conflictos
        """
        # Ordenar por día y hora para optimizar la búsqueda
        horarios_validos = [h for h in horarios_aula if self._validar_estructura_bloque(h)]
        horarios_ordenados = sorted(horarios_validos, key=lambda x: (x.get('dia', ''), x.get('hora_inicio', '')))

        n = len(horarios_ordenados)
        for i in range(n):
            h1 = horarios_ordenados[i]
            for j in range(i + 1, n):
                h2 = horarios_ordenados[j]

                # Si tienen IDs diferentes y se solapan, hay conflicto
                if (h1.get('id') != h2.get('id') and
                        h1.get('asignatura_id') != h2.get('asignatura_id') and
                        horarios_solapan(h1, h2)):

                    return self._generar_mensaje_conflicto_global(h1, h2, context)

        return None

    def _validar_estructura_bloque(self, bloque: Dict) -> bool:
        """
        Valida que un bloque tenga la estructura mínima requerida.

        :param bloque: Bloque horario a validar
        :return: True si tiene la estructura correcta, False en caso contrario
        """
        # Verificar campos de tiempo (soportar ambos formatos)
        campos_tiempo_nuevos = ['dia', 'hora_inicio', 'hora_fin']
        campos_tiempo_legacy = ['start_time', 'end_time']

        tiene_tiempo_nuevo = all(bloque.get(campo) for campo in campos_tiempo_nuevos)
        tiene_tiempo_legacy = all(bloque.get(campo) for campo in campos_tiempo_legacy)

        if not (tiene_tiempo_nuevo or tiene_tiempo_legacy):
            return False

        # Verificar que tenga al menos un campo de aula
        campos_aula = ['aula_id', 'aula']
        if not any(bloque.get(campo) for campo in campos_aula):
            return False

        return True

    def _generar_mensaje_conflicto_individual(self, nuevo_bloque: Dict, horario_existente: Dict, context: Dict[str, Any]) -> str:
        """
        Genera un mensaje descriptivo para conflictos en validación individual.

        :param nuevo_bloque: Nuevo bloque que causa conflicto
        :param horario_existente: Horario existente en conflicto
        :param context: Contexto con datos adicionales
        :return: Mensaje de error descriptivo
        """
        aula_nombre = self._obtener_nombre_aula(nuevo_bloque.get("aula_id"), context)
        asignatura_nueva = self._obtener_nombre_asignatura(nuevo_bloque.get("asignatura_id"), context)
        asignatura_existente = self._obtener_nombre_asignatura(horario_existente.get("asignatura_id"), context)

        return (
            f"Conflicto de horario detectado en {aula_nombre}: "
            f"La asignatura '{asignatura_nueva}' "
            f"({nuevo_bloque.get('dia')} {nuevo_bloque.get('hora_inicio')}-{nuevo_bloque.get('hora_fin')}) "
            f"se solapa con '{asignatura_existente}' "
            f"({horario_existente.get('dia')} {horario_existente.get('hora_inicio')}-{horario_existente.get('hora_fin')})."
        )

    def _generar_mensaje_conflicto_global(self, h1: Dict, h2: Dict, context: Dict[str, Any]) -> str:
        """
        Genera un mensaje descriptivo para conflictos en validación global.

        :param h1: Primer horario en conflicto
        :param h2: Segundo horario en conflicto
        :param context: Contexto con datos adicionales
        :return: Mensaje de error descriptivo
        """
        aula_id = h1.get('aula_id') or h1.get('aula')
        aula_nombre = self._obtener_nombre_aula(aula_id, context)

        asignatura1 = self._obtener_nombre_asignatura(h1.get("asignatura_id"), context)
        asignatura2 = self._obtener_nombre_asignatura(h2.get("asignatura_id"), context)

        return (
            f"Conflicto: Solapamiento de clases en {aula_nombre}: "
            f"'{asignatura1}' ({h1.get('dia')} {h1.get('hora_inicio')}-{h1.get('hora_fin')}) "
            f"se solapa con '{asignatura2}' ({h2.get('dia')} {h2.get('hora_inicio')}-{h2.get('hora_fin')})."
        )

    def _obtener_nombre_aula(self, aula_id: Any, context: Dict[str, Any]) -> str:
        """
        Obtiene el nombre descriptivo de un aula.

        :param aula_id: ID del aula
        :param context: Contexto que puede contener lista de aulas
        :return: Nombre del aula o ID si no se encuentra
        """
        aulas = context.get("aulas", [])
        for aula in aulas:
            if aula.get("id") == aula_id:
                return f"aula '{aula.get('nombre', aula_id)}'"
        return f"aula {aula_id}"

    def _obtener_nombre_asignatura(self, asignatura_id: Any, context: Dict[str, Any]) -> str:
        """
        Obtiene el nombre descriptivo de una asignatura.

        :param asignatura_id: ID de la asignatura
        :param context: Contexto que puede contener lista de asignaturas
        :return: Nombre de la asignatura o ID si no se encuentra
        """
        asignaturas = context.get("asignaturas", [])
        for asignatura in asignaturas:
            if asignatura.get("id") == asignatura_id:
                return asignatura.get("nombre", asignatura_id)
        return str(asignatura_id) if asignatura_id else "Asignatura desconocida"

    def obtener_aulas_disponibles(self, context: Dict[str, Any]) -> List[str]:
        """
        Método auxiliar que retorna las aulas disponibles para un bloque específico.

        Útil para el sistema de generación automática de horarios del Enfoque 2.

        :param context: Dict con las claves:
            - 'bloque_solicitado': Dict con dia, hora_inicio, hora_fin
            - 'todas_aulas': Lista de todas las aulas
            - 'horarios_existentes': Lista de horarios ya asignados
        :return: Lista de IDs de aulas disponibles
        """
        bloque_solicitado = context.get("bloque_solicitado", {})
        todas_aulas = context.get("todas_aulas", [])
        horarios_existentes = context.get("horarios_existentes", [])

        aulas_disponibles = []

        for aula in todas_aulas:
            aula_id = aula.get("id")

            # Crear contexto temporal para validar esta aula
            temp_context = {
                "nuevo_bloque": {
                    **bloque_solicitado,
                    "aula_id": aula_id
                },
                "horarios_existentes": horarios_existentes
            }

            # Si la validación retorna None, el aula está disponible
            if self._validar_bloque_individual(temp_context) is None:
                aulas_disponibles.append(aula_id)

        return aulas_disponibles