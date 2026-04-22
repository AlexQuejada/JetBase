"""
Endpoints para el sistema de jobs asíncronos.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.services.job_service import job_service, JobStatus
from app.schemas.job_schemas import (
    JobCreatedResponse,
    JobStatusResponse,
    JobStatus
)

router = APIRouter()


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Obtiene el estado actual de un job."""
    job = job_service.get_job(job_id)
    if not job:
        raise HTTPException(404, f"Job {job_id} no encontrado")

    return JobStatusResponse(
        job_id=job.job_id,
        status=JobStatus(job.status.value),
        progress=job.progress,
        result=job.result,
        error=job.error,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at
    )