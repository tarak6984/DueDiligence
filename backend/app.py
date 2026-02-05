from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import (
    projects_router,
    answers_router,
    documents_router,
    requests_router,
    evaluation_router,
    chat_router
)

app = FastAPI(
    title="Questionnaire Agent API",
    description="API for automated questionnaire answering with document indexing and citations",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(projects_router)
app.include_router(answers_router)
app.include_router(documents_router)
app.include_router(requests_router)
app.include_router(evaluation_router)
app.include_router(chat_router)


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "service": "questionnaire-agent"}
