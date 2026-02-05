"""Object storage for files."""

from pathlib import Path
import shutil
from typing import Optional


class ObjectStorage:
    """Simple file-based object storage."""
    
    def __init__(self, storage_dir: str = "data/storage"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_file(self, file_path: str, content: bytes, document_id: str) -> str:
        """Save a file and return the storage path."""
        file_extension = Path(file_path).suffix
        storage_path = self.storage_dir / f"{document_id}{file_extension}"
        
        with open(storage_path, 'wb') as f:
            f.write(content)
        
        return str(storage_path)
    
    def get_file(self, storage_path: str) -> Optional[bytes]:
        """Retrieve a file's content."""
        path = Path(storage_path)
        if path.exists():
            with open(path, 'rb') as f:
                return f.read()
        return None
    
    def delete_file(self, storage_path: str) -> bool:
        """Delete a file."""
        path = Path(storage_path)
        if path.exists():
            path.unlink()
            return True
        return False
    
    def copy_from_data_dir(self, source_file: str, document_id: str) -> str:
        """Copy a file from the data directory."""
        source = Path(source_file)
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source_file}")
        
        file_extension = source.suffix
        storage_path = self.storage_dir / f"{document_id}{file_extension}"
        shutil.copy(source, storage_path)
        
        return str(storage_path)


# Global object storage instance
object_storage = ObjectStorage()
