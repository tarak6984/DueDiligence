"""Database manager for structured data."""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from pathlib import Path


class DatabaseManager:
    """Simple file-based database for demo purposes."""
    
    def __init__(self, data_dir: str = "data/db"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._init_collections()
    
    def _init_collections(self):
        """Initialize data collections."""
        self.collections = {
            "projects": {},
            "questions": {},
            "sections": {},
            "answers": {},
            "documents": {},
            "requests": {},
            "evaluations": {}
        }
        self._load_all()
    
    def _get_collection_path(self, collection: str) -> Path:
        """Get path for a collection file."""
        return self.data_dir / f"{collection}.json"
    
    def _load_all(self):
        """Load all collections from disk."""
        for collection in self.collections.keys():
            path = self._get_collection_path(collection)
            if path.exists():
                with open(path, 'r') as f:
                    self.collections[collection] = json.load(f)
    
    def _save_collection(self, collection: str):
        """Save a collection to disk."""
        path = self._get_collection_path(collection)
        with open(path, 'w') as f:
            json.dump(self.collections[collection], f, indent=2, default=str)
    
    def insert(self, collection: str, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a document into a collection."""
        self.collections[collection][id] = data
        self._save_collection(collection)
        return data
    
    def get(self, collection: str, id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        return self.collections[collection].get(id)
    
    def update(self, collection: str, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a document."""
        if id in self.collections[collection]:
            self.collections[collection][id].update(data)
            self._save_collection(collection)
            return self.collections[collection][id]
        return None
    
    def delete(self, collection: str, id: str) -> bool:
        """Delete a document."""
        if id in self.collections[collection]:
            del self.collections[collection][id]
            self._save_collection(collection)
            return True
        return False
    
    def find(self, collection: str, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Find documents matching a query."""
        results = list(self.collections[collection].values())
        
        if query:
            filtered = []
            for doc in results:
                match = True
                for key, value in query.items():
                    if key not in doc or doc[key] != value:
                        match = False
                        break
                if match:
                    filtered.append(doc)
            return filtered
        
        return results
    
    def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document matching a query."""
        results = self.find(collection, query)
        return results[0] if results else None


# Global database instance
db = DatabaseManager()
