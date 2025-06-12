from typing import List, Dict, Optional, Any

def buscar_entidad_por_id(entidades: List[Dict], entity_id: Any) -> Optional[Dict]:
    """
    Busca una entidad por su ID en una lista.

    :param entidades: Lista de entidades
    :param entity_id: ID a buscar
    :return: Entidad encontrada o None
    """
    for entidad in entidades:
        if entidad.get("id") == entity_id:
            return entidad
    return None

def buscar_multiples_entidades_por_ids(entidades: List[Dict], entity_ids: List[Any]) -> List[Dict]:
    """
    Busca múltiples entidades por sus IDs.

    :param entidades: Lista de entidades
    :param entity_ids: Lista de IDs a buscar
    :return: Lista de entidades encontradas
    """
    return [entidad for entidad in entidades if entidad.get("id") in entity_ids]