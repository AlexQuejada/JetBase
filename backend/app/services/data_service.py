"""
Servicio principal de procesamiento de datos.
Contiene toda la lógica de negocio de los endpoints de data.
"""
import io
from typing import Optional, List, Tuple
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
from app.services.harmonizer_service import HarmonizerService

logger = get_logger("data_service")


def _get_client_ip(request: Request) -> str:
    """Extrae la IP del cliente del request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class DataService:
    """Servicio de procesamiento de archivos CSV/Excel."""

    @staticmethod
    def _validate_upload(file: UploadFile, allowed_extensions: tuple) -> None:
        """Valida el archivo al subirlo."""
        filename_lower = file.filename.lower()
        if not filename_lower.endswith(allowed_extensions):
            ext_str = ", ".join(allowed_extensions)
            logger.warning(f"Extensión inválida: {file.filename} - esperaba {ext_str}")
            raise HTTPException(400, f"El archivo debe ser: {ext_str}")

        # Validar tamaño usando file.size si está disponible
        if hasattr(file, 'size') and file.size is not None:
            validate_file_size(file.size, MAX_FILE_SIZE_BYTES)

    @staticmethod
    async def upload_file(request: Request, file: UploadFile, allowed_extensions: tuple) -> dict:
        """Procesa un archivo de upload (CSV o Excel)."""
        client_ip = _get_client_ip(request)
        logger.info(f"[{client_ip}] Upload request: {file.filename}")

        # Check rate limit
        config = ENDPOINT_RATE_LIMITS.get("upload")
        allowed, msg = rate_limiter.check_rate_limit(client_ip, config)
        if not allowed:
            logger.warning(f"[{client_ip}] Rate limit excedido en upload: {msg}")
            raise HTTPException(429, msg)
        rate_limiter.record_request(client_ip)

        # Validar extensión
        DataService._validate_upload(file, allowed_extensions)

        filename_lower = file.filename.lower()
        contents = await file.read()

        # Validar tamaño del contenido leído
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

    @staticmethod
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

        # Check rate limit
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

        # Normalizar
        df_clean = normalize_dataframe(df.copy(), case_sensitive, normalize_whitespace, normalize_accents)

        # Determinar columnas clave
        subset_cols = None
        if key_columns:
            subset_cols = [c.strip() for c in key_columns.split(',') if c.strip() in df_clean.columns]

        # Detectar duplicados
        duplicated_mask = TransformService.detect_duplicates(df_clean, subset_cols)
        duplicated_rows = df[duplicated_mask]

        # Agrupar
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

    @staticmethod
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

        # Check rate limit
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

    @staticmethod
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

        # Check rate limit
        config = ENDPOINT_RATE_LIMITS.get("merge")
        allowed, msg = rate_limiter.check_rate_limit(client_ip, config)
        if not allowed:
            logger.warning(f"[{client_ip}] Rate limit excedido en merge")
            raise HTTPException(429, msg)
        rate_limiter.record_request(client_ip)

        if len(files) < 2:
            raise HTTPException(400, "Se necesitan al menos 2 archivos")

        if len(files) > MAX_FILES_PER_REQUEST:
            raise HTTPException(400, f"Máximo {MAX_FILES_PER_REQUEST} archivos por request")

        # Leer todos los archivos
        dataframes = []
        file_info = []
        all_columns = set()

        for file in files:
            contents = await file.read()
            validate_file_size(len(contents), MAX_FILE_SIZE_BYTES)
            filename = file.filename.lower()

            try:
                df = await read_file(contents, filename)
            except Exception as e:
                logger.error(f"[{client_ip}] Error leyendo {file.filename}: {e}")
                raise HTTPException(400, f"No se pudo leer: {file.filename}")

            if df is None:
                raise HTTPException(400, f"No se pudo leer: {file.filename}")

            logger.debug(f"[{client_ip}] {file.filename}: {list(df.columns)[:5]}...")

            # 1. Primero mapear sinónimos de columnas (ej: full_name → nombre)
            df = MergeService.normalize_columns(df)

            # 2. Luego normalizar valores (acentos, espacios, mayúsculas)
            df = normalize_dataframe(df, case_sensitive, normalize_whitespace, normalize_accents)

            all_columns.update(df.columns)
            dataframes.append(df)
            file_info.append({
                "filename": file.filename,
                "rows": len(df),
                "columns": len(df.columns)
            })

        # Análisis de esquema
        columns_by_file = {
            info["filename"]: set(df.columns)
            for info, df in zip(file_info, dataframes)
        }
        common_columns = set.intersection(*columns_by_file.values()) if columns_by_file else set()
        all_columns = set().union(*columns_by_file.values())

        # Parsear key_columns
        key_cols_list = None
        if key_columns:
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
            key_cols_list = key_cols_normalized

        # Detectar y ejecutar merge
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

        # Trazabilidad
        row_counts = [len(df) for df in dataframes]
        filenames = [info["filename"] for info in file_info]
        combined_df = MergeService.add_source_column(combined_df, filenames, row_counts, final_mode)

        # Preparar key_columns
        key_columns_for_operation = ','.join(key_cols_list) if key_cols_list else key_columns

        # Aplicar operación de limpieza
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

    @staticmethod
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

        # Check rate limit
        config = ENDPOINT_RATE_LIMITS.get("merge")
        allowed, msg = rate_limiter.check_rate_limit(client_ip, config)
        if not allowed:
            raise HTTPException(429, msg)
        rate_limiter.record_request(client_ip)

        if len(files) < 2:
            raise HTTPException(400, "Se necesitan al menos 2 archivos")

        # Leer todos los archivos
        dataframes = []
        all_columns = set()

        for file in files:
            contents = await file.read()
            validate_file_size(len(contents), MAX_FILE_SIZE_BYTES)
            filename = file.filename.lower()

            df = await read_file(contents, filename)
            if df is None:
                raise HTTPException(400, f"No se pudo leer: {file.filename}")

            df = MergeService.normalize_columns(df)
            df = normalize_dataframe(df, case_sensitive, normalize_whitespace, normalize_accents)

            all_columns.update(df.columns)
            dataframes.append(df)

        # Análisis de esquema
        columns_by_file = [set(df.columns) for df in dataframes]
        common_columns = set.intersection(*columns_by_file) if columns_by_file else set()

        # Parsear key_columns
        key_cols_list = None
        if key_columns:
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
            key_cols_list = key_cols_normalized

        # Detectar y ejecutar merge
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

        # Trazabilidad
        row_counts = [len(df) for df in dataframes]
        filenames = [f.filename for f in files]
        combined_df = MergeService.add_source_column(combined_df, filenames, row_counts, final_mode)

        # Aplicar operación de limpieza
        key_columns_for_operation = ','.join(key_cols_list) if key_cols_list else key_columns
        combined_df, _ = TransformService.apply_operation(
            combined_df, operation, fill_value, key_columns_for_operation, keep
        )

        # Generar archivo en memoria
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

    @staticmethod
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

        # Check rate limit
        config = ENDPOINT_RATE_LIMITS.get("harmonize")
        allowed, msg = rate_limiter.check_rate_limit(client_ip, config)
        if not allowed:
            logger.warning(f"[{client_ip}] Rate limit excedido en harmonize")
            raise HTTPException(429, msg)
        rate_limiter.record_request(client_ip)

        if len(files) < 2:
            raise HTTPException(400, "Se necesitan al menos 2 archivos para armonizar")

        dataframes = []
        file_info = []
        all_columns = set()

        for file in files:
            contents = await file.read()
            validate_file_size(len(contents), MAX_FILE_SIZE_BYTES)
            filename = file.filename.lower()

            df = await read_file(contents, filename)
            if df is None:
                logger.error(f"[{client_ip}] No se pudo leer: {file.filename}")
                raise HTTPException(400, f"No se pudo leer: {file.filename}")

            df = MergeService.normalize_columns(df)
            df = normalize_dataframe(df, case_sensitive, normalize_whitespace, normalize_accents)

            all_columns.update(df.columns)
            dataframes.append(df)
            file_info.append({
                "filename": file.filename,
                "rows": len(df),
                "columns": len(df.columns)
            })

        # Llamar al armonizador
        filenames = [f.filename for f in files]
        combined_df, metadata = HarmonizerService.harmonize(dataframes, filenames)

        # Obtener scores de archivos para el response
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

    @staticmethod
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

        # Check rate limit
        config = ENDPOINT_RATE_LIMITS.get("harmonize")
        allowed, msg = rate_limiter.check_rate_limit(client_ip, config)
        if not allowed:
            raise HTTPException(429, msg)
        rate_limiter.record_request(client_ip)

        if len(files) < 2:
            raise HTTPException(400, "Se necesitan al menos 2 archivos para armonizar")

        dataframes = []
        filenames_list = []

        for file in files:
            contents = await file.read()
            validate_file_size(len(contents), MAX_FILE_SIZE_BYTES)
            filename = file.filename.lower()

            df = await read_file(contents, filename)
            if df is None:
                raise HTTPException(400, f"No se pudo leer: {file.filename}")

            df = MergeService.normalize_columns(df)
            df = normalize_dataframe(df, case_sensitive, normalize_whitespace, normalize_accents)

            dataframes.append(df)
            filenames_list.append(file.filename)

        # Armonizar
        combined_df, _ = HarmonizerService.harmonize(dataframes, filenames_list)

        # Generar archivo
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