"""
Servicio de upload de archivos.
Maneja la subida y validación de archivos CSV/Excel.
"""
import io
from fastapi import UploadFile, HTTPException, Request
import pandas as pd

from app.utils.file_reader import read_file
from app.utils.file_validation import validate_file_size
from app.utils.rate_limiter import rate_limiter, ENDPOINT_RATE_LIMITS
from app.core.config import MAX_FILE_SIZE_BYTES
from app.core.logging_config import get_logger

logger = get_logger("upload_service")


def _get_client_ip(request: Request) -> str:
    """Extrae la IP del cliente del request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _validate_upload(file: UploadFile, allowed_extensions: tuple) -> None:
    """Valida el archivo al subirlo."""
    filename_lower = file.filename.lower()
    if not filename_lower.endswith(allowed_extensions):
        ext_str = ", ".join(allowed_extensions)
        logger.warning(f"Extensión inválida: {file.filename} - esperaba {ext_str}")
        raise HTTPException(400, f"El archivo debe ser: {ext_str}")

    if hasattr(file, 'size') and file.size is not None:
        validate_file_size(file.size, MAX_FILE_SIZE_BYTES)


async def upload_file(request: Request, file: UploadFile, allowed_extensions: tuple) -> dict:
    """Procesa un archivo de upload (CSV o Excel)."""
    client_ip = _get_client_ip(request)
    logger.info(f"[{client_ip}] Upload request: {file.filename}")

    config = ENDPOINT_RATE_LIMITS.get("upload")
    allowed, msg = rate_limiter.check_rate_limit(client_ip, config)
    if not allowed:
        logger.warning(f"[{client_ip}] Rate limit excedido en upload: {msg}")
        raise HTTPException(429, msg)
    rate_limiter.record_request(client_ip)

    _validate_upload(file, allowed_extensions)

    filename_lower = file.filename.lower()
    contents = await file.read()

    validate_file_size(len(contents), MAX_FILE_SIZE_BYTES)
    logger.debug(f"[{client_ip}] Archivo leído: {len(contents)} bytes")

    try:
        df = await read_file(contents, filename_lower)
    except Exception as e:
        logger.error(f"[{client_ip}] Error leyendo archivo {file.filename}: {e}")
        raise HTTPException(400, "No se pudo leer el archivo. Verifica el formato.")

    if df is None:
        logger.warning(f"[{client_ip}] No se pudo parsear: {file.filename}")
        raise HTTPException(400, "No se pudo leer el archivo. Verifica el formato.")

    logger.info(f"[{client_ip}] Upload exitoso: {file.filename} - {len(df)} filas, {len(df.columns)} columnas")

    return {
        "filename": file.filename,
        "rows": len(df),
        "columns": list(df.columns),
        "preview": df.head(100).fillna("").to_dict(orient='records'),
        "column_types": df.dtypes.astype(str).to_dict()
    }
