"""
Tests de integracion para endpoints de la API
Prueba los endpoints HTTP directamente
"""

import pytest
from fastapi.testclient import TestClient
from io import BytesIO
import sys
import os

# Agregar backend al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)


class TestUploadEndpoints:
    """Tests para endpoints de subida de archivos"""

    def test_upload_csv_success(self):
        """Prueba subida exitosa de CSV"""
        csv_content = b"cliente_id,nombre,email\n1,Jose,jose@test.com\n2,Maria,maria@test.com"

        response = client.post(
            "/api/v1/data/upload/csv",
            files={"file": ("test.csv", BytesIO(csv_content), "text/csv")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["rows"] == 2
        assert data["columns"] == ["cliente_id", "nombre", "email"]
        assert len(data["preview"]) == 2

    def test_upload_csv_invalid_extension(self):
        """Prueba subida con extension invalida"""
        response = client.post(
            "/api/v1/data/upload/csv",
            files={"file": ("test.txt", BytesIO(b"contenido"), "text/plain")}
        )

        assert response.status_code == 400
        assert "CSV" in response.json()["detail"]

    def test_upload_excel_success(self):
        """Prueba subida exitosa de Excel"""
        import pandas as pd

        df = pd.DataFrame({
            "cliente_id": [1, 2],
            "nombre": ["Jose", "Maria"],
            "email": ["jose@test.com", "maria@test.com"]
        })

        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        response = client.post(
            "/api/v1/data/upload/excel",
            files={"file": ("test.xlsx", excel_buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["rows"] == 2


class TestTransformEndpoints:
    """Tests para endpoints de transformacion"""

    def test_transform_dropna(self):
        """Prueba transformacion dropna - solo 1 fila completa"""
        # Solo la primera fila tiene datos completos
        csv_content = b"cliente_id,nombre,email\n1,Jose,jose@test.com\n2,,\n3,,"

        response = client.post(
            "/api/v1/data/transform?operation=dropna",
            files={"file": ("test.csv", BytesIO(csv_content), "text/csv")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["original_rows"] == 3
        assert data["transformed_rows"] == 1
        assert "nulos" in data["message"]

    def test_transform_fillna(self):
        """Prueba transformacion fillna"""
        csv_content = b"cliente_id,nombre,email\n1,Jose,jose@test.com\n2,,maria@test.com"

        response = client.post(
            "/api/v1/data/transform?operation=fillna&fill_value=SIN_NOMBRE",
            files={"file": ("test.csv", BytesIO(csv_content), "text/csv")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["original_rows"] == data["transformed_rows"]
        assert "SIN_NOMBRE" in data["message"]

    def test_transform_drop_duplicates(self):
        """Prueba transformacion drop_duplicates"""
        csv_content = b"cliente_id,nombre\n1,Jose\n2,Maria\n2,Maria"

        response = client.post(
            "/api/v1/data/transform?operation=drop_duplicates&key_columns=cliente_id",
            files={"file": ("test.csv", BytesIO(csv_content), "text/csv")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["original_rows"] == 3
        assert data["transformed_rows"] == 2
        assert "duplicadas" in data["message"]

    def test_transform_invalid_operation(self):
        """Prueba operacion invalida"""
        csv_content = b"cliente_id,nombre\n1,Jose"

        response = client.post(
            "/api/v1/data/transform?operation=invalid_op",
            files={"file": ("test.csv", BytesIO(csv_content), "text/csv")}
        )
        assert response.status_code == 400


class TestDetectDuplicatesEndpoints:
    """Tests para endpoint de deteccion de duplicados"""

    def test_detect_duplicates_with_key_columns(self):
        """Prueba deteccion de duplicados con columnas clave"""
        csv_content = b"cliente_id,nombre\n1,Jose\n2,Maria\n2,Maria"

        response = client.post(
            "/api/v1/data/detect-duplicates?key_columns=cliente_id",
            files={"file": ("test.csv", BytesIO(csv_content), "text/csv")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_rows"] == 3
        assert data["duplicated_rows"] == 2
        assert data["duplicate_groups"] == 1

    def test_detect_duplicates_no_duplicates(self):
        """Prueba deteccion cuando no hay duplicados"""
        csv_content = b"cliente_id,nombre\n1,Jose\n2,Maria\n3,Pedro"

        response = client.post(
            "/api/v1/data/detect-duplicates?key_columns=cliente_id",
            files={"file": ("test.csv", BytesIO(csv_content), "text/csv")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_rows"] == 3
        assert data["duplicated_rows"] == 0
        assert data["duplicate_groups"] == 0


class TestRootEndpoint:
    """Tests para endpoint raiz"""

    def test_root(self):
        """Prueba endpoint raiz"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Flintrex API" in response.json()["message"]

    def test_health(self):
        """Prueba endpoint de health check"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])