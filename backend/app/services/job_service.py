"""
Servicio de jobs asíncronos para procesamiento pesado.
"""
import asyncio
import uuid
import time
from enum import Enum
from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor

from app.core.config import MAX_CONCURRENT_JOBS, JOB_TIMEOUT_SECONDS


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    """Representa un job de procesamiento."""
    job_id: str
    status: JobStatus = JobStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    progress: float = 0.0


class JobService:
    """Gestor de jobs asíncronos en memoria."""

    def __init__(self):
        self._jobs: Dict[str, Job] = {}
        self._executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_JOBS)

    def create_job(self) -> str:
        """Crea un nuevo job y retorna su ID."""
        job_id = str(uuid.uuid4())[:8]
        self._jobs[job_id] = Job(job_id=job_id)
        return job_id

    def get_job(self, job_id: str) -> Optional[Job]:
        """Obtiene el estado de un job."""
        return self._jobs.get(job_id)

    async def run_job(
        self,
        job_id: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Ejecuta una función en background y actualiza el estado del job.
        """
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} no encontrado")

        job.status = JobStatus.PROCESSING
        job.started_at = time.time()

        try:
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(self._executor, func, *args, **kwargs),
                timeout=JOB_TIMEOUT_SECONDS
            )
            job.result = result
            job.status = JobStatus.COMPLETED
            job.progress = 1.0
            job.completed_at = time.time()
            return result

        except asyncio.TimeoutError:
            job.error = f"Job excedió el timeout de {JOB_TIMEOUT_SECONDS}s"
            job.status = JobStatus.FAILED
            job.completed_at = time.time()
            raise

        except Exception as e:
            job.error = str(e)
            job.status = JobStatus.FAILED
            job.completed_at = time.time()
            raise

    def cleanup_old_jobs(self, max_age_seconds: int = 3600):
        """Elimina jobs completados/fallidos antiguos."""
        now = time.time()
        expired = [
            job_id for job_id, job in self._jobs.items()
            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED)
            and (now - job.completed_at) > max_age_seconds
        ]
        for job_id in expired:
            del self._jobs[job_id]


# Instancia global del servicio de jobs
job_service = JobService()