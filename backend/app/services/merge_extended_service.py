"""
Servicio extendido de merge.
Maneja merge de múltiples archivos y descarga de resultados.
"""
import io
from typing import List, Optional, Tuple
from fastapi import UploadFile, HTTPException, Request
import pandas as pd

from app.utils.file_reader import read_file
from app.utils.normalization import normalize_dataframe
from app.utils.file_validation import validate_file_size
from app.utils.rate_limiter import rate_limiter, ENDPOINT_RATE_LIMITS
from app.core.config import MAX_FILE_SIZE_BYTES, MAX_FILES_PER_REQUEST
from app.core.logging_config import get_logger
from app.services.transform_service import TransformService
from app.services.merge_service import MergeService

logger = get_logger("merge_extended_service")


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


def _parse_key_columns(key_columns: Optional[str]) -> Optional[List[str]]:
    """Normaliza y parsea las columnas clave."""
    if not key_columns:
        return None

    key_cols_normalized = []
    for col in key_columns.split(','):
        col_clean = col.strip().lower().replace(' ', '_').replace('-', '_')
        matched = False
        for standard_name, synonyms in MergeService.COLUMN_SYNONYMS.items():
            if col_clean in synonyms:
                key_cols_normalized.append(standard_name)
                matched = True
                break
        if not matched:
            key_cols_normalized.append(col.strip())
    return key_cols_normalized


async def merge(
    request: Request,
    files: List[UploadFile],
    operation: str,
    fill_value: Optional[str],
    key_columns: Optional[str],
    case_sensitive: bool,
    normalize_whitespace: bool,
    normalize_accents: bool,
    keep: str,
    merge_mode: str,
    join_type: str
) -> dict:
    """Combina múltiples archivos."""
    client_ip = _get_client_ip(request)
    logger.info(f"[{client_ip}] Merge request: {len(files)} archivos")

    config = ENDPOINT_RATE_LIMITS.get("merge")
    allowed, msg = rate_limiter.check_rate_limit(client_ip, config)
    if not allowed:
        logger.warning(f"[{client_ip}] Rate limit excedido en merge")
        raise HTTPException(429, msg)
    rate_limiter.record_request(client_ip)

    if len(files) < 1:
        raise HTTPException(400, "Se necesita al menos 1 archivo")

    if len(files) > MAX_FILES_PER_REQUEST:
        raise HTTPException(400, f"Máximo {MAX_FILES_PER_REQUEST} archivos por request")

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

    columns_by_file = {
        info["filename"]: set(df.columns)
        for info, df in zip(file_info, dataframes)
    }
    common_columns = set.intersection(*columns_by_file.values()) if columns_by_file else set()
    all_columns = set().union(*columns_by_file.values())

    key_cols_list = _parse_key_columns(key_columns)

    if len(files) == 1:
        df = dataframes[0]
        key_columns_for_operation = key_columns

        try:
            df, message = TransformService.apply_operation(
                df, operation, fill_value, key_columns_for_operation, keep
            )
            message = f"Archivo único: {message}"
        except ValueError as e:
            logger.warning(f"[{client_ip}] Transform error: {e}")
            raise HTTPException(400, str(e))

        logger.info(f"[{client_ip}] Single file done: {files[0].filename} -> {len(df)} rows")

        return {
            "success": True,
            "files_processed": 1,
            "files": file_info,
            "original_rows": sum(len(d) for d in dataframes),
            "transformed_rows": len(df),
            "message": message,
            "columns": list(df.columns),
            "schema_validation": {
                "total_columns": len(df.columns),
                "common_columns": list(df.columns),
                "columns_by_file": {file_info[0]["filename"]: list(df.columns)},
                "has_schema_differences": False,
                "merge_mode_requested": merge_mode,
                "merge_mode_detected": "single",
                "merge_mode_used": "single",
                "merge_strategy": "Archivo único (sin merge)"
            },
            "preview": df.head(100).fillna("").astype(str).to_dict(orient='records')
        }

    detected_mode = MergeService.detect_merge_mode(dataframes, key_cols_list, common_columns)
    final_mode = merge_mode if merge_mode != "auto" else detected_mode

    if final_mode == "join":
        if not key_cols_list:
            key_cols_list = MergeService._infer_key_columns(common_columns)
            if not key_cols_list:
                logger.warning(f"[{client_ip}] No se pudieron inferir columnas clave")
                raise HTTPException(400, "No se pudieron inferir columnas clave")
        combined_df = MergeService.perform_join(dataframes, key_cols_list, join_type)
        merge_strategy = f"JOIN ({join_type}) por {', '.join(key_cols_list)}"
    else:
        combined_df = MergeService.perform_union(dataframes)
        merge_strategy = "UNION (concatenación vertical)"

    original_rows = sum(len(df) for df in dataframes)

    row_counts = [len(df) for df in dataframes]
    filenames = [info["filename"] for info in file_info]
    combined_df = MergeService.add_source_column(combined_df, filenames, row_counts, final_mode)

    key_columns_for_operation = ','.join(key_cols_list) if key_cols_list else key_columns

    try:
        combined_df, message = TransformService.apply_operation(
            combined_df, operation, fill_value, key_columns_for_operation, keep
        )
        message = f"Merge ({final_mode}): {message}"
    except ValueError as e:
        logger.warning(f"[{client_ip}] Merge transform error: {e}")
        raise HTTPException(400, str(e))

    logger.info(f"[{client_ip}] Merge completado: {original_rows} -> {len(combined_df)} rows, {merge_strategy}")

    return {
        "success": True,
        "files_processed": len(files),
        "files": file_info,
        "original_rows": original_rows,
        "transformed_rows": len(combined_df),
        "message": message,
        "columns": list(combined_df.columns),
        "schema_validation": {
            "total_columns": len(all_columns),
            "common_columns": sorted(common_columns),
            "columns_by_file": {fn: sorted(cols) for fn, cols in columns_by_file.items()},
            "has_schema_differences": len(common_columns) < len(all_columns),
            "merge_mode_requested": merge_mode,
            "merge_mode_detected": detected_mode,
            "merge_mode_used": final_mode,
            "merge_strategy": merge_strategy
        },
        "preview": combined_df.head(100).fillna("").astype(str).to_dict(orient='records')
    }


