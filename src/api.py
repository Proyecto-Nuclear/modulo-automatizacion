import json
import os

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List

from src.services.aula_disponible_service import AulaDisponibleService
from src.models.aula_request import AulaDisponibleRequest, AulaDisponibleResponse, ReservaAulaRequest
from src.services.horario_completo_service import HorarioCompletoService
from src.services.reserva_aulas_service import ReservaAulaService

router = APIRouter()

# Dependency injection para el servicio
def get_aula_service() -> AulaDisponibleService:
    return AulaDisponibleService()

def get_reserva_service() -> ReservaAulaService:
    return ReservaAulaService()

def load_json(filename: str) -> List[Dict[str, Any]]:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, '../data'))
    with open(os.path.join(data_dir, filename), encoding="utf-8") as f:
        return json.load(f)

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

async def verificar_aula_disponible(
        asignatura_id: str,
        aula_id: str,
        hora_inicio: str,
        hora_fin: str,
        dia: str,
        cantidad_estudiantes: int,
        semestre: int,
        service: AulaDisponibleService
) -> bool:
    """
    Verifica si un aula específica está disponible para una asignatura.

    Args:
        asignatura_id: ID de la asignatura
        aula_id: ID del aula a verificar
        hora_inicio: Hora de inicio
        hora_fin: Hora de fin
        dia: Día de la semana
        cantidad_estudiantes: Cantidad de estudiantes
        semestre: Semestre
        service: Servicio de aulas disponibles

    Returns:
        True si el aula está disponible, False en caso contrario
    """
    try:
        resultado = service.get_aulas_disponibles(
            asignatura_id=asignatura_id,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            dia=dia,
            cantidad_estudiantes=cantidad_estudiantes,
            semestre=semestre
        )

        # Verificar si el aula está en la lista de aulas disponibles
        aulas_disponibles = resultado.get("aulas_disponibles", [])
        return any(aula["id"] == aula_id for aula in aulas_disponibles)

    except Exception:
        return False

@router.post("/reservar-aula")
async def reservar_aula(
        request: ReservaAulaRequest,
        aula_service: AulaDisponibleService = Depends(get_aula_service),
        reserva_service: ReservaAulaService = Depends(get_reserva_service)
):
    """
    Reserva un aula para una asignatura específica.

    Antes de realizar la reserva, verifica que el aula esté realmente disponible
    para esa asignatura en el horario solicitado.

    Args:
        request: Datos de la reserva
        aula_service: Servicio para verificar disponibilidad
        reserva_service: Servicio para realizar la reserva

    Returns:
        Resultado de la reserva

    Raises:
        HTTPException: Si el aula no está disponible o hay errores
    """
    try:
        # Verificar si el aula está disponible para esta asignatura
        # Necesitamos obtener datos adicionales de la asignatura para la verificación
        aula_disponible = await verificar_aula_disponible(
            asignatura_id=request.asignatura_id,
            aula_id=request.aula_id,
            hora_inicio=request.hora_inicio,
            hora_fin=request.hora_fin,
            dia=request.dia,
            cantidad_estudiantes=request.cantidad_estudiantes,  # Valor por defecto, puedes ajustarlo
            semestre=request.semestre,  # Valor por defecto, puedes ajustarlo
            service=aula_service
        )

        if not aula_disponible:
            raise HTTPException(
                status_code=400,
                detail="El aula seleccionada no está disponible para esta asignatura y horario. "
                       "Verifique las restricciones de capacidad, compatibilidad y disponibilidad."
            )

        # Si el aula está disponible, proceder con la reserva
        result = reserva_service.reservar_aula(request.dict(), request.id_usuario)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/programaciones")
