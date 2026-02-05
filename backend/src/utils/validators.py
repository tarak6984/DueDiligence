"""Validation utilities."""

from typing import List
from ..models import DocumentScope


def validate_document_scope(scope: DocumentScope, selected_document_ids: List[str]) -> bool:
    """Validate document scope configuration."""
    if scope == DocumentScope.SELECTED_DOCS:
        return len(selected_document_ids) > 0
    return True


def validate_file_type(filename: str) -> bool:
    """Validate if file type is supported."""
    supported_extensions = ['.pdf', '.docx', '.xlsx', '.pptx']
    return any(filename.lower().endswith(ext) for ext in supported_extensions)


def get_file_type(filename: str) -> str:
    """Get file type from filename."""
    extension = filename.lower().split('.')[-1]
    type_map = {
        'pdf': 'PDF',
        'docx': 'DOCX',
        'xlsx': 'XLSX',
        'pptx': 'PPTX'
    }
    return type_map.get(extension, 'UNKNOWN')
