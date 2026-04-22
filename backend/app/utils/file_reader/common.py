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

# ==================== VALIDACIÓN DE ARCHIVOS VACÍOS ====================

def validate_not_empty(contents: bytes, filename: str = "") -> bool:
    """
    Valida que el contenido del archivo no esté vacío.

    Args:
        contents: Contenido binario del archivo
        filename: Nombre del archivo (opcional, para mensajes de error)

    Returns:
        True si el archivo tiene contenido

    Raises:
        FileReadingError: Si el archivo está vacío
    """
    if not contents or len(contents) == 0:
        raise FileReadingError(
            f"El archivo {filename} está vacío. Por favor, sube un archivo con datos."
        )
    return True

def validate_not_corrupted(contents: bytes, filename: str = "") -> bool:
    """
    Valida que el archivo no esté corrupto o dañado.
    Versión mejorada con detección más estricta.
    """
    if not contents or len(contents) == 0:
        raise FileReadingError(f"El archivo {filename} está vacío.")
    
    sample = contents[:1000]  # Tomar una muestra más grande
    is_binary = b'\x00' in sample
    
    if not is_binary:
        # Es texto (posible CSV)
        try:
            decoded = sample.decode('utf-8', errors='replace')
            lines = [l.strip() for l in decoded.split('\n') if l.strip()]
            
            if not lines:
                raise FileReadingError(f"El archivo {filename} no contiene líneas legibles.")
            
            # ============ VALIDACIONES ADICIONALES ============
            
            # 1. Verificar que al menos una línea tenga estructura de CSV
            has_separator = False
            separators = [',', ';', '\t', '|', ':']
            for line in lines[:5]:  # primeras 5 líneas
                for sep in separators:
                    if line.count(sep) >= 1:
                        has_separator = True
                        break
                if has_separator:
                    break
            
            # 2. Si no tiene separadores, verificar que al menos tenga una estructura coherente
            if not has_separator:
                # Si todas las líneas son cortas (< 30 chars) y no tienen números, probablemente es basura
                all_short = all(len(line) < 30 for line in lines[:10])
                if all_short and len(lines) > 3:
                    # Puede ser una lista de palabras sueltas, no un CSV válido
                    raise FileReadingError(f"El archivo {filename} no tiene estructura de tabla válida.")
            
            # 3. Verificar consistencia de columnas (si hay varias líneas)
            if len(lines) >= 2:
                # Contar la cantidad esperada de columnas basada en la primera línea
                if has_separator:
                    # Encontrar el separador más común
                    sep_counts = {}
                    for line in lines[:5]:
                        for sep in separators:
                            if sep in line:
                                sep_counts[sep] = sep_counts.get(sep, 0) + line.count(sep)
                    
                    if sep_counts:
                        most_common_sep = max(sep_counts, key=sep_counts.get)
                        expected_cols = lines[0].count(most_common_sep) + 1
                        
                        # Verificar que las primeras 5 líneas tengan número similar de columnas
                        inconsistent = 0
                        for line in lines[1:5]:
                            actual_cols = line.count(most_common_sep) + 1
                            if abs(actual_cols - expected_cols) > 2:
                                inconsistent += 1
                        
                        if inconsistent >= 3:
                            raise FileReadingError(f"El archivo {filename} tiene estructura de columnas inconsistente.")
            
        except UnicodeDecodeError:
            raise FileReadingError(f"El archivo {filename} no se puede decodificar. Puede estar corrupto.")
    
    return True


def validate_dataframe_not_empty(df: pd.DataFrame, filename: str = "") -> bool:
    """
    Valida que el DataFrame tenga datos (al menos una fila).

    Args:
        df: DataFrame a validar
        filename: Nombre del archivo (opcional, para mensajes de error)

    Returns:
        True si el DataFrame tiene datos

    Raises:
        FileReadingError: Si el DataFrame está vacío
    """
    if df is None or df.empty:
        raise FileReadingError(
            f"El archivo {filename} no contiene datos. Verifica que tenga filas y columnas."
        )
    return True


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
