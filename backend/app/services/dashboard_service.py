"""
Servicio de análisis y visualización de datos para dashboards.
Genera métricas agregadas según el tipo de dato de cada columna.
"""
import io
from typing import Dict, List, Any, Optional, Tuple
from fastapi import UploadFile, HTTPException, Request
import pandas as pd
import numpy as np
from datetime import datetime

from app.utils.file_reader import read_file
from app.utils.file_validation import validate_file_size
from app.utils.rate_limiter import rate_limiter, DEFAULT_RATE_LIMITS
from app.core.config import MAX_FILE_SIZE_BYTES
from app.core.logging_config import get_logger

logger = get_logger("dashboard_service")


def _get_client_ip(request: Request) -> str:
    """Extrae la IP del cliente del request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class DashboardService:
    """Servicio de generación de métricas para dashboards."""

    # Métricas permitidas por tipo de dato
    METRICS_BY_TYPE = {
        "numeric": ["sum", "avg", "min", "max", "count", "median", "std_dev"],
        "text": ["count", "unique_count", "mode", "avg_length"],
        "datetime": ["count", "min", "max", "range_days", "count_by_month", "count_by_year"],
        "boolean": ["count", "count_true", "count_false", "percentage_true"],
        "unknown": ["count"]
    }

    # Tipos de gráficos permitidos por tipo de dato
    CHARTS_BY_TYPE = {
        "numeric": ["bar", "line", "pie", "scatter", "histogram", "table"],
        "text": ["bar", "pie", "table"],
        "datetime": ["line", "bar", "table"],
        "boolean": ["pie", "bar", "table"],
        "unknown": ["table"]
    }

    @staticmethod
    def detect_column_type(series: pd.Series) -> str:
        """Detecta el tipo de dato de una columna pandas."""
        if pd.api.types.is_bool_dtype(series):
            return "boolean"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        elif pd.api.types.is_numeric_dtype(series):
            return "numeric"
        elif pd.api.types.is_string_dtype(series) or series.dtype == object:
            return "text"
        return "unknown"

    @staticmethod
    async def analyze_columns(request: Request, file: UploadFile) -> Dict[str, Any]:
        """
        Analiza un archivo y devuelve información de sus columnas con tipos detectados.
        """
        client_ip = _get_client_ip(request)

        # Rate limit check
        allowed, msg = rate_limiter.check_rate_limit(client_ip, DEFAULT_RATE_LIMITS)
        if not allowed:
            logger.warning(f"[{client_ip}] Rate limit excedido en dashboard/analyze")
            raise HTTPException(429, msg)
        rate_limiter.record_request(client_ip)

        contents = await file.read()
        validate_file_size(len(contents), MAX_FILE_SIZE_BYTES)
        filename = file.filename.lower()

        logger.debug(f"[{client_ip}] Analyzing: {file.filename}")

        try:
            df = await read_file(contents, filename)
        except Exception as e:
            logger.error(f"[{client_ip}] Error reading file: {e}")
            raise HTTPException(400, "No se pudo leer el archivo")

        if df is None:
            raise HTTPException(400, "No se pudo leer el archivo")

        columns_info = []
        for col in df.columns:
            series = df[col]
            col_type = DashboardService.detect_column_type(series)

            info = {
                "name": col,
                "type": col_type,
                "sample_values": series.dropna().head(5).astype(str).tolist(),
                "null_count": int(series.isna().sum()),
                "unique_count": int(series.nunique()),
                "available_metrics": DashboardService.METRICS_BY_TYPE.get(col_type, ["count"]),
                "available_charts": DashboardService.CHARTS_BY_TYPE.get(col_type, ["table"])
            }

            # Estadísticas adicionales según el tipo
            if col_type == "numeric":
                info["stats"] = {
                    "min": float(series.min()) if not series.dropna().empty else None,
                    "max": float(series.max()) if not series.dropna().empty else None,
                    "mean": float(series.mean()) if not series.dropna().empty else None
                }
            elif col_type == "datetime":
                info["stats"] = {
                    "min": str(series.min()) if not series.dropna().empty else None,
                    "max": str(series.max()) if not series.dropna().empty else None
                }
            elif col_type == "text":
                info["stats"] = {
                    "avg_length": float(series.astype(str).str.len().mean()) if not series.dropna().empty else None,
                    "most_common": series.mode().iloc[0] if not series.mode().empty else None
                }

            columns_info.append(info)

        logger.info(f"[{client_ip}] Analyze done: {file.filename} - {len(df)} rows, {len(columns_info)} columns")

        return {
            "filename": file.filename,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": columns_info
        }

    @staticmethod
    def validate_metric_for_type(metric: str, column_type: str) -> Tuple[bool, str]:
        """
        Valida si una métrica es compatible con un tipo de dato.
        Retorna (es_valido, mensaje_error).
        """
        allowed_metrics = DashboardService.METRICS_BY_TYPE.get(column_type, ["count"])

        if metric not in allowed_metrics:
            return False, (
                f"La métrica '{metric}' no es válida para columnas de tipo '{column_type}'. "
                f"Métricas disponibles: {', '.join(allowed_metrics)}"
            )
        return True, ""

    @staticmethod
    async def calculate_metric(
        request: Request,
        file: UploadFile,
        column: str,
        metric: str,
        group_by: Optional[str] = None,
        filter_column: Optional[str] = None,
        filter_value: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calcula una métrica específica para una columna.
        Opcionalmente agrupada por otra columna y/o filtrada.
        """
        client_ip = _get_client_ip(request)

        # Rate limit check
        allowed, msg = rate_limiter.check_rate_limit(client_ip, DEFAULT_RATE_LIMITS)
        if not allowed:
            logger.warning(f"[{client_ip}] Rate limit excedido en dashboard/metric")
            raise HTTPException(429, msg)
        rate_limiter.record_request(client_ip)

        contents = await file.read()
        validate_file_size(len(contents), MAX_FILE_SIZE_BYTES)
        filename = file.filename.lower()

        try:
            df = await read_file(contents, filename)
        except Exception as e:
            logger.error(f"[{client_ip}] Error reading file: {e}")
            raise HTTPException(400, "No se pudo leer el archivo")

        if df is None:
            raise HTTPException(400, "No se pudo leer el archivo")

        if column not in df.columns:
            raise HTTPException(400, f"La columna '{column}' no existe en el archivo")

        # Detectar tipo de dato y validar métrica
        col_type = DashboardService.detect_column_type(df[column])
        is_valid, error_msg = DashboardService.validate_metric_for_type(metric, col_type)
        if not is_valid:
            raise HTTPException(400, error_msg)

        # Aplicar filtro si se especificó
        if filter_column and filter_value and filter_column in df.columns:
            df = df[df[filter_column].astype(str) == filter_value]

        # Calcular la métrica
        result = await DashboardService._compute_metric(df, column, metric, col_type, group_by)

        logger.debug(f"[{client_ip}] Metric calculated: {column}/{metric} -> {type(result).__name__}")

        return {
            "success": True,
            "column": column,
            "column_type": col_type,
            "metric": metric,
            "group_by": group_by,
            "filter": {"column": filter_column, "value": filter_value} if filter_column else None,
            "result": result
        }

    @staticmethod
    async def _compute_metric(
        df: pd.DataFrame,
        column: str,
        metric: str,
        col_type: str,
        group_by: Optional[str] = None
    ) -> Any:
        """Computa la métrica solicitada."""
        series = df[column]

        if group_by and group_by in df.columns:
            grouped = df.groupby(group_by)[column]

            if metric == "sum":
                return grouped.sum().reset_index().rename(columns={column: "value"}).to_dict("records")
            elif metric == "avg":
                return grouped.mean().reset_index().rename(columns={column: "value"}).to_dict("records")
            elif metric == "min":
                return grouped.min().reset_index().rename(columns={column: "value"}).to_dict("records")
            elif metric == "max":
                return grouped.max().reset_index().rename(columns={column: "value"}).to_dict("records")
            elif metric == "count":
                return grouped.size().reset_index(name="value").to_dict("records")
            elif metric == "median":
                return grouped.median().reset_index().rename(columns={column: "value"}).to_dict("records")
            elif metric == "std_dev":
                return grouped.std().reset_index().rename(columns={column: "value"}).to_dict("records")
            elif metric == "unique_count":
                return grouped.nunique().reset_index(name="value").to_dict("records")
            elif metric == "mode":
                result = []
                for name, group in grouped:
                    mode_val = group.mode().iloc[0] if not group.mode().empty else None
                    result.append({group_by: name, "value": mode_val})
                return result
            elif metric == "count_true":
                return grouped.apply(lambda x: (x == True).sum()).reset_index(name="value").to_dict("records")
            elif metric == "count_false":
                return grouped.apply(lambda x: (x == False).sum()).reset_index(name="value").to_dict("records")
            elif metric == "percentage_true":
                return grouped.apply(lambda x: (x == True).mean() * 100).reset_index(name="value").to_dict("records")
        else:
            # Sin agrupación
            if metric == "sum":
                return float(series.sum()) if not series.dropna().empty else 0
            elif metric == "avg":
                return float(series.mean()) if not series.dropna().empty else 0
            elif metric == "min":
                return float(series.min()) if col_type == "numeric" else str(series.min())
            elif metric == "max":
                return float(series.max()) if col_type == "numeric" else str(series.max())
            elif metric == "count":
                return int(series.count())
            elif metric == "median":
                return float(series.median()) if not series.dropna().empty else 0
            elif metric == "std_dev":
                return float(series.std()) if not series.dropna().empty else 0
            elif metric == "unique_count":
                return int(series.nunique())
            elif metric == "mode":
                return str(series.mode().iloc[0]) if not series.mode().empty else None
            elif metric == "avg_length":
                return float(series.astype(str).str.len().mean()) if not series.dropna().empty else 0
            elif metric == "range_days":
                if col_type == "datetime":
                    return (series.max() - series.min()).days if not series.dropna().empty else 0
                return None
            elif metric == "count_by_month":
                if col_type == "datetime":
                    return series.dt.to_period('M').value_counts().sort_index().reset_index()
                return None
            elif metric == "count_by_year":
                if col_type == "datetime":
                    return series.dt.to_period('Y').value_counts().sort_index().reset_index()
                return None
            elif metric == "count_true":
                return int((series == True).sum())
            elif metric == "count_false":
                return int((series == False).sum())
            elif metric == "percentage_true":
                return float((series == True).mean() * 100) if not series.dropna().empty else 0

        raise HTTPException(400, f"Métrica '{metric}' no implementada para tipo '{col_type}'")

    @staticmethod
    async def get_compatible_charts(column_type: str) -> List[str]:
        """Devuelve los tipos de gráficos compatibles con un tipo de dato."""
        return DashboardService.CHARTS_BY_TYPE.get(column_type, ["table"])

    @staticmethod
    async def validate_chart_config(column: str, metric: str, chart_type: str, columns_info: List[Dict]) -> Tuple[bool, str]:
        """
        Valida si una configuración de gráfico es válida.
        """
        col_info = next((c for c in columns_info if c["name"] == column), None)
        if not col_info:
            return False, f"La columna '{column}' no existe"

        col_type = col_info["type"]

        # Validar métrica
        is_valid, error_msg = DashboardService.validate_metric_for_type(metric, col_type)
        if not is_valid:
            return False, error_msg

        # Validar tipo de gráfico
        allowed_charts = DashboardService.CHARTS_BY_TYPE.get(col_type, ["table"])
        if chart_type not in allowed_charts:
            return False, (
                f"El tipo de gráfico '{chart_type}' no es compatible con columnas de tipo '{col_type}'. "
                f"Gráficos disponibles: {', '.join(allowed_charts)}"
            )

        return True, "Configuración válida"