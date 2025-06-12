from typing import List, Any, Union, Dict
import json

class ExportadorHorarios:
    """Gestiona la exportación de horarios en diferentes formatos."""

    def exportar_horarios(self, horarios: List[Any], formato: str = 'json') -> Union[str, Dict, List]:
        """Exporta horarios en diferentes formatos."""
        if formato == 'dict':
            return [h.to_dict() if hasattr(h, 'to_dict') else h for h in horarios]

        elif formato == 'json':
            horarios_dict = [h.to_dict() if hasattr(h, 'to_dict') else h for h in horarios]
            return json.dumps(horarios_dict, indent=2, ensure_ascii=False)

        elif formato == 'csv_data':
            csv_data = []
            for horario in horarios:
                if hasattr(horario, 'to_dict'):
                    h_dict = horario.to_dict()
                    csv_data.append({
                        'id': h_dict.get('id', ''),
                        'tipo': h_dict.get('tipo', ''),
                        'docente': h_dict.get('docente', {}).get('nombre', ''),
                        'aula': h_dict.get('aula', {}).get('nombre', ''),
                        'asignatura': h_dict.get('asignatura', {}).get('nombre', ''),
                        'dia': h_dict.get('dia', ''),
                        'inicio': h_dict.get('start_time', ''),
                        'fin': h_dict.get('end_time', ''),
                        'sede': h_dict.get('sede', {}).get('nombre', '')
                    })
            return csv_data

        else:
            raise ValueError(f"Formato '{formato}' no soportado")