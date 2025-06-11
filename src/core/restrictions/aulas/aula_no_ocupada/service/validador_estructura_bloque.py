from typing import Dict


class ValidadorEstructuraBloque:
    """Valida que los bloques horarios tengan la estructura correcta."""

    @staticmethod
    def validar(bloque: Dict) -> bool:
        """
        Valida que un bloque tenga la estructura mínima requerida.
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