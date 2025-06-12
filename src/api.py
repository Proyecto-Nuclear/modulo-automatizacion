from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from src.services.aula_disponible_service import AulaDisponibleService
from src.models.aula_request import AulaDisponibleRequest, AulaDisponibleResponse

router = APIRouter()

# Dependency injection para el servicio
def get_aula_service() -> AulaDisponibleService:
    return AulaDisponibleService()

@router.get("/")
def read_root():
    return {"message": "Sistema de Gestión de Horarios - API v1.0"}

@router.post("/aulas-disponibles", response_model=AulaDisponibleResponse)
def obtener_aulas_disponibles(
        request: AulaDisponibleRequest,
        service: AulaDisponibleService = Depends(get_aula_service)
) -> Dict[str, Any]:
    """
    Obtiene las aulas disponibles para una asignatura en un horario específico.

    Este endpoint aplica todas las restricciones definidas:
    - Capacidad suficiente para los estudiantes
    - Compatibilidad de tipo de aula con la asignatura
    - Disponibilidad (no ocupada por otra clase)

    Args:
        request: Datos de la solicitud (asignatura, horario, estudiantes, etc.)

    Returns:
        Lista de aulas disponibles y no disponibles con sus razones

    Raises:
        HTTPException: Si hay errores en la validación o procesamiento
        :param request:
        :param service:
    """
    try:
        resultado = service.get_aulas_disponibles(
            asignatura_id=request.asignatura_id,
            hora_inicio=request.hora_inicio,
            hora_fin=request.hora_fin,
            dia=request.dia,
            cantidad_estudiantes=request.cantidad_estudiantes,
            semestre=request.semestre
        )

        if 'error' in resultado and resultado['error']:
            raise HTTPException(status_code=404, detail=resultado['error'])

        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/health")
def health_check():
    """Endpoint de salud para verificar que la API está funcionando."""
    return {
        "status": "healthy",
        "service": "Gestión de Horarios",
        "version": "1.0.0"
    }