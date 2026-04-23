"""
Esquemas Pydantic para el módulo de datos.
Define la estructura de request/response de los endpoints.
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class FileInfo(BaseModel):
    """Información de un archivo procesado."""
    filename: str
    rows: int
    columns: int


class SchemaValidation(BaseModel):
    """Validación de esquema entre archivos."""
    total_columns: int
    common_columns: List[str]
    columns_by_file: Dict[str, List[str]]
    has_schema_differences: bool
    merge_mode_requested: str
    merge_mode_detected: str
    merge_mode_used: str
    merge_strategy: str


class UploadResponse(BaseModel):
    """Respuesta de upload CSV/Excel."""
    filename: str
    rows: int
    columns: List[str]
    preview: List[Dict[str, Any]]
    column_types: Dict[str, str]


class TransformResponse(BaseModel):
    """Respuesta de transformación de datos."""
    success: bool
    filename: str
    operation: str
    original_rows: int
    transformed_rows: int
    message: str
    columns: List[str]
    preview: List[Dict[str, Any]]


class DuplicateGroup(BaseModel):
    """Grupo de filas duplicadas."""
    count: int
    indices: List[int]
    rows: List[Dict[str, Any]]


class DetectDuplicatesResponse(BaseModel):
    """Respuesta de detección de duplicados."""
    success: bool
    total_rows: int
    duplicated_rows: int
    duplicate_groups: int
    groups: List[DuplicateGroup]
    key_columns_used: Any  # str o "TODAS"
    message: str


class MergeResponse(BaseModel):
    """Respuesta de merge de archivos."""
    success: bool
    files_processed: int
    files: List[FileInfo]
    original_rows: int
    transformed_rows: int
    message: str
    columns: List[str]
    schema_validation: SchemaValidation
    preview: List[Dict[str, Any]]



class FileHealthScore(BaseModel):
    """Score de salud de un archivo."""
    index: int
    filename: str
    health_score: float
    rows: int
    columns: int


class HarmonizeResponse(BaseModel):
    """Respuesta de armonización de archivos."""
    success: bool
    files_processed: int
    files: List[FileInfo]
    reference_file: str
    reference_index: int
    file_scores: List[FileHealthScore]
    combined_rows: int
    final_columns: List[str]
    columns: List[str]
    preview: List[Dict[str, Any]]



# ============ Dashboard Schemas ============

class ColumnInfo(BaseModel):
    """Información de una columna para el dashboard."""
    name: str
    type: str
    sample_values: List[str]
    null_count: int
    unique_count: int
    available_metrics: List[str]
    available_charts: List[str]
    stats: Optional[Dict[str, Any]] = None


class DashboardAnalyzeResponse(BaseModel):
    """Respuesta de análisis de columnas para dashboard."""
    filename: str
    total_rows: int
    total_columns: int
    columns: List[ColumnInfo]


class DashboardMetricResponse(BaseModel):
    """Respuesta de cálculo de métrica para dashboard."""
    success: bool
    column: str
    column_type: str
    metric: str
    group_by: Optional[str]
    filter: Optional[Dict[str, str]]
    result: Any


class DashboardValidationResponse(BaseModel):
    """Respuesta de validación de configuración de gráfico."""
    valid: bool
    message: str
    column: str
    metric: str
    chart_type: str