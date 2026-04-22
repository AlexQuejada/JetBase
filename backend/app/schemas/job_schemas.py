"""
Esquemas para el sistema de jobs asíncronos.
"""
from pydantic import BaseModel
from typing import Optional, Any, List
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobInfo(BaseModel):
    """Información de un job."""
    job_id: str
    status: JobStatus
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    progress: float = 0.0
    error: Optional[str] = None


class JobCreatedResponse(BaseModel):
    """Respuesta cuando se crea un job."""
    job_id: str
    status: JobStatus
    message: str
    status_url: str


class JobStatusResponse(BaseModel):
    """Respuesta de estado de un job."""
    job_id: str
    status: JobStatus
    progress: float
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


class ValidationResponse(BaseModel):
    """Respuesta de validación de archivo."""
    valid: bool
    file_type: Optional[str] = None
    size: int
    size_formatted: str
    message: str