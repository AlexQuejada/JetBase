from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.uploaded_file import UploadedFile
import pandas as pd
import io
from typing import Optional
import json

router = APIRouter()

# ==================== UPLOAD CSV ====================
@router.post("/upload/csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "El archivo debe ser CSV")
    
    try:
        contents = await file.read()
        
        # Intentar decodificar con UTF-8
        try:
            text = contents.decode('utf-8')
        except UnicodeDecodeError:
            # Si falla UTF-8, intentar con latin-1
            text = contents.decode('latin-1')
        
        df = pd.read_csv(io.StringIO(text))
        
        preview = df.head(100).fillna("").to_dict(orient='records')
        
        return {
            "filename": file.filename,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": preview,
            "column_types": df.dtypes.astype(str).to_dict()
        }
    
    except Exception as e:
        # Devolver el error específico
        raise HTTPException(400, f"Error al procesar el archivo: {str(e)}")


# ==================== UPLOAD EXCEL ====================
@router.post("/upload/excel")
async def upload_excel(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(400, "El archivo debe ser Excel (.xlsx o .xls)")
    
    try:
        contents = await file.read()
        
        # Leer Excel (pandas lo maneja bien, no necesita decodificación)
        df = pd.read_excel(io.BytesIO(contents))
        
        preview = df.head(100).fillna("").to_dict(orient='records')
        
        return {
            "filename": file.filename,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": preview,
            "column_types": df.dtypes.astype(str).to_dict()
        }
    
    except Exception as e:
        raise HTTPException(400, f"Error al leer el Excel: {str(e)}")


# ==================== TRANSFORM (CON GUARDADO EN BD) ====================
@router.post("/transform")
async def transform_data(
    file: UploadFile = File(...),
    operation: str = "dropna",
    fill_value: Optional[float] = None
):
    contents = await file.read()              # ← DEFINIDA
    filename = file.filename.lower()          # ← DEFINIDA
    
    # ==================== LEER ARCHIVO ====================
    try:
        if filename.endswith('.csv'):
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            for enc in encodings:
                try:
                    df = pd.read_csv(
                        io.BytesIO(contents),
                        encoding=enc,
                        errors="replace"
                    )
                    break
                except Exception:
                    continue
            if df is None:
                raise HTTPException(400, "No se pudo leer el CSV")
        
        elif filename.endswith(('.xlsx', '.xls')):
            try:
                df = pd.read_excel(io.BytesIO(contents), engine='openpyxl')
            except Exception as e:
                raise HTTPException(400, f"Error al leer Excel: {str(e)}")
        
        else:
            raise HTTPException(400, "Formato no soportado")
    
    except Exception as e:
        raise HTTPException(400, f"Error al leer el archivo: {str(e)}")
    
    original_rows = len(df)
    
    # ==================== TRANSFORMACIONES ====================
    if operation == "dropna":
        df = df.dropna()
        message = f"Eliminadas {original_rows - len(df)} filas con valores nulos"
    elif operation == "fillna":
        if fill_value is None:
            raise HTTPException(400, "fillna requiere fill_value")
        df = df.fillna(fill_value)
        message = f"Rellenados valores nulos con {fill_value}"
    elif operation == "drop_duplicates":
        df = df.drop_duplicates()
        message = f"Eliminadas {original_rows - len(df)} filas duplicadas"
    else:
        raise HTTPException(400, "Operación no soportada")
    
    # ==================== RESPUESTA ====================
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
@router.post("/transform")
async def transform_data(
    file: UploadFile = File(...),
    operation: str = "dropna",
    fill_value: Optional[float] = None,
    db: Session = Depends(get_db)
):
    contents = await file.read()
    filename = file.filename.lower()
    
    # ==================== LEER ARCHIVO ====================
    try:
        if filename.endswith('.csv'):
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            for enc in encodings:
                try:
                    df = pd.read_csv(
                        io.BytesIO(contents),
                        encoding=enc,
                        errors="replace"
                    )
                    break
                except Exception:
                    continue
            if df is None:
                raise HTTPException(400, "No se pudo leer el CSV")
        
        elif filename.endswith(('.xlsx', '.xls')):
            try:
                df = pd.read_excel(io.BytesIO(contents), engine='openpyxl')
            except Exception as e:
                raise HTTPException(400, f"Error al leer Excel: {str(e)}")
        
        else:
            raise HTTPException(400, "Formato no soportado")
    
    except Exception as e:
        raise HTTPException(400, f"Error al leer el archivo: {str(e)}")
    
    original_rows = len(df)
    
    # ==================== TRANSFORMACIONES ====================
    if operation == "dropna":
        df = df.dropna()
        message = f"Eliminadas {original_rows - len(df)} filas con valores nulos"
    
    elif operation == "fillna":
        if fill_value is None:
            raise HTTPException(400, "fillna requiere fill_value")
        df = df.fillna(fill_value)
        message = f"Rellenados valores nulos con {fill_value}"
    
    elif operation == "drop_duplicates":
        df = df.drop_duplicates()
        message = f"Eliminadas {original_rows - len(df)} filas duplicadas"
    
    else:
        raise HTTPException(400, "Operación no soportada")
    
    # ==================== LIMPIEZA SEGURA ====================
    df = df.where(pd.notnull(df), None)
    safe_columns = [str(col) for col in df.columns]
    
    # ==================== RESPUESTA (SIN GUARDAR EN BD) ====================
    return {
        "filename": file.filename,
        "operation": operation,
        "original_rows": original_rows,
        "transformed_rows": len(df),
        "message": message,
        "columns": safe_columns,
        "preview": df.head(100).fillna("").astype(str).to_dict(orient='records')
    }