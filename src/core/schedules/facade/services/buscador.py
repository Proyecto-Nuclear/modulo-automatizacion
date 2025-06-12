from typing import Dict, List, Any

class BuscadorHorarios:
    """Gestiona la búsqueda de horarios."""

    def buscar_horarios_docente(self, docente_id: str, horarios: List[Any]) -> List[Any]:
        """Busca todos los horarios asignados a un docente específico."""
        horarios_docente = []
        for horario in horarios:
            if hasattr(horario, 'docente') and horario.docente.get('id') == docente_id:
                horarios_docente.append(horario)
        return horarios_docente

    def buscar_horarios_aula(self, aula_id: str, horarios: List[Any]) -> List[Any]:
        """Busca todos los horarios asignados a un aula específica."""
        horarios_aula = []
        for horario in horarios:
            if hasattr(horario, 'aula') and horario.aula.get('id') == aula_id:
                horarios_aula.append(horario)
        return horarios_aula

    def buscar_horarios_dia(self, dia: str, horarios: List[Any]) -> List[Any]:
        """Busca todos los horarios de un día específico."""
        horarios_dia = []
        for horario in horarios:
            if hasattr(horario, 'dia') and horario.dia.lower() == dia.lower():
                horarios_dia.append(horario)
        return horarios_dia