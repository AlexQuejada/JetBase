"""
Servicio de transformación y detección de duplicados.
Maneja dedup y operaciones de transform.
"""
from typing import Optional
from fastapi import UploadFile, HTTPException, Request
import pandas as pd

from app.utils.file_reader import read_file
from app.utils.normalization import normalize_dataframe
from app.utils.file_validation import validate_file_size
from app.utils.rate_limiter import rate_limiter, ENDPOINT_RATE_LIMITS
from app.core.config import MAX_FILE_SIZE_BYTES
from app.core.logging_config import get_logger
from app.services.transform_service import TransformService

logger = get_logger("dedup_service")


def _get_client_ip(request: Request) -> str:
    """Extrae la IP del cliente del request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def detect_duplicates(
    request: Request,
    file: UploadFile,
    key_columns: Optional[str],
    case_sensitive: bool,
    normalize_whitespace: bool,
    normalize_accents: bool
) -> dict:
    """Detecta duplicados sin eliminarlos."""
    client_ip = _get_client_ip(request)
    logger.info(f"[{client_ip}] Detect duplicates: {file.filename}")

    config = ENDPOINT_RATE_LIMITS.get("detect_duplicates")
    allowed, msg = rate_limiter.check_rate_limit(client_ip, config)
    if not allowed:
        logger.warning(f"[{client_ip}] Rate limit excedido en detect_duplicates")
        raise HTTPException(429, msg)
    rate_limiter.record_request(client_ip)

    contents = await file.read()
    validate_file_size(len(contents), MAX_FILE_SIZE_BYTES)
    filename = file.filename.lower()

    try:
        df = await read_file(contents, filename)
    except Exception as e:
        logger.error(f"[{client_ip}] Error leyendo archivo: {e}")
        raise HTTPException(400, "No se pudo leer el archivo")

    if df is None:
        raise HTTPException(400, "No se pudo leer el archivo")

    df_clean = normalize_dataframe(df.copy(), case_sensitive, normalize_whitespace, normalize_accents)

    subset_cols = None
    if key_columns:
        subset_cols = [c.strip() for c in key_columns.split(',') if c.strip() in df_clean.columns]

    duplicated_mask = TransformService.detect_duplicates(df_clean, subset_cols)
    duplicated_rows = df[duplicated_mask]

    groups = []
    if len(duplicated_rows) > 0:
        if subset_cols:
            grouped = duplicated_rows.groupby([df_clean.loc[duplicated_rows.index, col] for col in subset_cols])
        else:
            grouped = [('', duplicated_rows)]

        for _, group in grouped if subset_cols else grouped:
            groups.append({
                "count": len(group),
                "indices": group.index.tolist(),
                "rows": group.fillna("").astype(str).to_dict(orient='records')
            })

    dup_count = int(duplicated_mask.sum())
    logger.info(f"[{client_ip}] Duplicates detected: {dup_count} rows in {len(groups)} groups")

    return {
        "success": True,
        "total_rows": len(df),
        "duplicated_rows": dup_count,
        "duplicate_groups": len(groups),
        "groups": groups[:50],
        "key_columns_used": subset_cols or "TODAS",
        "message": f"Se encontraron {len(groups)} grupos de duplicados"
    }


async def transform(
    request: Request,
    file: UploadFile,
    operation: str,
    fill_value: Optional[str],
    key_columns: Optional[str],
    case_sensitive: bool,
    normalize_whitespace: bool,
    normalize_accents: bool,
    keep: str
) -> dict:
    """Aplica operaciones de transformación."""
    client_ip = _get_client_ip(request)
    logger.info(f"[{client_ip}] Transform request: {file.filename} - operation={operation}")

    config = ENDPOINT_RATE_LIMITS.get("transform")
    allowed, msg = rate_limiter.check_rate_limit(client_ip, config)
    if not allowed:
        logger.warning(f"[{client_ip}] Rate limit excedido en transform")
        raise HTTPException(429, msg)
    rate_limiter.record_request(client_ip)

    contents = await file.read()
    validate_file_size(len(contents), MAX_FILE_SIZE_BYTES)
    filename = file.filename.lower()

    try:
        df = await read_file(contents, filename)
    except Exception as e:
        logger.error(f"[{client_ip}] Error leyendo archivo: {e}")
        raise HTTPException(400, "No se pudo leer el archivo")

    if df is None:
        raise HTTPException(400, "No se pudo leer el archivo")

    original_rows = len(df)
    df = normalize_dataframe(df, case_sensitive, normalize_whitespace, normalize_accents)

    try:
        df, message = TransformService.apply_operation(df, operation, fill_value, key_columns, keep)
    except ValueError as e:
        logger.warning(f"[{client_ip}] Transform error: {e}")
        raise HTTPException(400, str(e))

    logger.info(f"[{client_ip}] Transform done: {original_rows} -> {len(df)} rows")

    return {
        "success": True,
        "filename": file.filename,
        "operation": operation,
        "original_rows": original_rows,
        "transformed_rows": len(df),
        "message": message,
        "columns": list(df.columns),
        "preview": df.head(100).fillna("").astype(str).to_dict(orient='records')
    }
