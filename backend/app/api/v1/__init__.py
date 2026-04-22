from fastapi import APIRouter
from .endpoints import data, jobs

router = APIRouter()
router.include_router(data.router, prefix="/data", tags=["Data"])
router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])