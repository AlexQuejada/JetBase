"""
Paquete para lectura robusta de archivos CSV y Excel.

API Pública:
    - read_file: Lee CSV o Excel según extensión
    - read_csv_robust: Lee CSV con detección automática de encoding/separador
    - read_excel_robust: Lee Excel con soporte multi-hoja

Ejemplo:
    from app.utils.file_reader import read_file
    df = await read_file(contents, "archivo.csv")
"""

from .csv_handler import read_csv_robust
from .excel_handler import read_excel_robust
from .core import read_file

__all__ = ['read_file', 'read_csv_robust', 'read_excel_robust']
