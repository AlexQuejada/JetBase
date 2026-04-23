"""
Tests de integración para DataService
Prueba el servicio principal de procesamiento de datos
"""

import pytest
import pandas as pd
import io
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.data_service import DataService
from fastapi import UploadFile, HTTPException


class MockRequest:
    """Mock de Request para testing"""
    def __init__(self):
        self.client = MagicMock()
        self.client.host = "127.0.0.1"
        self.headers = {}


class MockUploadFile:
    """Mock de UploadFile para testing"""

    def __init__(self, filename, content):
        self.filename = filename
        self._content = content

    async def read(self):
        return self._content


class TestDataServiceUpload:
    """Tests para metodos de upload"""

    @pytest.mark.asyncio
    async def test_upload_csv_success(self):
        """Upload CSV exitoso"""
        content = b'cliente_id,nombre,email\n1,Jose,jose@test.com\n2,Maria,maria@test.com'
        file = MockUploadFile('test.csv', content)
        request = MockRequest()

        result = await DataService.upload_file(request, file, allowed_extensions=('.csv',))

        assert result['filename'] == 'test.csv'
        assert result['rows'] == 2
        assert 'cliente_id' in result['columns']
        assert len(result['preview']) == 2

    @pytest.mark.asyncio
    async def test_upload_invalid_extension(self):
        """Upload con extension invalida"""
        file = MockUploadFile('test.txt', b'contenido')
        request = MockRequest()

        with pytest.raises(HTTPException) as exc_info:
            await DataService.upload_file(request, file, allowed_extensions=('.csv',))

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_corrupted_file(self):
        """Upload de archivo corrupto"""
        file = MockUploadFile('test.csv', b'\x00\x01\x02')
        request = MockRequest()

        with pytest.raises(HTTPException) as exc_info:
            await DataService.upload_file(request, file, allowed_extensions=('.csv',))

        assert exc_info.value.status_code == 400


class TestDataServiceDetectDuplicates:
    """Tests para deteccion de duplicados"""

    @pytest.mark.asyncio
    async def test_detect_duplicates_simple(self):
        """Deteccion simple de duplicados"""
        content = b'cliente_id,nombre\n1,Jose\n2,Maria\n2,Maria'
        file = MockUploadFile('test.csv', content)
        request = MockRequest()

        result = await DataService.detect_duplicates(request, file, 'cliente_id', False, True, True)

        assert result['success'] is True
        assert result['total_rows'] == 3
        assert result['duplicated_rows'] == 2
        assert result['duplicate_groups'] == 1

    @pytest.mark.asyncio
    async def test_detect_duplicates_no_duplicates(self):
        """Deteccion cuando no hay duplicados"""
        content = b'cliente_id,nombre\n1,Jose\n2,Maria\n3,Pedro'
        file = MockUploadFile('test.csv', content)
        request = MockRequest()

        result = await DataService.detect_duplicates(request, file, 'cliente_id', False, True, True)

        assert result['duplicated_rows'] == 0
        assert result['duplicate_groups'] == 0

    @pytest.mark.asyncio
    async def test_detect_duplicates_all_columns(self):
        """Deteccion considerando todas las columnas"""
        content = b'cliente_id,nombre\n1,Jose\n2,Maria\n3,Jose'
        file = MockUploadFile('test.csv', content)
        request = MockRequest()

        result = await DataService.detect_duplicates(request, file, None, False, True, True)

        # No hay duplicados exactos en todas las columnas
        assert result['duplicated_rows'] == 0


