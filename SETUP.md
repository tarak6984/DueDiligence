# Questionnaire Agent - Setup & Running Guide

## Prerequisites

- **Python**: 3.8 or higher
- **Node.js**: 16.x or higher
- **npm**: 8.x or higher
- **Git**: For version control

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/tarak6984/DueDiligence.git
cd DueDiligence

# Checkout the feature branch
git checkout feature/questionnaire-agent-implementation
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run automated test to verify setup
python test_system.py

# Start the backend server
uvicorn app:app --reload
```

Backend will be available at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

### 3. Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the development server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

### 4. Access the Application

Open your browser and navigate to **http://localhost:5173**

---

## First Time Usage

### Step 1: Upload and Index Documents

1. Click on **"Documents"** in the navigation
2. Upload reference documents:
   - Click **"Upload Reference Document"**
   - Select files from `data/` directory (exclude the questionnaire)
   - Click "Index Now" for each uploaded document
   - Wait for status to change to **INDEXED**

3. Upload questionnaire:
   - Click **"Upload Questionnaire"**
   - Select `data/ILPA_Due_Diligence_Questionnaire_v1.2.pdf`
   - Click "Index Now"
   - Wait for status to change to **INDEXED**

### Step 2: Create a Project

1. Click on **"Projects"** in the navigation
2. Click **"+ Create New Project"**
3. Fill in the form:
   - **Project Name**: "Q1 2026 Due Diligence"
   - **Questionnaire**: Select the ILPA questionnaire
   - **Document Scope**: Choose "All Documents"
4. Click **"Create Project"**
5. Wait a few seconds, then refresh the page
6. Your project should appear in the list with status **READY**

### Step 3: Generate Answers

1. Click on your project to open it
2. Click **"Generate All Answers"**
3. Wait for generation to complete (a few seconds)
4. Refresh the page to see generated answers
5. Review answers, citations, and confidence scores

### Step 4: Review and Edit Answers

1. Browse through sections and questions
2. Review AI-generated answers
3. Check citations and confidence scores
4. Manually edit answers if needed (future feature)

---

## Project Structure

```
DueDiligence/
├── backend/
│   ├── app.py                 # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   ├── test_system.py        # Automated test script
│   └── src/
│       ├── api/              # API endpoints
│       ├── models/           # Data models
│       ├── services/         # Business logic
│       ├── indexing/         # Document processing
│       ├── storage/          # Data persistence
│       ├── workers/          # Async processing
│       └── utils/            # Utilities
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API client
│   │   ├── App.tsx          # Main app component
│   │   └── main.tsx         # Entry point
│   ├── package.json         # Node dependencies
│   └── vite.config.ts       # Vite configuration
├── data/                     # Sample PDFs for testing
├── docs/                     # Documentation
│   ├── ARCHITECTURE.md
│   ├── FUNCTIONAL_DESIGN.md
│   ├── TESTING.md
│   └── QUESTIONNAIRE_AGENT_TASKS.md
└── README.md
```

---

## Running Tests

### Automated Backend Test

```bash
cd backend
python test_system.py
```

This test will:
- Register and index all sample documents
- Create a test project
- Generate answers for all questions
- Verify OUTDATED status behavior
- Test manual answer updates
- Run evaluation

### Manual Testing

Follow the test scenarios in `docs/TESTING.md`

---

## API Endpoints Overview

### Projects
- `POST /projects/create-project-async` - Create project
- `GET /projects/list` - List all projects
- `GET /projects/get-project-info/{project_id}` - Get project details
- `GET /projects/get-project-status/{project_id}` - Get status
- `POST /projects/update-project-async/{project_id}` - Update project

### Answers
- `POST /answers/generate-single-answer/{question_id}` - Generate one answer
- `POST /answers/generate-all-answers/{project_id}` - Generate all answers
- `POST /answers/update-answer/{answer_id}` - Update answer
- `GET /answers/list/{project_id}` - List answers

### Documents
- `POST /documents/upload` - Upload document
- `POST /documents/index-document-async/{document_id}` - Index document
- `GET /documents/list` - List documents
- `DELETE /documents/delete/{document_id}` - Delete document

### Evaluation
- `POST /evaluation/evaluate-answer` - Evaluate single answer
- `POST /evaluation/evaluate-project/{project_id}` - Evaluate project
- `GET /evaluation/get-report/{project_id}` - Get evaluation report

Full API documentation available at **http://localhost:8000/docs**

---

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`
```bash
cd backend
pip install -r requirements.txt
```

**Problem**: Port 8000 already in use
```bash
# Use a different port
uvicorn app:app --reload --port 8001

# Update frontend API_BASE_URL in src/services/api.ts
```

**Problem**: Database/storage errors
```bash
# Clean storage directories
rm -rf backend/data/db backend/data/vectors backend/data/storage

# Re-run test
python test_system.py
```

### Frontend Issues

**Problem**: `npm: command not found`
```bash
# Install Node.js from https://nodejs.org/
# Then run: npm install
```

**Problem**: Port 5173 already in use
```bash
# Vite will automatically try the next available port
# Check the terminal output for the actual port
```

**Problem**: API connection errors
```bash
# Ensure backend is running on port 8000
# Check browser console for CORS errors
# Verify API_BASE_URL in src/services/api.ts
```

### Common Issues

**Problem**: Documents not indexing
- Check file format (PDF, DOCX, XLSX, PPTX only)
- Ensure file exists in data/ directory
- Check backend logs for parsing errors

**Problem**: No answers generated
- Verify documents are INDEXED (not PENDING)
- Check project document scope
- Review backend logs for errors

**Problem**: Project stuck in CREATING status
- Check backend logs for errors
- Verify questionnaire is properly formatted
- Try re-creating the project

---

## Data Persistence

The demo implementation uses file-based storage:

- **Database**: `backend/data/db/*.json`
- **Vector Store**: `backend/data/vectors/*.json`
- **Object Storage**: `backend/data/storage/*`

To reset the system:
```bash
cd backend
rm -rf data/db data/vectors data/storage
python test_system.py  # Re-initialize with test data
```

---

## Development Workflow

### Making Changes

```bash
# Create a new branch for your changes
git checkout -b feature/my-new-feature

# Make changes
# ...

# Test your changes
cd backend && python test_system.py
cd frontend && npm run build

# Commit changes
git add .
git commit -m "Description of changes"

# Push to repository
git push origin feature/my-new-feature
```

### Code Style

**Backend (Python)**:
- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions

**Frontend (TypeScript)**:
- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks

---

## Production Deployment Considerations

For production deployment, you would need:

1. **Database**: Replace JSON files with PostgreSQL/MongoDB
2. **Vector Store**: Use Pinecone, Weaviate, or Qdrant
3. **Object Storage**: Use S3 or Azure Blob Storage
4. **Authentication**: Implement JWT-based auth
5. **LLM Integration**: Add OpenAI or Anthropic API
6. **Embeddings**: Use sentence-transformers or OpenAI embeddings
7. **Queue System**: Use Celery + Redis for async tasks
8. **Monitoring**: Add logging and error tracking
9. **HTTPS**: Configure SSL certificates
10. **Environment Variables**: Use .env files for configuration

---

## Support

For issues or questions:
1. Check documentation in `docs/` directory
2. Review API documentation at http://localhost:8000/docs
3. Check the test script: `backend/test_system.py`
4. Review GitHub issues (if applicable)

---

## License

[Add your license information here]
