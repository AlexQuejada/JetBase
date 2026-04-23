"""
Servicio extendido de armonización.
Maneja harmonize de múltiples archivos y descarga de resultados.
"""
import io
from typing import List, Tuple
from fastapi import UploadFile, HTTPException, Request
import pandas as pd

from app.utils.file_reader import read_file
from app.utils.normalization import normalize_dataframe
from app.utils.file_validation import validate_file_size
from app.utils.rate_limiter import rate_limiter, ENDPOINT_RATE_LIMITS
from app.core.config import MAX_FILE_SIZE_BYTES
from app.core.logging_config import get_logger
from app.services.merge_service import MergeService
from app.services.harmonizer_service import HarmonizerService

logger = get_logger("harmonize_extended_service")


def _get_client_ip(request: Request) -> str:
    """Extrae la IP del cliente del request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _read_and_normalize_file(file: UploadFile, case_sensitive: bool, normalize_whitespace: bool, normalize_accents: bool) -> pd.DataFrame:
    """Lee y normaliza un archivo individual."""
    contents = await file.read()
    validate_file_size(len(contents), MAX_FILE_SIZE_BYTES)
    filename = file.filename.lower()

    df = await read_file(contents, filename)
    if df is None:
        raise HTTPException(400, f"No se pudo leer: {file.filename}")

    df = MergeService.normalize_columns(df)
    df = normalize_dataframe(df, case_sensitive, normalize_whitespace, normalize_accents)
    return df


async def harmonize(
    request: Request,
    files: List[UploadFile],
    case_sensitive: bool,
    normalize_whitespace: bool,
    normalize_accents: bool
) -> dict:
    """Armoniza múltiples archivos: elige referencia, alinea esquemas, combina."""
    client_ip = _get_client_ip(request)
    logger.info(f"[{client_ip}] Harmonize request: {len(files)} archivos")

    config = ENDPOINT_RATE_LIMITS.get("harmonize")
    allowed, msg = rate_limiter.check_rate_limit(client_ip, config)
    if not allowed:
        logger.warning(f"[{client_ip}] Rate limit excedido en harmonize")
        raise HTTPException(429, msg)
    rate_limiter.record_request(client_ip)

    if len(files) < 1:
        raise HTTPException(400, "Se necesita al menos 1 archivo para armonizar")

    dataframes = []
    file_info = []
    all_columns = set()

    for file in files:
        df = await _read_and_normalize_file(file, case_sensitive, normalize_whitespace, normalize_accents)
        all_columns.update(df.columns)
        dataframes.append(df)
        file_info.append({
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns)
        })

    filenames = [f.filename for f in files]
    combined_df, metadata = HarmonizerService.harmonize(dataframes, filenames)

    file_scores = metadata.get('file_scores', [])
    for i, info in enumerate(file_scores):
        info['filename'] = file_info[i]['filename']

    logger.info(f"[{client_ip}] Harmonize completado: reference={metadata.get('reference_file')}")

    return {
        "success": True,
        "files_processed": len(files),
        "files": file_info,
        "reference_file": metadata.get('reference_file'),
        "reference_index": metadata.get('reference_index'),
        "file_scores": file_scores,
        "combined_rows": metadata.get('combined_rows', len(combined_df)),
        "final_columns": metadata.get('final_columns', list(combined_df.columns)),
        "columns": list(combined_df.columns),
        "preview": combined_df.head(100).fillna("").astype(str).to_dict(orient='records')
    }


async def harmonize_download(
    request: Request,
    files: List[UploadFile],
    case_sensitive: bool,
    normalize_whitespace: bool,
    normalize_accents: bool,
    download_format: str = "csv"
) -> Tuple[bytes, str, str]:
    """Armoniza múltiples archivos y devuelve el resultado como archivo descargable."""
    client_ip = _get_client_ip(request)
    logger.info(f"[{client_ip}] Harmonize download: {len(files)} archivos")

    config = ENDPOINT_RATE_LIMITS.get("harmonize")
    allowed, msg = rate_limiter.check_rate_limit(client_ip, config)
    if not allowed:
        raise HTTPException(429, msg)
    rate_limiter.record_request(client_ip)

    if len(files) < 1:
        raise HTTPException(400, "Se necesita al menos 1 archivo para armonizar")

    dataframes = []
    filenames_list = []

    for file in files:
        df = await _read_and_normalize_file(file, case_sensitive, normalize_whitespace, normalize_accents)
        dataframes.append(df)
        filenames_list.append(file.filename)

    combined_df, _ = HarmonizerService.harmonize(dataframes, filenames_list)

    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")

    if download_format.lower() == "excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            combined_df.to_excel(writer, index=False, sheet_name='Harmonized')
        output.seek(0)
        content = output.getvalue()
        download_filename = f"harmonized_{timestamp}.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        output = io.StringIO()
        combined_df.to_csv(output, index=False, encoding='utf-8-sig')
        content = output.getvalue().encode('utf-8-sig')
        download_filename = f"harmonized_{timestamp}.csv"
        media_type = "text/csv; charset=utf-8"

    return content, download_filename, media_type