class TestDataServiceTransform:
    """Tests para transformaciones"""

    @pytest.mark.asyncio
    async def test_transform_dropna(self):
        """Transformacion dropna"""
        content = b'cliente_id,nombre,email\n1,Jose,jose@test.com\n2,,'
        file = MockUploadFile('test.csv', content)
        request = MockRequest()

        result = await DataService.transform(request, file, 'dropna', None, None, False, True, True, 'first')

        assert result['success'] is True
        assert result['original_rows'] == 2
        assert result['transformed_rows'] == 1
        assert 'nulos' in result['message']

    @pytest.mark.asyncio
    async def test_transform_fillna(self):
        """Transformacion fillna"""
        content = b'cliente_id,nombre,email\n1,Jose,jose@test.com\n2,,maria@test.com'
        file = MockUploadFile('test.csv', content)
        request = MockRequest()

        result = await DataService.transform(request, file, 'fillna', 'SIN_NOMBRE', None, False, True, True, 'first')

        assert result['success'] is True
        assert result['original_rows'] == result['transformed_rows']
        assert 'SIN_NOMBRE' in result['message']

    @pytest.mark.asyncio
    async def test_transform_invalid_operation(self):
        """Transformacion con operacion invalida"""
        content = b'cliente_id,nombre\n1,Jose'
        file = MockUploadFile('test.csv', content)
        request = MockRequest()

        with pytest.raises(HTTPException) as exc_info:
            await DataService.transform(request, file, 'invalid_op', None, None, False, True, True, 'first')

        assert exc_info.value.status_code == 400


class TestDataServiceMerge:
    """Tests para merge de archivos"""

    @pytest.mark.asyncio
    async def test_merge_union_same_schema(self):
        """Merge UNION con mismo esquema"""
        content1 = b'cliente_id,nombre\n1,Jose\n2,Maria'
        content2 = b'cliente_id,nombre\n3,Pedro\n4,Ana'
        files = [
            MockUploadFile('file1.csv', content1),
            MockUploadFile('file2.csv', content2)
        ]
        request = MockRequest()

        result = await DataService.merge(request, files, 'clean', None, None, False, True, True, 'first', 'union', 'inner')

        assert result['success'] is True
        assert result['files_processed'] == 2
        assert result['original_rows'] == 4
        assert result['schema_validation']['merge_mode_used'] == 'union'

    @pytest.mark.asyncio
    async def test_merge_join_by_key(self):
        """Merge JOIN por key_columns"""
        content1 = b'cliente_id,nombre\n1,Jose\n2,Maria'
        content2 = b'cliente_id,email\n1,jose@test.com\n2,maria@test.com'
        files = [
            MockUploadFile('clientes.csv', content1),
            MockUploadFile('emails.csv', content2)
        ]
        request = MockRequest()

        result = await DataService.merge(request, files, 'clean', None, 'cliente_id', False, True, True, 'first', 'join', 'inner')

        assert result['success'] is True
        assert result['original_rows'] == 4
        assert 'email' in result['columns']
        assert result['schema_validation']['merge_mode_used'] == 'join'

    @pytest.mark.asyncio
    async def test_merge_auto_detect(self):
        """Merge con deteccion automatica"""
        content1 = b'cliente_id,nombre\n1,Jose\n2,Maria'
        content2 = b'cliente_id,email\n1,jose@test.com\n2,maria@test.com'
        files = [
            MockUploadFile('clientes.csv', content1),
            MockUploadFile('emails.csv', content2)
        ]
        request = MockRequest()

        result = await DataService.merge(request, files, 'clean', None, None, False, True, True, 'first', 'auto', 'inner')

        # Debe detectar JOIN por el patron cliente_id
        assert result['schema_validation']['merge_mode_detected'] == 'join'

    @pytest.mark.asyncio
    async def test_merge_insufficient_files(self):
        """Merge con menos de 2 archivos"""
        files = [MockUploadFile('test.csv', b'a,b\n1,2')]
        request = MockRequest()

        with pytest.raises(HTTPException) as exc_info:
            await DataService.merge(request, files, 'clean', None, None, False, True, True, 'first', 'union', 'inner')

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_merge_with_operation(self):
        """Merge con operacion de limpieza"""
        content1 = b'cliente_id,nombre\n1,Jose'
        content2 = b'cliente_id,nombre\n1,Jose'  # Duplicado
        files = [
            MockUploadFile('file1.csv', content1),
            MockUploadFile('file2.csv', content2)
        ]
        request = MockRequest()

        result = await DataService.merge(request, files, 'drop_duplicates', None, 'cliente_id', False, True, True, 'first', 'union', 'inner')

        assert result['transformed_rows'] == 1  # Se elimino el duplicado


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
