from typing import Optional

class ReglasCompatibilidad:
    """Define las reglas de compatibilidad entre tipos de asignatura y aula."""

    # Tipos de asignatura permitidos
    TIPOS_ASIGNATURA = {"laboratorio", "teorica", "hibrida"}

    # Diccionario de reglas: (tipo_asignatura, tipo_aula) -> mensaje de error
    REGLAS = {
        ("laboratorio", lambda tipo_aula: tipo_aula != "laboratorio"): "Las asignaturas de laboratorio requieren aulas de tipo laboratorio.",
        ("hibrida", lambda tipo_aula: tipo_aula not in ["hibrida", "laboratorio"]): "Las asignaturas híbridas requieren aulas híbridas o de laboratorio.",
        ("teorica", lambda tipo_aula: tipo_aula in ["laboratorio_especializado", "quirofano", "laboratorio_quimica"]): "Las asignaturas teóricas no deberían usar laboratorios especializados."
    }

    @staticmethod
    def verificar_incompatibilidades(tipo_asignatura: str, tipo_aula: str) -> Optional[str]:
        """
        Verifica las reglas de incompatibilidad entre tipos de asignatura y aula.

        :param tipo_asignatura: Tipo de la asignatura (normalizado)
        :param tipo_aula: Tipo del aula (normalizado)
        :return: Mensaje de incompatibilidad o None si son compatibles
        """
        if tipo_asignatura not in ReglasCompatibilidad.TIPOS_ASIGNATURA:
            return f"Tipo de asignatura no válido: {tipo_asignatura}"

        for (asignatura_regla, condicion), mensaje in ReglasCompatibilidad.REGLAS.items():
            if tipo_asignatura == asignatura_regla and condicion(tipo_aula):
                return mensaje

        return None