from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api_router
from app.core.logging_config import setup_logging
from app.core.config import MAX_FILE_SIZE_MB

# Setup logging
logger = setup_logging()
logger.info(f"Flintrex API starting - max file size: {MAX_FILE_SIZE_MB}MB")

app = FastAPI(
    title="Flintrex API",
    description="Plataforma de transformación y visualización de datos",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas de la API
app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Flintrex API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}