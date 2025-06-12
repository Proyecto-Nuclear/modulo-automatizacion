from typing import Dict, List, Any


def validar_estructura_basica_bloque(bloque: Dict, campos_requeridos: List[str]) -> bool:
    """
    Valida que un bloque tenga los campos requeridos.

    :param bloque: Bloque a validar
    :param campos_requeridos: Lista de campos que deben estar presentes
    :return: True si tiene todos los campos, False en caso contrario
    """
    return all(bloque.get(campo) for campo in campos_requeridos)


def extraer_horarios_de_context(context: Dict[str, Any]) -> List[Dict]:
    """
    Extrae la lista de horarios del contexto, soportando diferentes formatos.

    :param context: Contexto que puede contener 'schedules' o 'horarios'
    :return: Lista de horarios
    """
    return context.get("schedules") or context.get("horarios", [])