"""
Delegación de servicios de datos.
Mantiene la interfaz DataService para backwards compatibility.
"""
from fastapi import Request
from typing import List, Optional, Tuple

from app.services.upload_service import upload_file as _upload_file
from app.services.dedup_service import detect_duplicates as _detect_duplicates, transform as _transform
from app.services.merge_extended_service import merge as _merge, merge_download as _merge_download
from app.services.harmonize_extended_service import harmonize as _harmonize, harmonize_download as _harmonize_download


class DataService:
    """Wrapper de métodos estáticos para backwards compatibility."""

    @staticmethod
    async def upload_file(request: Request, file, allowed_extensions: tuple) -> dict:
        return await _upload_file(request, file, allowed_extensions)

    @staticmethod
    async def detect_duplicates(
        request: Request,
        file,
        key_columns: Optional[str],
        case_sensitive: bool,
        normalize_whitespace: bool,
        normalize_accents: bool
    ) -> dict:
        return await _detect_duplicates(
            request, file, key_columns, case_sensitive, normalize_whitespace, normalize_accents
        )

    @staticmethod
    async def transform(
        request: Request,
        file,
        operation: str,
        fill_value: Optional[str],
        key_columns: Optional[str],
        case_sensitive: bool,
        normalize_whitespace: bool,
        normalize_accents: bool,
        keep: str
    ) -> dict:
        return await _transform(
            request, file, operation, fill_value, key_columns,
            case_sensitive, normalize_whitespace, normalize_accents, keep
        )

    @staticmethod
    async def merge(
        request: Request,
        files: List,
        operation: str,
        fill_value: Optional[str],
        key_columns: Optional[str],
        case_sensitive: bool,
        normalize_whitespace: bool,
        normalize_accents: bool,
        keep: str,
        merge_mode: str,
        join_type: str
    ) -> dict:
        return await _merge(
            request, files, operation, fill_value, key_columns,
            case_sensitive, normalize_whitespace, normalize_accents, keep,
            merge_mode, join_type
        )

    @staticmethod
    async def merge_download(
        request: Request,
        files: List,
        operation: str,
        fill_value: Optional[str],
        key_columns: Optional[str],
        case_sensitive: bool,
        normalize_whitespace: bool,
        normalize_accents: bool,
        keep: str,
        merge_mode: str,
        join_type: str,
        download_format: str = "csv"
    ) -> Tuple[bytes, str, str]:
        return await _merge_download(
            request, files, operation, fill_value, key_columns,
            case_sensitive, normalize_whitespace, normalize_accents, keep,
            merge_mode, join_type, download_format
        )

    @staticmethod
    async def harmonize(
        request: Request,
        files: List,
        case_sensitive: bool,
        normalize_whitespace: bool,
        normalize_accents: bool
    ) -> dict:
        return await _harmonize(
            request, files, case_sensitive, normalize_whitespace, normalize_accents
        )

    @staticmethod
    async def harmonize_download(
        request: Request,
        files: List,
        case_sensitive: bool,
        normalize_whitespace: bool,
        normalize_accents: bool,
        download_format: str = "csv"
    ) -> Tuple[bytes, str, str]:
        return await _harmonize_download(
            request, files, case_sensitive, normalize_whitespace, normalize_accents, download_format
        )
