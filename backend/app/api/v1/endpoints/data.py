"""
Endpoints de procesamiento de datos.
Controller puramente de enrutamiento - toda la logica esta en DataService.
"""
import io
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional, List

from app.services.data_service import DataService
from app.services.dashboard_service import DashboardService
from app.schemas.data_schemas import (
    UploadResponse,
    TransformResponse,
    DetectDuplicatesResponse,
    MergeResponse
)

router = APIRouter()


@router.post("/upload/csv", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """Sube y procesa un archivo CSV."""
    return await DataService.upload_file(file, allowed_extensions=('.csv',))


@router.post("/upload/excel", response_model=UploadResponse)
async def upload_excel(file: UploadFile = File(...)):
    """Sube y procesa un archivo Excel."""
    return await DataService.upload_file(file, allowed_extensions=('.xlsx', '.xls'))


@router.post("/detect-duplicates", response_model=DetectDuplicatesResponse)
async def detect_duplicates(
    file: UploadFile = File(...),
    key_columns: Optional[str] = None,
    case_sensitive: bool = False,
    normalize_whitespace: bool = True,
    normalize_accents: bool = True
):
    """Detecta duplicados SIN eliminarlos. Devuelve grupos para revision."""
    return await DataService.detect_duplicates(
        file, key_columns, case_sensitive, normalize_whitespace, normalize_accents
    )


@router.post("/transform", response_model=TransformResponse)
async def transform_data(
    file: UploadFile = File(...),
    operation: str = "dropna",
    fill_value: Optional[str] = None,
    key_columns: Optional[str] = None,
    case_sensitive: bool = False,
    normalize_whitespace: bool = True,
    normalize_accents: bool = True,
    keep: str = "first"
):
    """Operaciones de limpieza: dropna, fillna, drop_duplicates, clean."""
    return await DataService.transform(
        file, operation, fill_value, key_columns,
        case_sensitive, normalize_whitespace, normalize_accents, keep
    )


@router.post("/merge", response_model=MergeResponse)
async def merge_files(
    files: List[UploadFile] = File(...),
    operation: str = Form("clean"),
    fill_value: Optional[str] = Form(None),
    key_columns: Optional[str] = Form(None),
    case_sensitive: bool = Form(False),
    normalize_whitespace: bool = Form(True),
    normalize_accents: bool = Form(True),
    keep: str = Form("first"),
    merge_mode: str = Form("auto"),
    join_type: str = Form("inner")
):
    """
    Combina multiples archivos CSV o Excel.
    Modos: auto (detecta), union (vertical), join (horizontal por key_columns).
    """
    return await DataService.merge(
        files, operation, fill_value, key_columns,
        case_sensitive, normalize_whitespace, normalize_accents, keep,
        merge_mode, join_type
    )


@router.post("/merge/download")
async def merge_download(
    files: List[UploadFile] = File(...),
    operation: str = Form("clean"),
    fill_value: Optional[str] = Form(None),
    key_columns: Optional[str] = Form(None),
    case_sensitive: bool = Form(False),
    normalize_whitespace: bool = Form(True),
    normalize_accents: bool = Form(True),
    keep: str = Form("first"),
    merge_mode: str = Form("auto"),
    join_type: str = Form("inner"),
    download_format: str = Form("csv")
):
    """
    Combina multiples archivos y devuelve el resultado como archivo descargable.

    - download_format: "csv" o "excel"
    """
    content, filename, media_type = await DataService.merge_download(
        files, operation, fill_value, key_columns,
        case_sensitive, normalize_whitespace, normalize_accents, keep,
        merge_mode, join_type, download_format
    )

    return StreamingResponse(
        io.BytesIO(content),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ==================== DASHBOARD ENDPOINTS ====================

@router.post("/dashboard/analyze-columns")
async def dashboard_analyze_columns(file: UploadFile = File(...)):
    """
    Analiza un archivo y devuelve información de sus columnas con tipos detectados.
    Usado para poblar el selector de columnas en el dashboard.
    """
    return await DashboardService.analyze_columns(file)


@router.post("/dashboard/calculate-metric")
async def dashboard_calculate_metric(
    file: UploadFile = File(...),
    column: str = Form(...),
    metric: str = Form(...),
    group_by: Optional[str] = Form(None),
    filter_column: Optional[str] = Form(None),
    filter_value: Optional[str] = Form(None)
):
    """
    Calcula una métrica específica para una columna.
    Valida que la métrica sea compatible con el tipo de dato.

    Métricas por tipo:
    - numeric: sum, avg, min, max, count, median, std_dev
    - text: count, unique_count, mode, avg_length
    - datetime: count, min, max, range_days, count_by_month, count_by_year
    - boolean: count, count_true, count_false, percentage_true
    """
    return await DashboardService.calculate_metric(
        file, column, metric, group_by, filter_column, filter_value
    )


@router.post("/dashboard/validate-chart")
async def dashboard_validate_chart(
    file: UploadFile = File(...),
    column: str = Form(...),
    metric: str = Form(...),
    chart_type: str = Form(...)
):
    """
    Valida si una configuración de gráfico es válida para los datos.
    Retorna error si la métrica no es compatible con el tipo de dato.
    """
    columns_info = await DashboardService.analyze_columns(file)
    is_valid, message = await DashboardService.validate_chart_config(
        column, metric, chart_type, columns_info["columns"]
    )

    return {
        "valid": is_valid,
        "message": message,
        "column": column,
        "metric": metric,
        "chart_type": chart_type
    }
