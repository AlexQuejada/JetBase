from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api_router

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