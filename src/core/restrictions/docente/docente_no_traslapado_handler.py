from typing import List, Dict, Optional, Any
from src.core.restrictions.restriction_handler import RestrictionHandler

class DocenteNoTraslapadoHandler(RestrictionHandler):
    """
    Restricción: Un profesor no puede tener dos clases asignadas al mismo tiempo (sin superposición de horarios).

    Invariante: Horario.allInstances() -> forAll(h1, h2 | h1 <> h2 and h1.docente = h2.docente
                implies h1.horaFin <= h2.horaInicio or h2.horaFin <= h1.horaInicio)

    Interpretación: No existe par de horarios distintos con el mismo docente y con traslape de tiempo.

    Esta restricción es esencial para el Enfoque 2 ya que:
    - Valida cada nuevo bloque contra los horarios existentes del docente
    - Permite detectar conflictos de horarios durante la generación automática
    - Soporta tanto validación individual como validación global del horario completo
    - Facilita la identificación de docentes disponibles en franjas horarias específicas
    """

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Verifica que un docente no tenga dos clases asignadas que se traslapen en el mismo horario.

        Soporta tres modos de validación:
        1. Validación individual: Verifica un nuevo bloque contra horarios existentes
        2. Validación global: Verifica todo el conjunto de horarios asignados
        3. Validación directa: Compatibilidad con versión anterior

        :param context: Dict con las claves:
            Para validación individual:
            - 'nuevo_bloque': Dict con el nuevo bloque a validar
                - 'docente_id': ID del docente
                - 'dia': Día de la semana
                - 'hora_inicio': Hora de inicio (formato HH:MM)
                - 'hora_fin': Hora de fin (formato HH:MM)
            - 'horarios_existentes': Lista de horarios ya asignados
            - 'docentes': Lista de docentes (opcional, para nombres descriptivos)

            Para validación global:
            - 'schedules' o 'horarios': Lista completa de horarios a validar
            - 'docentes': Lista de docentes (opcional)

            Para validación directa (compatibilidad):
            - 'schedule': Lista de horarios existentes
            - 'new_schedule': Nuevo horario a validar
            - 'docentes': Lista de docentes (opcional)

        :return: None si es válido, mensaje de error (str) si hay traslape de horarios
        """
        # Determinar modo de validación
        nuevo_bloque = context.get("nuevo_bloque")
        schedule_directo = context.get("schedule")

        if nuevo_bloque:
            return self._validar_bloque_individual(context)
        elif schedule_directo:
            return self._validar_directo(context)
        else:
            return self._validar_horarios_globales(context)

    def _validar_bloque_individual(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Valida un nuevo bloque contra los horarios existentes del docente.

        Este método es especialmente útil para el Enfoque 2 durante la generación
        automática, ya que permite validar cada bloque antes de agregarlo al horario.

        :param context: Contexto con nuevo_bloque y horarios_existentes
        :return: None si es válido, mensaje de error si hay traslape
        """
        nuevo_bloque = context["nuevo_bloque"]
        horarios_existentes = context.get("horarios_existentes", [])
        docentes = context.get("docentes", [])

        # Validar datos del nuevo bloque
        docente_id = nuevo_bloque.get("docente_id")
        dia = nuevo_bloque.get("dia")
        hora_inicio = nuevo_bloque.get("hora_inicio")
        hora_fin = nuevo_bloque.get("hora_fin")

        if not all([docente_id, dia, hora_inicio, hora_fin]):
            return "El nuevo bloque debe tener docente_id, dia, hora_inicio y hora_fin definidos."

        # Buscar conflictos con horarios existentes del mismo docente
        for horario in horarios_existentes:
            if self._hay_conflicto_horario(nuevo_bloque, horario):
                return self._generar_mensaje_conflicto(docente_id, nuevo_bloque, horario, docentes)

        return None

    def _validar_horarios_globales(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Valida todo el conjunto de horarios para detectar traslapes de docentes.

        Útil para validación final del horario completo generado automáticamente.

        :param context: Contexto con schedules/horarios y docentes
        :return: None si es válido, mensaje de error si hay traslapes
        """
        horarios = context.get("schedules") or context.get("horarios", [])
        docentes = context.get("docentes", [])

        if not horarios:
            return None  # No hay horarios que validar

        # Comparar cada par de horarios
        for i, horario1 in enumerate(horarios):
            for j, horario2 in enumerate(horarios[i+1:], i+1):
                if self._hay_conflicto_horario(horario1, horario2):
                    docente_id = horario1.get('docente_id') or horario1.get('docente')
                    return self._generar_mensaje_conflicto(docente_id, horario1, horario2, docentes)

        return None

    def _validar_directo(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Validación directa con schedule y new_schedule proporcionados directamente.

        Mantiene compatibilidad con la versión anterior del handler.

        :param context: Contexto con schedule, new_schedule y docentes
        :return: None si es válido, mensaje de error si hay traslape
        """
        schedules = context["schedule"]
        new_schedule = context["new_schedule"]
        docentes = context.get("docentes", [])

        # Convertir al formato del nuevo enfoque para reutilizar lógica
        nuevo_bloque = {
            "docente_id": new_schedule.get("docente_id"),
            "dia": new_schedule.get("date") or new_schedule.get("dia"),
            "hora_inicio": new_schedule.get("start_time") or new_schedule.get("hora_inicio"),
            "hora_fin": new_schedule.get("end_time") or new_schedule.get("hora_fin")
        }

        # Convertir schedules existentes al formato nuevo
        horarios_existentes = []
        for schedule in schedules:
            horario = {
                "docente_id": schedule.get("docente_id"),
                "dia": schedule.get("date") or schedule.get("dia"),
                "hora_inicio": schedule.get("start_time") or schedule.get("hora_inicio"),
                "hora_fin": schedule.get("end_time") or schedule.get("hora_fin")
            }
            horarios_existentes.append(horario)

        # Reutilizar lógica de validación individual
        temp_context = {
            "nuevo_bloque": nuevo_bloque,
            "horarios_existentes": horarios_existentes,
            "docentes": docentes
        }

        return self._validar_bloque_individual(temp_context)

    def _hay_conflicto_horario(self, horario1: Dict, horario2: Dict) -> bool:
        """
        Determina si dos horarios tienen conflicto (mismo docente, mismo día, horarios traslapados).

        :param horario1: Primer horario
        :param horario2: Segundo horario
        :return: True si hay conflicto, False en caso contrario
        """
        # Obtener IDs de docentes (soporta diferentes formatos de campo)
        docente1 = horario1.get("docente_id") or horario1.get("docente")
        docente2 = horario2.get("docente_id") or horario2.get("docente")

        # Si no son el mismo docente, no hay conflicto
        if docente1 != docente2:
            return False

        # Obtener días (soporta diferentes formatos de campo)
        dia1 = horario1.get("dia") or horario1.get("date")
        dia2 = horario2.get("dia") or horario2.get("date")

        # Si no son el mismo día, no hay conflicto
        if dia1 != dia2:
            return False

        # Obtener horas (soporta diferentes formatos de campo)
        inicio1 = horario1.get("hora_inicio") or horario1.get("start_time")
        fin1 = horario1.get("hora_fin") or horario1.get("end_time")
        inicio2 = horario2.get("hora_inicio") or horario2.get("start_time")
        fin2 = horario2.get("hora_fin") or horario2.get("end_time")

        # Verificar traslape de horarios
        # No hay traslape si: fin1 <= inicio2 OR fin2 <= inicio1
        # Hay traslape si: NOT (fin1 <= inicio2 OR fin2 <= inicio1)
        return not (fin1 <= inicio2 or fin2 <= inicio1)

    def _generar_mensaje_conflicto(self, docente_id: str, horario1: Dict, horario2: Dict, docentes: List[Dict]) -> str:
        """
        Genera un mensaje descriptivo para conflictos de horarios.

        :param docente_id: ID del docente en conflicto
        :param horario1: Primer horario en conflicto
        :param horario2: Segundo horario en conflicto
        :param docentes: Lista de docentes para obtener nombres
        :return: Mensaje de error descriptivo
        """
        nombre_docente = self._obtener_nombre_docente(docente_id, docentes)

        # Obtener datos del primer horario (existente)
        dia1 = horario1.get("dia") or horario1.get("date", "N/A")
        inicio1 = horario1.get("hora_inicio") or horario1.get("start_time", "N/A")
        fin1 = horario1.get("hora_fin") or horario1.get("end_time", "N/A")

        # Obtener datos del segundo horario (nuevo)
        dia2 = horario2.get("dia") or horario2.get("date", "N/A")
        inicio2 = horario2.get("hora_inicio") or horario2.get("start_time", "N/A")
        fin2 = horario2.get("hora_fin") or horario2.get("end_time", "N/A")

        return (
            f"Conflicto: El docente {nombre_docente} ya tiene una clase asignada "
            f"el {dia1} de {inicio1} a {fin1}, que se traslapa con el nuevo horario "
            f"del {dia2} de {inicio2} a {fin2}."
        )

    def _obtener_nombre_docente(self, docente_id: str, docentes: List[Dict]) -> str:
        """
        Obtiene el nombre completo de un docente por su ID.

        :param docente_id: ID del docente
        :param docentes: Lista de docentes
        :return: Nombre completo del docente o su ID si no se encuentra
        """
        docente = next((d for d in docentes if d.get("id") == docente_id), None)
        if docente:
            nombre = docente.get("nombre", "")
            apellido = docente.get("apellido", "")
            return f"{nombre} {apellido}".strip() or docente_id
        return docente_id

    def obtener_docentes_disponibles(self, context: Dict[str, Any]) -> List[str]:
        """
        Método auxiliar que retorna los docentes disponibles en una franja horaria específica.

        Útil para el sistema de generación automática de horarios del Enfoque 2.

        :param context: Dict con las claves:
            - 'dia': Día de la semana
            - 'hora_inicio': Hora de inicio
            - 'hora_fin': Hora de fin
            - 'todos_docentes': Lista de todos los docentes
            - 'horarios_existentes': Lista de horarios ya asignados
        :return: Lista de IDs de docentes disponibles
        """
        dia = context.get("dia")
        hora_inicio = context.get("hora_inicio")
        hora_fin = context.get("hora_fin")
        todos_docentes = context.get("todos_docentes", [])
        horarios_existentes = context.get("horarios_existentes", [])

        if not all([dia, hora_inicio, hora_fin]):
            return []

        docentes_disponibles = []

        for docente in todos_docentes:
            docente_id = docente.get("id")
            if not docente_id:
                continue

            # Crear horario temporal para verificar conflictos
            horario_temporal = {
                "docente_id": docente_id,
                "dia": dia,
                "hora_inicio": hora_inicio,
                "hora_fin": hora_fin
            }

            # Verificar si hay conflicto con horarios existentes
            tiene_conflicto = False
            for horario_existente in horarios_existentes:
                if self._hay_conflicto_horario(horario_temporal, horario_existente):
                    tiene_conflicto = True
                    break

            if not tiene_conflicto:
                docentes_disponibles.append(docente_id)

        return docentes_disponibles

    def es_docente_disponible(self, docente_id: str, dia: str, hora_inicio: str, hora_fin: str, context: Dict[str, Any]) -> bool:
        """
        Verifica si un docente específico está disponible en una franja horaria.

        Método de conveniencia para validaciones rápidas durante la generación automática.

        :param docente_id: ID del docente
        :param dia: Día de la semana
        :param hora_inicio: Hora de inicio
        :param hora_fin: Hora de fin
        :param context: Contexto con horarios_existentes
        :return: True si está disponible, False en caso contrario
        """
        horarios_existentes = context.get("horarios_existentes", [])

        # Crear horario temporal
        horario_temporal = {
            "docente_id": docente_id,
            "dia": dia,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin
        }

        # Verificar conflictos
        for horario_existente in horarios_existentes:
            if self._hay_conflicto_horario(horario_temporal, horario_existente):
                return False

        return True

    def obtener_conflictos_docente(self, context: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Retorna un diccionario con los conflictos de horarios por docente.

        Útil para análisis y depuración de horarios.

        :param context: Dict con horarios y docentes
        :return: Dict con docente_id como clave y lista de conflictos como valor
        """
        horarios = context.get("schedules") or context.get("horarios", [])
        docentes = context.get("docentes", [])

        conflictos_por_docente = {}

        # Comparar cada par de horarios
        for i, horario1 in enumerate(horarios):
            for j, horario2 in enumerate(horarios[i+1:], i+1):
                if self._hay_conflicto_horario(horario1, horario2):
                    docente_id = horario1.get('docente_id') or horario1.get('docente')

                    if docente_id not in conflictos_por_docente:
                        conflictos_por_docente[docente_id] = []

                    conflicto = {
                        "horario1": horario1,
                        "horario2": horario2,
                        "mensaje": self._generar_mensaje_conflicto(docente_id, horario1, horario2, docentes)
                    }

                    conflictos_por_docente[docente_id].append(conflicto)

        return conflictos_por_docente