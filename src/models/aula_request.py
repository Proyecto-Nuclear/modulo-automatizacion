# src/models/aula_request.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import re

class AulaDisponibleRequest(BaseModel):
    """Modelo para la solicitud de aulas disponibles."""

    asignatura_id: str = Field(..., description="ID de la asignatura")
    hora_inicio: str = Field(..., description="Hora de inicio en formato HH:MM")
    hora_fin: str = Field(..., description="Hora de fin en formato HH:MM")
    dia: str = Field(..., description="Día de la semana")
    cantidad_estudiantes: int = Field(..., gt=0, description="Número de estudiantes")
    semestre: int = Field(..., gt=0, le=10, description="Semestre académico")

    @validator('hora_inicio', 'hora_fin')
    def validate_time_format(cls, v):
        if not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', v):
            raise ValueError('Formato de hora inválido. Debe ser HH:MM')
        return v

    @validator('dia')
    def validate_dia(cls, v):
        dias_validos = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        if v not in dias_validos:
            raise ValueError(f'Día inválido. Debe ser uno de: {", ".join(dias_validos)}')
        return v

    @validator('hora_fin')
    def validate_hora_fin_mayor(cls, v, values):
        if 'hora_inicio' in values and v <= values['hora_inicio']:
            raise ValueError('La hora de fin debe ser posterior a la hora de inicio')
        return v

class AulaInfo(BaseModel):
    """Información de un aula."""
    id: str
    nombre: str
    tipo: str
    capacidad: int
    sede: str
    recursos: List[str] = []

class AulaNoDisponible(BaseModel):
    """Información de un aula no disponible."""
    id: str
    nombre: str
    razon: str

class AsignaturaInfo(BaseModel):
    """Información de la asignatura."""
    id: str
    nombre: str
    tipo: str

class HorarioSolicitado(BaseModel):
    """Información del horario solicitado."""
    dia: str
    hora_inicio: str
    hora_fin: str
    cantidad_estudiantes: int
    semestre: int

class AulaDisponibleResponse(BaseModel):
    """Respuesta con aulas disponibles."""
    asignatura: AsignaturaInfo
    horario_solicitado: HorarioSolicitado
    aulas_disponibles: List[AulaInfo]
    aulas_no_disponibles: List[AulaNoDisponible]
    total_disponibles: int
    total_no_disponibles: int
    error: Optional[str] = None