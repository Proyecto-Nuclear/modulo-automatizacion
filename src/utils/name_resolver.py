from typing import Dict, Any, List

def obtener_nombre_aula(aula_id: Any, context: Dict[str, Any]) -> str:
    """Obtiene el nombre descriptivo de un aula."""
    aulas = context.get("aulas", [])
    for aula in aulas:
        if aula.get("id") == aula_id:
            return f"aula '{aula.get('nombre', aula_id)}'"
    return f"aula {aula_id}"

def obtener_nombre_asignatura(asignatura_id: Any, context: Dict[str, Any]) -> str:
    """Obtiene el nombre descriptivo de una asignatura."""
    asignaturas = context.get("asignaturas", [])
    for asignatura in asignaturas:
        if asignatura.get("id") == asignatura_id:
            return asignatura.get("nombre", asignatura_id)
    return str(asignatura_id) if asignatura_id else "Asignatura desconocida"

def obtener_nombre_recurso(recurso_id: Any, context: Dict[str, Any]) -> str:
    """Obtiene el nombre descriptivo de un recurso."""
    recursos = context.get("recursos", [])
    for recurso in recursos:
        if recurso.get("id") == recurso_id:
            return recurso.get("nombre", recurso_id)
    return str(recurso_id) if recurso_id else "Recurso desconocido"

def obtener_nombres_recursos(recurso_ids: List[Any], context: Dict[str, Any]) -> List[str]:
    """Obtiene los nombres descriptivos de múltiples recursos."""
    return [obtener_nombre_recurso(rid, context) for rid in recurso_ids]