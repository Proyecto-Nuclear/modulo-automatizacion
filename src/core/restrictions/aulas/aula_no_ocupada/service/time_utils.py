from typing import Any
from datetime import datetime, time

def horarios_solapan(h1: dict, h2: dict) -> bool:
    """
    Devuelve True si los horarios h1 y h2 se solapan temporalmente.
    """
    # Verificar que sean el mismo día (si aplica)
    dia1 = h1.get('dia')
    dia2 = h2.get('dia')

    if dia1 and dia2 and dia1 != dia2:
        return False

    # Obtener horas de inicio y fin (soportar ambos formatos)
    inicio1 = h1.get('hora_inicio') or h1.get('start_time')
    fin1 = h1.get('hora_fin') or h1.get('end_time')
    inicio2 = h2.get('hora_inicio') or h2.get('start_time')
    fin2 = h2.get('hora_fin') or h2.get('end_time')

    if not all([inicio1, fin1, inicio2, fin2]):
        return False

    # Convertir a formato comparable si es necesario
    inicio1 = normalize_time(inicio1)
    fin1 = normalize_time(fin1)
    inicio2 = normalize_time(inicio2)
    fin2 = normalize_time(fin2)

    # Verificar solapamiento
    return not (fin1 <= inicio2 or fin2 <= inicio1)

def normalize_time(time_value: Any) -> str:
    """
    Normaliza diferentes formatos de tiempo a un formato comparable.
    """
    if isinstance(time_value, str):
        return time_value
    elif isinstance(time_value, time):
        return time_value.strftime("%H:%M")
    elif isinstance(time_value, datetime):
        return time_value.strftime("%H:%M")
    else:
        return str(time_value)