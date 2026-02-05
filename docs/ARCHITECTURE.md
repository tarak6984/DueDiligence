# Questionnaire Agent - Architecture Design

## System Overview

The Questionnaire Agent is a full-stack application that automates the process of answering due diligence questionnaires using indexed document corpus with AI-powered answer generation, citation tracking, and evaluation capabilities.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Frontend (React)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │Project List  │  │Project Detail│  │Document Mgmt │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
┌────────────────────────────┴────────────────────────────────────┐
│                       Backend (FastAPI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │API Endpoints │  │  Services    │  │   Workers    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│  ┌──────┴──────────────────┴──────────────────┴───────┐         │
│  │              Storage Layer                          │         │
│  │  • Database (JSON files)                            │         │
│  │  • Vector Store (Multi-layer index)                 │         │
│  │  • Object Storage (Files)                           │         │
│  └─────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Component Boundaries

### Frontend Components

1. **Project Management**
   - ProjectList: Display all projects with status
   - CreateProject: Modal for creating new projects
   - ProjectDetail: Show sections, questions, and answers

2. **Document Management**
   - DocumentManager: Upload, index, and manage documents

3. **API Client**
   - Centralized API service for backend communication

### Backend Components

1. **API Layer** (`src/api/`)
   - RESTful endpoints for all operations
   - Request validation with Pydantic
   - Async request handling

2. **Service Layer** (`src/services/`)
   - ProjectService: Project lifecycle management
   - AnswerService: Answer generation and updates
   - DocumentService: Document operations
   - EvaluationService: AI vs human comparison

3. **Indexing Layer** (`src/indexing/`)
   - DocumentParser: Multi-format parsing (PDF, DOCX, XLSX, PPTX)
   - ChunkingStrategy: Two-layer chunking
   - DocumentIndexer: Orchestrates indexing pipeline

4. **Storage Layer** (`src/storage/`)
   - DatabaseManager: Structured data (JSON-based)
   - VectorStore: Two-layer semantic index
   - ObjectStorage: File management

5. **Workers** (`src/workers/`)
   - RequestTracker: Async task management and status tracking

## Data Flow

### Document Indexing Flow
```
1. Upload → 2. Parse → 3. Chunk (2 layers) → 4. Index → 5. Mark ALL_DOCS OUTDATED
```

### Project Creation Flow
```
1. Create Project → 2. Parse Questionnaire → 3. Create Sections/Questions → 4. Create Pending Answers
```

### Answer Generation Flow
```
1. Query Question → 2. Search Layer 1 (Answers) → 3. Generate Response → 
4. Search Layer 2 (Citations) → 5. Calculate Confidence → 6. Save Answer
```

### Evaluation Flow
```
1. Get AI Answer → 2. Compare with Human Answer → 3. Calculate Metrics → 4. Generate Explanation
```

## Multi-Layer Indexing

### Layer 1: Answer Retrieval
- **Purpose**: Find relevant sections for answering questions
- **Chunk Size**: ~1000 characters with 100 char overlap
- **Strategy**: Semantic retrieval based on question text
- **Storage**: Answer index with embeddings (simulated)

### Layer 2: Citation Chunks
- **Purpose**: Provide precise citations with page numbers
- **Chunk Size**: ~300 characters with 30 char overlap
- **Strategy**: Smaller chunks for accurate reference tracking
- **Storage**: Citation index with bounding box metadata

## Storage Design

### Database Schema
```
projects/
  - id, name, questionnaire_id, document_scope, status, ...

documents/
  - id, name, file_type, indexing_status, is_questionnaire, ...

sections/
  - id, project_id, title, order

questions/
  - id, project_id, section_id, text, order

answers/
  - id, question_id, status, is_answerable, ai_answer, 
    citations, confidence_score, manual_answer, ...

requests/
  - id, request_type, status, progress, result, error_message

evaluations/
  - id, question_id, ai_answer, human_answer, similarity_score, ...
```

### Vector Store Structure
```
answer_index/
  chunk_id → {document_id, text, embedding, metadata}

citation_index/
  chunk_id → {document_id, text, embedding, page_number, bounding_box}
```

## Status Transitions

### Project Status
- CREATING → READY (initial creation)
- READY → GENERATING (answer generation started)
- GENERATING → READY (answer generation completed)
- READY → OUTDATED (document scope changed or new ALL_DOCS document added)
- * → ERROR (any failure)

### Answer Status
- PENDING → GENERATED (AI answer created)
- GENERATED → CONFIRMED (reviewer approved)
- GENERATED → REJECTED (reviewer rejected)
- GENERATED → MANUAL_UPDATED (manual edit applied)
- * → MISSING_DATA (no relevant documents found)

### Document Indexing Status
- PENDING → INDEXING → INDEXED (success path)
- PENDING → INDEXING → FAILED (failure path)

## API Endpoints

### Projects
- POST `/projects/create-project-async` - Create new project
- GET `/projects/get-project-info/{project_id}` - Get project details
- GET `/projects/get-project-status/{project_id}` - Get status
- POST `/projects/update-project-async/{project_id}` - Update configuration
- GET `/projects/list` - List all projects

### Answers
- POST `/answers/generate-single-answer/{question_id}` - Generate one answer
- POST `/answers/generate-all-answers/{project_id}` - Generate all answers
- POST `/answers/update-answer/{answer_id}` - Update answer
- GET `/answers/get-answer/{answer_id}` - Get answer
- GET `/answers/list/{project_id}` - List project answers

### Documents
- POST `/documents/upload` - Upload document
- POST `/documents/index-document-async/{document_id}` - Index document
- GET `/documents/get-document/{document_id}` - Get document
- GET `/documents/list` - List documents
- DELETE `/documents/delete/{document_id}` - Delete document

### Requests
- GET `/requests/get-request-status/{request_id}` - Get async request status

### Evaluation
- POST `/evaluation/evaluate-answer` - Evaluate single answer
- POST `/evaluation/evaluate-project/{project_id}` - Evaluate project
- GET `/evaluation/get-report/{project_id}` - Get evaluation report

## Technology Stack

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.8+
- **Parsing**: PyPDF2 (PDF support)
- **Validation**: Pydantic
- **Server**: Uvicorn

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite
- **Styling**: Inline styles (demo)

### Storage (Demo Implementation)
- **Database**: JSON files
- **Vector Store**: In-memory with JSON persistence
- **Object Storage**: File system

## Scalability Considerations

For production deployment:

1. **Database**: Replace JSON files with PostgreSQL or MongoDB
2. **Vector Store**: Use Pinecone, Weaviate, or Qdrant
3. **Object Storage**: Use S3 or Azure Blob Storage
4. **Async Processing**: Use Celery with Redis/RabbitMQ
5. **Caching**: Add Redis for frequently accessed data
6. **LLM Integration**: Add OpenAI, Anthropic, or local models for answer generation
7. **Authentication**: Add JWT-based auth and user management

## Error Handling

- All API endpoints return appropriate HTTP status codes
- Async operations tracked via RequestTracker
- Failed operations update status with error messages
- Frontend displays user-friendly error messages
