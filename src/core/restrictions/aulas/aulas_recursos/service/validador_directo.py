from typing import Dict, Optional, Any
from .validador_recursos import ValidadorRecursos


class ValidadorDirecto:
    """Validación directa con aula y asignatura proporcionadas directamente."""

    def __init__(self):
        self.validador_recursos = ValidadorRecursos()

    def validar(self, context: Dict[str, Any]) -> Optional[str]:
        """Validación directa con aula y asignatura proporcionadas directamente."""
        aula = context["aula"]
        asignatura = context["asignatura"]

        return self.validador_recursos.validar_recursos_aula_asignatura(aula, asignatura, context)