async def merge_download(
    request: Request,
    files: List[UploadFile],
    operation: str,
    fill_value: Optional[str],
    key_columns: Optional[str],
    case_sensitive: bool,
    normalize_whitespace: bool,
    normalize_accents: bool,
    keep: str,
    merge_mode: str,
    join_type: str,
    download_format: str = "csv"
) -> Tuple[bytes, str, str]:
    """Combina múltiples archivos y devuelve el resultado como archivo descargable."""
    client_ip = _get_client_ip(request)
    logger.info(f"[{client_ip}] Merge download: {len(files)} archivos, format={download_format}")

    config = ENDPOINT_RATE_LIMITS.get("merge")
    allowed, msg = rate_limiter.check_rate_limit(client_ip, config)
    if not allowed:
        raise HTTPException(429, msg)
    rate_limiter.record_request(client_ip)

    if len(files) < 1:
        raise HTTPException(400, "Se necesita al menos 1 archivo")

    dataframes = []
    all_columns = set()

    for file in files:
        df = await _read_and_normalize_file(file, case_sensitive, normalize_whitespace, normalize_accents)
        all_columns.update(df.columns)
        dataframes.append(df)

    columns_by_file = [set(df.columns) for df in dataframes]
    common_columns = set.intersection(*columns_by_file) if columns_by_file else set()

    key_cols_list = _parse_key_columns(key_columns)

    if len(files) == 1:
        df = dataframes[0]
        key_columns_for_operation = key_columns
        df, _ = TransformService.apply_operation(
            df, operation, fill_value, key_columns_for_operation, keep
        )

        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        if download_format.lower() == "excel":
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Result')
            output.seek(0)
            content = output.getvalue()
            download_filename = f"result_{timestamp}.xlsx"
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            output = io.StringIO()
            df.to_csv(output, index=False, encoding='utf-8-sig')
            content = output.getvalue().encode('utf-8-sig')
            download_filename = f"result_{timestamp}.csv"
            media_type = "text/csv; charset=utf-8"

        logger.info(f"[{client_ip}] Single file download: {download_filename}")
        return content, download_filename, media_type

    detected_mode = MergeService.detect_merge_mode(dataframes, key_cols_list, common_columns)
    final_mode = merge_mode if merge_mode != "auto" else detected_mode

    if final_mode == "join":
        if not key_cols_list:
            key_cols_list = MergeService._infer_key_columns(common_columns)
            if not key_cols_list:
                raise HTTPException(400, "No se pudieron inferir columnas clave")
        combined_df = MergeService.perform_join(dataframes, key_cols_list, join_type)
    else:
        combined_df = MergeService.perform_union(dataframes)

    row_counts = [len(df) for df in dataframes]
    filenames = [f.filename for f in files]
    combined_df = MergeService.add_source_column(combined_df, filenames, row_counts, final_mode)

    key_columns_for_operation = ','.join(key_cols_list) if key_cols_list else key_columns
    combined_df, _ = TransformService.apply_operation(
        combined_df, operation, fill_value, key_columns_for_operation, keep
    )

    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")

    if download_format.lower() == "excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            combined_df.to_excel(writer, index=False, sheet_name='Merged')
        output.seek(0)
        content = output.getvalue()
        download_filename = f"merged_{timestamp}.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        output = io.StringIO()
        combined_df.to_csv(output, index=False, encoding='utf-8-sig')
        content = output.getvalue().encode('utf-8-sig')
        download_filename = f"merged_{timestamp}.csv"
        media_type = "text/csv; charset=utf-8"

    logger.info(f"[{client_ip}] Merge download generado: {download_filename} ({len(content)} bytes)")

    return content, download_filename, media_type
