from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import io
from typing import List, Dict, Any

router = APIRouter()

@router.post("/upload/csv")
async def upload_csv(file: UploadFile = File(...)):
    
    # Validar que sea un CSV
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "El archivo debe ser CSV")
    
    try:
        # Leer el archivo

        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Convertir a JSON (solo primeras 100 filas para no saturar)

        preview = df.head(100).fillna("").to_dict(orient='records')
        
        return {
            "filename": file.filename,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": preview,
            "column_types": df.dtypes.astype(str).to_dict()
        }
    
    except Exception as e:
        raise HTTPException(400, f"Error al procesar el archivo: {str(e)}")
    
@router.post("/upload/excel")
async def upload_excel(file: UploadFile = File(...)):
    """
    Sube un archivo Excel (.xlsx, .xls) y devuelve su estructura
    """
    
    # Validar extensión
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(400, "El archivo debe ser Excel (.xlsx o .xls)")
    
    try:
        # Leer el archivo
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Devolver información
        return {
            "filename": file.filename,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": df.head(100).fillna("").to_dict(orient='records'),
            "column_types": df.dtypes.astype(str).to_dict()
        }
    
    except Exception as e:
        raise HTTPException(400, f"Error al leer el Excel: {str(e)}")
    
from typing import Optional

@router.post("/transform")
async def transform_data(
    file: UploadFile = File(...),
    operation: str = "dropna",  # dropna, fillna, drop_duplicates
    fill_value: Optional[float] = None,
    column: Optional[str] = None
):
    
    # Leer según extensión
    contents = await file.read()
    filename = file.filename.lower()
    
    if filename.endswith('.csv'):
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    elif filename.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(io.BytesIO(contents))
    else:
        raise HTTPException(400, "Formato no soportado. Use CSV o Excel")
    
    original_rows = len(df)
    
    # Aplicar transformación
    if operation == "dropna":
        df = df.dropna()
        message = f"Eliminadas {original_rows - len(df)} filas con valores nulos"
    
    elif operation == "fillna":
        if fill_value is None:
            raise HTTPException(400, "fillna requiere el parámetro fill_value")
        df = df.fillna(fill_value)
        message = f"Rellenados valores nulos con {fill_value}"
    
    elif operation == "drop_duplicates":
        df = df.drop_duplicates()
        message = f"Eliminadas {original_rows - len(df)} filas duplicadas"
    
    else:
        raise HTTPException(400, "Operación no soportada")
    
    return {
        "filename": file.filename,
        "operation": operation,
        "original_rows": original_rows,
        "transformed_rows": len(df),
        "message": message,
        "preview": df.head(100).fillna("").to_dict(orient='records')
    }