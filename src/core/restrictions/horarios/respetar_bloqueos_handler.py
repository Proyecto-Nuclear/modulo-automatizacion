from typing import List, Dict, Optional, Any
from src.core.restrictions.restriction_handler import RestrictionHandler

class RespetarBloqueosHandler(RestrictionHandler):
    """
    Restricción: Un horario asignado a un aula no puede coincidir con un bloqueo para esa aula.

    Invariante OCL:
    Bloqueo.allInstances() -> forAll(b | self.aula <> b.aula or self.horaFin <= b.horario.horaInicio or b.horario.horaFin <= self.horaInicio)
    """

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Valida que ningún horario asignado a un aula se solape con un bloqueo de esa aula.

        Soporta:
        - Validación individual: 'nuevo_bloque' y 'bloqueos'
        - Validación global: 'schedules' y 'bloqueos'
        - Compatibilidad directa: 'schedule', 'bloqueos'

        :param context: Dict con las claves:
            - 'nuevo_bloque': Dict con el bloque a validar (opcional)
            - 'schedules': Lista de horarios a validar (opcional)
            - 'schedule': Lista de horarios (compatibilidad)
            - 'bloqueos': Lista de bloqueos
        :return: None si es válido, mensaje de error (str) si hay conflicto
        """
        if "nuevo_bloque" in context:
            return self._validar_bloque_individual(context)
        elif "schedules" in context or "schedule" in context:
            return self._validar_horarios_globales(context)
        else:
            return None  # No hay nada que validar

    def _validar_bloque_individual(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Valida un nuevo bloque contra los bloqueos existentes.
        """
        bloque = context["nuevo_bloque"]
        bloqueos = context.get("bloqueos", [])

        aula_bloque = bloque.get("aula_id") or bloque.get("aula")
        inicio_bloque = bloque.get("hora_inicio") or bloque.get("start_time")
        fin_bloque = bloque.get("hora_fin") or bloque.get("end_time")
        id_bloque = bloque.get("id", "")

        if not all([aula_bloque, inicio_bloque, fin_bloque]):
            return "El nuevo bloque debe tener aula, hora_inicio y hora_fin definidos."

        for bloqueo in bloqueos:
            aula_b = bloqueo.get("aula_id") or bloqueo.get("aula")
            horario_b = bloqueo.get("horario", bloqueo)
            inicio_b = horario_b.get("hora_inicio") or horario_b.get("start_time")
            fin_b = horario_b.get("hora_fin") or horario_b.get("end_time")

            if aula_bloque == aula_b:
                if not (fin_bloque <= inicio_b or fin_b <= inicio_bloque):
                    return (
                        f"Conflicto: El bloque '{id_bloque}' ({inicio_bloque}-{fin_bloque}) en el aula '{aula_bloque}' "
                        f"coincide con un bloqueo ({inicio_b}-{fin_b}) para esa aula."
                    )
        return None

    def _validar_horarios_globales(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Valida todos los horarios contra los bloqueos existentes.
        """
        horarios = context.get("schedules") or context.get("schedule", [])
        bloqueos = context.get("bloqueos", [])
        errores = []

        for h in horarios:
            aula_h = h.get("aula_id") or h.get("aula")
            inicio_h = h.get("hora_inicio") or h.get("start_time")
            fin_h = h.get("hora_fin") or h.get("end_time")
            id_h = h.get("id", "")

            if not all([aula_h, inicio_h, fin_h]):
                errores.append(f"El horario '{id_h}' debe tener aula, hora_inicio y hora_fin definidos.")
                continue

            for b in bloqueos:
                aula_b = b.get("aula_id") or b.get("aula")
                horario_b = b.get("horario", b)
                inicio_b = horario_b.get("hora_inicio") or horario_b.get("start_time")
                fin_b = horario_b.get("hora_fin") or horario_b.get("end_time")

                if aula_h == aula_b:
                    if not (fin_h <= inicio_b or fin_b <= inicio_h):
                        errores.append(
                            f"Conflicto: El horario '{id_h}' ({inicio_h}-{fin_h}) en el aula '{aula_h}' "
                            f"coincide con un bloqueo ({inicio_b}-{fin_b}) para esa aula."
                        )
        if errores:
            return "\n".join(errores)
        return None

    def hay_bloqueo(self, aula_id: str, hora_inicio: str, hora_fin: str, bloqueos: List[Dict]) -> bool:
        """
        Método auxiliar para saber si un aula está bloqueada en una franja horaria.
        """
        for bloqueo in bloqueos:
            aula_b = bloqueo.get("aula_id") or bloqueo.get("aula")
            horario_b = bloqueo.get("horario", bloqueo)
            inicio_b = horario_b.get("hora_inicio") or horario_b.get("start_time")
            fin_b = horario_b.get("hora_fin") or horario_b.get("end_time")
            if aula_id == aula_b:
                if not (hora_fin <= inicio_b or fin_b <= hora_inicio):
                    return True
        return False

    def obtener_bloqueos_conflictivos(self, context: Dict[str, Any]) -> List[Dict]:
        """
        Devuelve una lista de dicts con los horarios que tienen conflicto con bloqueos.
        """
        horarios = context.get("schedules") or context.get("schedule", [])
        bloqueos = context.get("bloqueos", [])
        conflictos = []

        for h in horarios:
            aula_h = h.get("aula_id") or h.get("aula")
            inicio_h = h.get("hora_inicio") or h.get("start_time")
            fin_h = h.get("hora_fin") or h.get("end_time")
            id_h = h.get("id", "")

            for b in bloqueos:
                aula_b = b.get("aula_id") or b.get("aula")
                horario_b = b.get("horario", b)
                inicio_b = horario_b.get("hora_inicio") or horario_b.get("start_time")
                fin_b = horario_b.get("hora_fin") or horario_b.get("end_time")

                if aula_h == aula_b:
                    if not (fin_h <= inicio_b or fin_b <= inicio_h):
                        conflictos.append({
                            "horario": h,
                            "bloqueo": b,
                            "mensaje": (
                                f"Conflicto: El horario '{id_h}' ({inicio_h}-{fin_h}) en el aula '{aula_h}' "
                                f"coincide con un bloqueo ({inicio_b}-{fin_b}) para esa aula."
                            )
                        })
        return conflictos