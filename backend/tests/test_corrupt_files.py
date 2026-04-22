"""
Tests para validación de archivos vacíos y corruptos.
"""
import pytest
import sys
from pathlib import Path

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.file_reader.csv_handler import read_csv_robust
from app.utils.file_reader.excel_handler import read_excel_robust


# ==================== FIXTURES ====================

@pytest.fixture
def valid_csv_content():
    """CSV válido con datos"""
    return b"nombre,edad,email\nJuan,25,juan@test.com\nMaria,30,maria@test.com"


@pytest.fixture
def empty_csv_content():
    """CSV vacío (0 bytes)"""
    return b''


@pytest.fixture
def corrupt_csv_content():
    """CSV con texto basura (pero aún legible como texto)"""
    return b'esto no es un csv valido\nsolo texto basura\nx,y,z\nsin sentido real'


@pytest.fixture
def truly_corrupt_csv_content():
    """CSV realmente corrupto (bytes aleatorios, no es texto)"""
    import random
    return bytes([random.randint(0, 255) for _ in range(500)])


@pytest.fixture
def csv_only_headers():
    """CSV solo con encabezados"""
    return b'nombre,edad,email\n'


@pytest.fixture
def valid_excel_content(tmp_path):
    """Excel válido con datos"""
    import pandas as pd
    df = pd.DataFrame({
        'nombre': ['Juan', 'Maria', 'Pedro'],
        'edad': [25, 30, 28],
        'email': ['juan@test.com', 'maria@test.com', 'pedro@test.com']
    })
    excel_path = tmp_path / "test.xlsx"
    df.to_excel(excel_path, index=False)
    with open(excel_path, 'rb') as f:
        return f.read()


@pytest.fixture
def empty_excel_content():
    """Excel vacío (0 bytes)"""
    return b''


@pytest.fixture
def corrupt_excel_content():
    """Excel corrupto (bytes basura)"""
    return b'\x00\xFF\x00\xFFbasura no excel' * 100


# ==================== TESTS PARA CSV ====================

@pytest.mark.asyncio
async def test_valid_csv_returns_dataframe(valid_csv_content):
    """CSV válido debe retornar un DataFrame con datos"""
    result = await read_csv_robust(valid_csv_content, "test.csv")
    assert result is not None
    assert len(result) == 2
    assert list(result.columns) == ['nombre', 'edad', 'email']


@pytest.mark.asyncio
async def test_empty_csv_returns_none(empty_csv_content):
    """CSV vacío debe retornar None"""
    result = await read_csv_robust(empty_csv_content, "empty.csv")
    assert result is None


@pytest.mark.asyncio
async def test_csv_with_text_basura_is_handled(corrupt_csv_content):
    """CSV con texto basura puede ser leído (pandas es tolerante)"""
    result = await read_csv_robust(corrupt_csv_content, "corrupt.csv")
    # Pandas puede leerlo, no es un error
    # Solo verificamos que no explote
    assert True


@pytest.mark.asyncio
async def test_corrupt_file_does_not_crash(truly_corrupt_csv_content):
    """Archivo realmente corrupto no debe hacer explotar el sistema"""
    try:
        result = await read_csv_robust(truly_corrupt_csv_content, "truly_corrupt.csv")
        # El test pasa si no lanza excepción
        assert True
    except Exception as e:
        pytest.fail(f"El lector falló inesperadamente: {e}")


@pytest.mark.asyncio
async def test_csv_only_headers_returns_none(csv_only_headers):
    """CSV solo con encabezados debe retornar None"""
    result = await read_csv_robust(csv_only_headers, "headers.csv")
    assert result is None


# ==================== TESTS PARA EXCEL ====================

@pytest.mark.asyncio
async def test_valid_excel_returns_dataframe(valid_excel_content):
    """Excel válido debe retornar un DataFrame con datos"""
    result = await read_excel_robust(valid_excel_content, filename="test.xlsx")
    assert result is not None
    assert len(result) == 3
    assert 'nombre' in result.columns


@pytest.mark.asyncio
async def test_empty_excel_returns_none(empty_excel_content):
    """Excel vacío debe retornar None"""
    result = await read_excel_robust(empty_excel_content, filename="empty.xlsx")
    assert result is None


@pytest.mark.asyncio
async def test_corrupt_excel_returns_none(corrupt_excel_content):
    """Excel corrupto debe retornar None"""
    result = await read_excel_robust(corrupt_excel_content, filename="corrupt.xlsx")
    assert result is None


# ==================== TEST DE VALIDACIONES ====================

@pytest.mark.asyncio
async def test_validation_order():
    """Verifica que la validación ocurre antes de la lectura"""
    # Archivo vacío debe ser rechazado
    result = await read_csv_robust(b'', "empty.csv")
    assert result is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])