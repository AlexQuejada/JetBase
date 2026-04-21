"""
Funciones principales de lectura de archivos.
"""
from typing import Optional
import pandas as pd

from .csv_handler import read_csv_robust
from .excel_handler import read_excel_robust


async def read_file(
    contents: bytes,
    filename: str,
    sheet_name: Optional[str] = None,
    combine_sheets: bool = False
) -> Optional[pd.DataFrame]:
    """
    Lee CSV o Excel de forma robusta según la extensión del archivo.

    Args:
        contents: Contenido binario del archivo
        filename: Nombre del archivo (para detectar tipo)
        sheet_name: Para Excel, nombre de hoja específica
        combine_sheets: Para Excel, combinar todas las hojas

    Returns:
        DataFrame o None si no se puede leer

    Examples:
        # Leer CSV
        df = await read_file(contents, "datos.csv")

        # Leer Excel primera hoja
        df = await read_file(contents, "datos.xlsx")

        # Leer hoja específica de Excel
        df = await read_file(contents, "datos.xlsx", sheet_name="Ventas")

        # Combinar todas las hojas
        df = await read_file(contents, "datos.xlsx", combine_sheets=True)
    """
    filename_lower = filename.lower()

    if filename_lower.endswith('.csv'):
        return await read_csv_robust(contents)

    if filename_lower.endswith(('.xlsx', '.xls', '.xlsm', '.xltx', '.xlt')):
        return await read_excel_robust(contents, sheet_name, combine_sheets)

    return None
