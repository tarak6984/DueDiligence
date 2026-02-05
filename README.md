# Questionnaire Agent - Due Diligence Automation

A full-stack AI-powered system for automating due diligence questionnaire responses with document indexing, citation tracking, and answer evaluation.

## 🚀 Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
python test_system.py              # Run automated tests
uvicorn app:app --reload           # Start server (http://localhost:8000)

# Frontend (new terminal)
cd frontend
npm install
npm run dev                        # Start UI (http://localhost:5173)
```

## ✨ Features

- **Multi-Format Document Ingestion**: PDF, DOCX, XLSX, PPTX support
- **Multi-Layer Indexing**: Separate indices for answer retrieval and precise citations
- **Automated Answer Generation**: AI-powered responses with confidence scores
- **Citation Tracking**: Chunk-level references with page numbers
- **Review Workflow**: Approve, reject, or manually edit answers
- **Evaluation Framework**: Compare AI answers against human ground truth
- **Async Processing**: Background tasks with progress tracking
- **Smart Status Management**: Projects auto-marked OUTDATED when documents change

## 📋 System Architecture

```
Frontend (React + TypeScript)
    ↓ REST API
Backend (FastAPI + Python)
    ├── Document Parser (Multi-format)
    ├── Multi-Layer Indexer (Answer + Citation)
    ├── Answer Generator (Citations + Confidence)
    ├── Evaluation Engine (Similarity Metrics)
    └── Storage (DB + Vector Store + Object Storage)
```

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup and running instructions
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and components
- **[docs/FUNCTIONAL_DESIGN.md](docs/FUNCTIONAL_DESIGN.md)** - User flows and API behaviors
- **[docs/TESTING.md](docs/TESTING.md)** - Test plan, QA checklist, and metrics

## 🧪 Testing with Sample Data

The project includes sample PDFs in `data/` directory:
- **ILPA_Due_Diligence_Questionnaire_v1.2.pdf** - Questionnaire template
- **MiniMax financial documents** - Reference documents for answers

Run the automated test:
```bash
cd backend
python test_system.py
```

This validates:
- ✅ Document indexing (multi-layer)
- ✅ Project creation and structure parsing
- ✅ Answer generation with citations
- ✅ OUTDATED status when documents added
- ✅ Manual answer updates
- ✅ Evaluation against ground truth

## 🎯 Key Workflows

### 1. Upload & Index Documents
```
Upload → Parse → Chunk (2 layers) → Index → Mark ALL_DOCS Projects OUTDATED
```

### 2. Create Project
```
Select Questionnaire → Choose Scope (ALL_DOCS/SELECTED_DOCS) → Parse Structure → Create Questions
```

### 3. Generate Answers
```
Search Layer 1 (Answer) → Generate Response → Search Layer 2 (Citations) → Calculate Confidence
```

### 4. Review & Edit
```
Review Answer → Confirm/Reject/Edit → Preserve Original for Comparison
```

### 5. Evaluate
```
Compare AI vs Human → Calculate Similarity → Generate Explanation
```

## 🛠️ Technology Stack

**Backend**
- FastAPI (API framework)
- Pydantic (data validation)
- PyPDF2 (PDF parsing)
- Python 3.8+

**Frontend**
- React 18
- TypeScript
- Vite (build tool)

**Storage (Demo)**
- JSON files (database)
- In-memory vectors (search)
- File system (objects)

## 📊 API Endpoints

- **Projects**: Create, list, update, get status
- **Answers**: Generate single/all, update, list
- **Documents**: Upload, index, list, delete
- **Evaluation**: Evaluate answers, get reports
- **Requests**: Track async operations

API Docs: **http://localhost:8000/docs**

## 🔄 Status Transitions

**Project**: `CREATING → READY → GENERATING → READY → OUTDATED`

**Answer**: `PENDING → GENERATED → CONFIRMED/REJECTED/MANUAL_UPDATED`

**Document**: `PENDING → INDEXING → INDEXED/FAILED`

## 📈 Evaluation Metrics

- **Semantic Similarity**: Word overlap analysis
- **Keyword Overlap**: Important term matching
- **Overall Score**: Weighted combination
- **Confidence**: Based on chunk relevance

## 🚦 Getting Started

1. **Setup**: Follow [SETUP.md](SETUP.md) for detailed instructions
2. **Test**: Run `python test_system.py` to verify installation
3. **Upload**: Add documents via UI or test script
4. **Create**: Make a new project with questionnaire
5. **Generate**: Run answer generation
6. **Review**: Examine answers, citations, and confidence
7. **Evaluate**: Compare against ground truth

## 🔮 Future Enhancements

- LLM Integration (OpenAI/Anthropic)
- Production-grade vector store (Pinecone/Weaviate)
- Real database (PostgreSQL)
- Real-time updates (WebSockets)
- Advanced parsing (layout analysis)
- Authentication & authorization
- Export to PDF/Excel

## 📝 Development

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and test
cd backend && python test_system.py

# Commit and push
git add .
git commit -m "Description"
git push origin feature/my-feature
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

[Add license information]

---

**Built with ❤️ for automating due diligence workflows**
