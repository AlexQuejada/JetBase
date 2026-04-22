"""
Configuración central de la aplicación.
"""
import os
from pathlib import Path

# Tamaño máximo de archivo (100 MB por defecto)
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Límite de archivos en operaciones múltiples
MAX_FILES_PER_REQUEST = int(os.getenv("MAX_FILES_PER_REQUEST", "20"))

# Configuración de jobs async (en memoria)
# En producción usar Redis o similar
JOB_TIMEOUT_SECONDS = int(os.getenv("JOB_TIMEOUT_SECONDS", "300"))
MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "5"))

# Path base
BASE_DIR = Path(__file__).resolve().parent.parent.parent