def obtener_programaciones(reserva_service: ReservaAulaService = Depends(get_reserva_service)):
    """
    Obtiene todas las programaciones/reservas existentes.

    Returns:
        Lista de todas las programaciones
    """
    try:
        programaciones = reserva_service.obtener_todas_programaciones()
        return {
            "programaciones": programaciones,
            "total": len(programaciones)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/programaciones/{programacion_id}")
def obtener_programacion(
        programacion_id: str,
        reserva_service: ReservaAulaService = Depends(get_reserva_service)
):
    """
    Obtiene una programación específica por ID.

    Args:
        programacion_id: ID de la programación

    Returns:
        Datos de la programación
    """
    try:
        programacion = reserva_service.obtener_programacion_por_id(programacion_id)
        if not programacion:
            raise HTTPException(status_code=404, detail="Programación no encontrada")
        return programacion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.put("/programaciones/{programacion_id}/estado")
def cambiar_estado_programacion(
        programacion_id: str,
        nuevo_estado: str,
        reserva_service: ReservaAulaService = Depends(get_reserva_service)
):
    """
    Cambia el estado de una programación (reservado -> ocupado -> cancelado).

    Args:
        programacion_id: ID de la programación
        nuevo_estado: Nuevo estado (reservado, ocupado, cancelado)

    Returns:
        Programación actualizada
        :param programacion_id:
        :param nuevo_estado:
        :param reserva_service:
    """
    try:
        estados_validos = ["reservado", "ocupado", "cancelado"]
        if nuevo_estado not in estados_validos:
            raise HTTPException(
                status_code=400,
                detail=f"Estado inválido. Estados válidos: {', '.join(estados_validos)}"
            )

        result = reserva_service.cambiar_estado_programacion(programacion_id, nuevo_estado)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.delete("/programaciones/{programacion_id}")
def cancelar_programacion(
        programacion_id: str,
        reserva_service: ReservaAulaService = Depends(get_reserva_service)
):
    """
    Cancela una programación (cambia su estado a 'cancelado').

    Args:
        programacion_id: ID de la programación a cancelar

    Returns:
        Resultado de la cancelación
    """
    try:
        result = reserva_service.cambiar_estado_programacion(programacion_id, "cancelado")
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


def get_horario_completo_service() -> HorarioCompletoService:
    return HorarioCompletoService()

@router.post("/crear-horario-desde-programacion/{programacion_id}")
def crear_horario_desde_programacion(
        programacion_id: str,
        service: HorarioCompletoService = Depends(get_horario_completo_service)
):
    """
    Crea un horario usando el patrón Builder a partir de una programación reservada.
    """
    resultado = service.crear_horario_desde_programacion(programacion_id)
    if not resultado["success"]:
        raise HTTPException(status_code=400, detail=resultado["error"])
    return resultado

@router.post("/crear-horario-completo-semestre/{semestre}")
def crear_horario_completo_semestre(
        semestre: int,
        validar_conjunto: bool = True,
        service: HorarioCompletoService = Depends(get_horario_completo_service)
):
    """
    Crea el horario completo de un semestre usando todas las programaciones ocupadas.
    """
    resultado = service.crear_horario_completo_semestre(semestre, validar_conjunto)
    if not resultado["success"]:
        raise HTTPException(status_code=400, detail=resultado["error"])
    return resultado

@router.get("/horarios-por-semestre/{semestre}")
def listar_horarios_por_semestre(semestre: int):
    """
    Lista los horarios creados para un semestre, usando las programaciones con estado 'ocupado'.
    """
    programaciones = load_json("programaciones.json")
    horarios = [
        {
            "horario_id": p.get("horario_id"),
            "programacion_id": p.get("id"),
            "aula_id": p.get("aula_id"),
            "asignatura_id": p.get("asignatura_id"),
            "docente_id": p.get("docente_id"),
            "fecha": p.get("fecha"),
            "dia": p.get("dia"),
            "hora_inicio": p.get("hora_inicio"),
            "hora_fin": p.get("hora_fin"),
            "semestre": p.get("semestre"),
            "estado": p.get("estado"),
            "fecha_confirmacion": p.get("fecha_confirmacion")
        }
        for p in programaciones
        if p.get("estado") == "ocupado" and p.get("semestre") == semestre
    ]
    return {
        "semestre": semestre,
        "total_horarios": len(horarios),
        "horarios": horarios
    }

@router.get("/health")
def health_check():
    """Endpoint de salud para verificar que la API está funcionando."""
    return {
        "status": "healthy",
        "service": "Gestión de Horarios",
        "version": "1.0.0"
    }