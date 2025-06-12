from typing import Dict, Any

class GestorEstadisticas:
    """Gestiona las estadísticas del sistema de horarios."""

    def __init__(self):
        """Inicializa el gestor de estadísticas."""
        self.stats = {
            'horarios_creados': 0,
            'validaciones_exitosas': 0,
            'validaciones_fallidas': 0,
            'restricciones_violadas': {},
            'tipos_horarios_creados': {}
        }

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas de uso del sistema."""
        return {'estadisticas': self.stats.copy()}

    def reiniciar_estadisticas(self) -> None:
        """Reinicia las estadísticas."""
        self.stats = {
            'horarios_creados': 0,
            'validaciones_exitosas': 0,
            'validaciones_fallidas': 0,
            'restricciones_violadas': {},
            'tipos_horarios_creados': {}
        }

    def _update_stats(self, stat_name: str) -> None:
        """Actualiza una estadística específica."""
        if stat_name in self.stats:
            self.stats[stat_name] += 1

    def _update_type_stats(self, tipo: str) -> None:
        """Actualiza estadísticas por tipo de horario."""
        if tipo not in self.stats['tipos_horarios_creados']:
            self.stats['tipos_horarios_creados'][tipo] = 0
        self.stats['tipos_horarios_creados'][tipo] += 1

    def _update_restriction_stats(self, error: str) -> None:
        """Actualiza estadísticas de restricciones violadas."""
        restriction_type = 'general'
        if 'docente' in error.lower():
            restriction_type = 'docente'
        elif 'aula' in error.lower():
            restriction_type = 'aula'
        elif 'bloqueo' in error.lower():
            restriction_type = 'bloqueo'
        elif 'integridad' in error.lower():
            restriction_type = 'integridad'

        if restriction_type not in self.stats['restricciones_violadas']:
            self.stats['restricciones_violadas'][restriction_type] = 0
        self.stats['restricciones_violadas'][restriction_type] += 1