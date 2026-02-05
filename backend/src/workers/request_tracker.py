"""Request tracking for async operations."""

from typing import Dict, Any, Optional, Callable
from datetime import datetime
import threading
from ..models import AsyncRequest, RequestStatus
from ..storage.database import db
from ..utils import generate_id


class RequestTracker:
    """Track and manage async requests."""
    
    def __init__(self):
        self.db = db
        self.active_requests: Dict[str, threading.Thread] = {}
    
    def create_request(self, request_type: str) -> AsyncRequest:
        """Create a new async request."""
        request_id = generate_id("req")
        
        request_data = {
            "id": request_id,
            "request_type": request_type,
            "status": RequestStatus.PENDING.value,
            "progress": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.db.insert("requests", request_id, request_data)
        
        return AsyncRequest(**request_data)
    
    def update_request(self, request_id: str, status: Optional[RequestStatus] = None,
                      progress: Optional[int] = None, result: Optional[Any] = None,
                      error_message: Optional[str] = None):
        """Update request status and progress."""
        updates = {
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if status:
            updates["status"] = status.value
            
            if status == RequestStatus.COMPLETED:
                updates["completed_at"] = datetime.utcnow().isoformat()
                updates["progress"] = 100
        
        if progress is not None:
            updates["progress"] = progress
        
        if result is not None:
            updates["result"] = result
        
        if error_message:
            updates["error_message"] = error_message
        
        self.db.update("requests", request_id, updates)
    
    def get_request(self, request_id: str) -> Optional[AsyncRequest]:
        """Get request status."""
        request_data = self.db.get("requests", request_id)
        return AsyncRequest(**request_data) if request_data else None
    
    def execute_async(self, request_id: str, task_func: Callable, *args, **kwargs):
        """Execute a task asynchronously."""
        def run_task():
            try:
                self.update_request(request_id, status=RequestStatus.IN_PROGRESS, progress=10)
                
                result = task_func(*args, **kwargs)
                
                self.update_request(request_id, status=RequestStatus.COMPLETED, result=result)
            except Exception as e:
                self.update_request(
                    request_id,
                    status=RequestStatus.FAILED,
                    error_message=str(e)
                )
        
        thread = threading.Thread(target=run_task)
        self.active_requests[request_id] = thread
        thread.start()


# Global request tracker instance
request_tracker = RequestTracker()
