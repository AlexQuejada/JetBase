from fastapi import APIRouter
from .endpoints import data

router = APIRouter()
router.include_router(data.router, prefix="/data", tags=["Data"])