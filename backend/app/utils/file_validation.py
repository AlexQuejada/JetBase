"""
Utilidades de validación de archivos.
"""
import math
from fastapi import HTTPException


class FileValidationError(Exception):
    """Error de validación de archivo."""
    pass


def format_size(size_bytes: int) -> str:
    """Convierte bytes a string legible (KB, MB, GB)."""
    if size_bytes == 0:
        return "0 B"
    units = ['B', 'KB', 'MB', 'GB']
    unit_idx = int(math.log10(size_bytes) // 3)
    size = size_bytes / (1024 ** unit_idx)
    return f"{size:.1f} {units[unit_idx]}"


def validate_file_size(content_length: int, max_size_bytes: int) -> None:
    """
    Valida que el archivo no exceda el tamaño máximo.

    Raises:
        HTTPException 413 si el archivo es demasiado grande
    """
    if content_length > max_size_bytes:
        size_str = format_size(content_length)
        max_str = format_size(max_size_bytes)
        raise HTTPException(
            413,
            f"Archivo demasiado grande: {size_str}. Límite máximo: {max_str}"
        )


def validate_file_signature(content: bytes) -> tuple[bool, str]:
    """
    Valida que el archivo tenga una firma válida (magic bytes).

    Returns:
        Tuple de (es_valido, tipo_detectado)
    """
    if len(content) < 4:
        return False, "unknown"

    # Firmas conocidas
    signatures = {
        # CSV
        b'PK': 'zip/xlsx',  # XLSX es un ZIP
        b'\xef\xbb\xbf': 'csv',  # UTF-8 BOM
        b',': 'csv',  # Comienza con coma (común en CSV)

        # Excel antiguo
        b'\xd0\xcf': 'xls',  # OLE Compound Document

        # Plain text
    }

    # Verificar firma binaria
    first_bytes = content[:4]

    if first_bytes[:2] == b'PK':
        # XLSX o DOCX (ZIP)
        return True, 'xlsx'
    elif first_bytes[:3] == b'\xef\xbb\xbf':
        return True, 'csv'
    elif first_bytes[:4] == b'\xd0\xcf\x11\xe0':
        return True, 'xls'
    elif first_bytes[:1] in [b',', b'"', b'a', b'b', b'c', b'd', b'e', b'f',
                               b'g', b'h', b'i', b'j', b'k', b'l', b'm', b'n',
                               b'o', b'p', b'q', b'r', b's', b't', b'u', b'v',
                               b'w', b'x', b'y', b'z', b'A', b'B', b'C', b'D',
                               b'E', b'F', b'G', b'H', b'I', b'J', b'K', b'L',
                               b'M', b'N', b'O', b'P', b'Q', b'R', b'S', b'T',
                               b'U', b'V', b'W', b'X', b'Y', b'Z']:
        # Parece texto plano (CSV可能性)
        return True, 'csv'

    return False, 'unknown'