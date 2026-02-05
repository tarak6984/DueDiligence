"""API route handlers."""

from .projects import router as projects_router
from .answers import router as answers_router
from .documents import router as documents_router
from .requests import router as requests_router
from .evaluation import router as evaluation_router
from .chat import router as chat_router

__all__ = [
    "projects_router",
    "answers_router", 
    "documents_router",
    "requests_router",
    "evaluation_router",
    "chat_router"
]
