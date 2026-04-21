"""
Constantes y utilidades compartidas para lectura de archivos.
"""
import re
import pandas as pd
from typing import Tuple, Optional


# Encodings comunes ordenados por probabilidad
COMMON_ENCODINGS = [
    'utf-8-sig',   # UTF-8 con BOM
    'utf-8',
    'latin-1',
    'cp1252',       # Windows-1252
    'iso-8859-1',
    'iso-8859-15',
    'latin-2',
    'cp1250',       # Windows-1250 (Europa Central)
    'gbk',          # Chino simplificado
    'gb2312',
    'big5',         # Chino tradicional
    'shift_jis',    # Japonés
    'euc-jp',
    'euc-kr',       # Coreano
    'koi8-r',       # Ruso
    'cp1251',       # Windows-1251 (Cirílico)
    'mac_roman',    # Mac OS Roman
    'utf-16',
    'utf-16-le',
    'utf-16-be',
]

# Separadores ordenados por frecuencia
COMMON_SEPARATORS = [',', ';', '\t', '|', ':', '~', '^']


class FileReadingError(Exception):
    """Excepción para errores de lectura de archivos."""
    pass


def detect_bom(contents: bytes) -> Tuple[bytes, Optional[str], int]:
    """
    Detecta y remueve BOM (Byte Order Mark).

    Args:
        contents: Contenido binario del archivo

    Returns:
        Tupla de (contenido_sin_bom, encoding_detectado, bytes_removidos)
    """
    boms = [
        (b'\xef\xbb\xbf', 'utf-8'),
        (b'\xff\xfe\x00\x00', 'utf-32-le'),
        (b'\x00\x00\xfe\xff', 'utf-32-be'),
        (b'\xff\xfe', 'utf-16-le'),
        (b'\xfe\xff', 'utf-16-be'),
    ]

    for bom, encoding in boms:
        if contents.startswith(bom):
            return contents[len(bom):], encoding, len(bom)

    return contents, None, 0


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia el DataFrame:
    - Elimina filas completamente vacías
    - Elimina columnas sin nombre o completamente vacías
    - Normaliza nombres de columnas

    Args:
        df: DataFrame a limpiar

    Returns:
        DataFrame limpio
    """
    if df is None or df.empty:
        return df

    # Eliminar filas donde TODAS las celdas están vacías
    df = df.dropna(how='all')

    # Eliminar columnas donde TODAS las celdas están vacías
    df = df.dropna(axis=1, how='all')

    # Limpiar nombres de columnas
    new_columns = []
    seen = {}
    for col in df.columns:
        col_str = str(col).strip() if pd.notna(col) else ''
        col_str = re.sub(r'\s+', ' ', col_str)

        if not col_str or col_str.lower() in ['nan', 'none', 'null', '']:
            col_str = f'Column_{len(new_columns)}'

        # Manejar duplicados
        original = col_str
        counter = seen.get(col_str, 0)
        while col_str in seen:
            counter += 1
            col_str = f"{original}_{counter}"
        seen[col_str] = counter

        new_columns.append(col_str)

    df.columns = new_columns
    return df


def detect_separator_sample(content_str: str) -> Optional[str]:
    """
    Detecta el separador analizando una muestra del contenido.

    Args:
        content_str: Contenido del archivo como string

    Returns:
        Separador detectado o None
    """
    lines = [line for line in content_str.split('\n') if line.strip()][:10]
    if not lines:
        return None

    first_line = lines[0]
    scores = {}

    for sep in COMMON_SEPARATORS:
        count = first_line.count(sep)
        if count == 0:
            continue

        score = count
        expected_cols = count + 1

        # Verificar consistencia
        consistent = True
        for line in lines[1:]:
            if line.strip():
                cols = line.count(sep) + 1
                if abs(cols - expected_cols) > 1:
                    consistent = False
                    break

        if consistent:
            score *= 2

        # Bonus para separadores comunes
        if sep == ',':
            score += 1
        elif sep == ';':
            score += 0.5

        scores[sep] = score

    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]

    return None
