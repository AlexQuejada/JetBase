"""
Manejador de lectura robusta de archivos CSV.
"""
import io
import csv
import pandas as pd
from typing import Optional

from .common import (
    COMMON_ENCODINGS,
    COMMON_SEPARATORS,
    detect_bom,
    detect_separator_sample,
    clean_dataframe,
    FileReadingError,
)


def _try_read_csv_with_encoding(content: bytes, encoding: str) -> Optional[pd.DataFrame]:
    """
    Intenta leer CSV con un encoding específico.

    Args:
        content: Contenido binario
        encoding: Encoding a usar

    Returns:
        DataFrame o None
    """
    try:
        content_str = content.decode(encoding, errors='replace')
    except Exception:
        return None

    separator = detect_separator_sample(content_str)

    # Intentar con separador detectado
    if separator:
        try:
            df = pd.read_csv(
                io.StringIO(content_str),
                sep=separator,
                engine='python',
                on_bad_lines='skip',
                skip_blank_lines=True,
                quoting=csv.QUOTE_MINIMAL,
                quotechar='"',
                escapechar='\\',
                doublequote=True,
            )
            if len(df.columns) > 0:
                return clean_dataframe(df)
        except Exception:
            pass

    # Probar todos los separadores
    for sep in COMMON_SEPARATORS:
        try:
            df = pd.read_csv(
                io.StringIO(content_str),
                sep=sep,
                engine='python',
                on_bad_lines='skip',
                skip_blank_lines=True,
                quoting=csv.QUOTE_MINIMAL,
                quotechar='"',
                escapechar='\\',
                doublequote=True,
            )
            if len(df.columns) > 1:
                return clean_dataframe(df)
        except Exception:
            continue

    # Fallback con engine C para archivos grandes
    if separator:
        try:
            df = pd.read_csv(
                io.BytesIO(content.encode(encoding)),
                sep=separator,
                engine='c',
                on_bad_lines='skip',
                skip_blank_lines=True,
            )
            if len(df.columns) > 0:
                return clean_dataframe(df)
        except Exception:
            pass

    return None


async def read_csv_robust(contents: bytes) -> Optional[pd.DataFrame]:
    """
    Lee un CSV probando múltiples codificaciones y separadores.

    Maneja:
    - BOM (UTF-8, UTF-16, UTF-32)
    - Múltiples encodings (UTF-8, Latin-1, Windows-1252, etc.)
    - Separadores automáticos (coma, punto y coma, tab, pipe)
    - Líneas vacías y filas incompletas
    - Campos entre comillas con escapes

    Args:
        contents: Contenido binario del archivo CSV

    Returns:
        DataFrame limpio o None si no se puede leer
    """
    if not contents or len(contents) < 5:
        return None

    # Detectar y remover BOM
    content, detected_encoding, _ = detect_bom(contents)

    # Preparar lista de encodings a probar
    encodings_to_try = []
    if detected_encoding:
        encodings_to_try.append(detected_encoding)
    encodings_to_try.extend(COMMON_ENCODINGS)

    # Intentar cada encoding
    for enc in encodings_to_try:
        try:
            df = _try_read_csv_with_encoding(content, enc)
            if df is not None and len(df.columns) > 0:
                return df
        except Exception:
            continue

    # Último recurso - lectura permisiva con latin-1
    try:
        df = pd.read_csv(
            io.BytesIO(content),
            encoding='latin-1',
            sep=None,
            engine='python',
            on_bad_lines='skip',
            skip_blank_lines=True,
        )
        if df is not None and len(df.columns) > 0:
            return clean_dataframe(df)
    except Exception:
        pass

    return None
