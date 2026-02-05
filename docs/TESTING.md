# Questionnaire Agent - Testing & Evaluation Guide

## Testing Plan

### 1. Dataset Testing

The `data/` directory contains sample PDFs for comprehensive testing:

#### Test Documents
- **ILPA_Due_Diligence_Questionnaire_v1.2.pdf** - Questionnaire input
- **20260110_MiniMax_Accountants_Report.pdf** - Financial reference
- **20260110_MiniMax_Audited_Consolidated_Financial_Statements.pdf** - Financial data
- **20260110_MiniMax_Global_Offering_Prospectus.pdf** - Company overview
- **20260110_MiniMax_Industry_Report.pdf** - Market context

#### Test Scenarios

**Scenario 1: Basic Workflow**
```bash
# Run automated test
cd backend
python test_system.py
```

Expected Results:
- All documents successfully indexed
- Project created with 15 questions (5 sections × 3 questions)
- Answers generated with citations and confidence scores
- Project marked OUTDATED when new document added

**Scenario 2: Document Scope Testing**
1. Create project with ALL_DOCS scope
2. Generate answers - verify all documents used
3. Create project with SELECTED_DOCS (2 documents)
4. Generate answers - verify only selected documents used
5. Compare answer quality between scopes

**Scenario 3: OUTDATED Status Validation**
1. Create project with ALL_DOCS scope
2. Verify status = READY
3. Upload and index new document
4. Verify project status = OUTDATED
5. Create project with SELECTED_DOCS
6. Upload new document
7. Verify SELECTED_DOCS project unchanged

**Scenario 4: Review Workflow**
1. Generate answers for project
2. Mark answer as CONFIRMED
3. Mark answer as REJECTED
4. Edit answer manually (MANUAL_UPDATED)
5. Verify status transitions correct
6. Verify original AI answer preserved

**Scenario 5: Evaluation**
1. Generate AI answers
2. Provide human ground truth answers
3. Run evaluation
4. Verify similarity scores calculated
5. Check evaluation report metrics

---

## QA Checklist

### Document Management
- [ ] Upload PDF document
- [ ] Upload DOCX document (if supported)
- [ ] Upload questionnaire document
- [ ] Document shows PENDING status
- [ ] Index document successfully
- [ ] Document shows INDEXED status
- [ ] Index failure shows error message
- [ ] List all documents correctly
- [ ] Filter documents by type (questionnaire/reference)

### Project Management
- [ ] Create project with ALL_DOCS scope
- [ ] Create project with SELECTED_DOCS scope
- [ ] Project list shows all projects
- [ ] Project status displayed correctly
- [ ] Progress bar shows answered/total questions
- [ ] Open project detail view
- [ ] Sections displayed in order
- [ ] Questions displayed in order per section
- [ ] Update project document scope
- [ ] Project marked OUTDATED after config change

### Answer Generation
- [ ] Generate all answers for project
- [ ] Generate single answer for question
- [ ] Answers display with correct status
- [ ] Confidence scores shown (0-100%)
- [ ] Citations included with references
- [ ] MISSING_DATA status for unanswerable questions
- [ ] Answer generation completes within reasonable time
- [ ] Async request tracking works
- [ ] Answered questions count updates

### Answer Review
- [ ] View generated answer
- [ ] Confirm answer (status → CONFIRMED)
- [ ] Reject answer (status → REJECTED)
- [ ] Edit answer manually (status → MANUAL_UPDATED)
- [ ] Add review notes
- [ ] Original AI answer preserved after manual edit
- [ ] View citations for answer
- [ ] Citations show document name, page number

### Evaluation
- [ ] Evaluate single answer
- [ ] Similarity score calculated (0-1)
- [ ] Semantic similarity shown
- [ ] Keyword overlap shown
- [ ] Explanation generated
- [ ] Evaluate multiple answers in project
- [ ] View evaluation report
- [ ] Report shows average scores
- [ ] Report shows distribution (high/medium/low)

### Status Transitions
- [ ] Project: CREATING → READY
- [ ] Project: READY → GENERATING → READY
- [ ] Project: READY → OUTDATED (on new doc)
- [ ] Answer: PENDING → GENERATED
- [ ] Answer: GENERATED → CONFIRMED
- [ ] Answer: GENERATED → REJECTED
- [ ] Answer: GENERATED → MANUAL_UPDATED
- [ ] Document: PENDING → INDEXING → INDEXED
- [ ] Document: INDEXING → FAILED (on error)

### Edge Cases
- [ ] Upload unsupported file type (error shown)
- [ ] Create project without questionnaire (validation error)
- [ ] Create SELECTED_DOCS project with no selections (error)
- [ ] Generate answers with no documents indexed (MISSING_DATA)
- [ ] Generate answers for OUTDATED project
- [ ] Add document while project is GENERATING
- [ ] Delete document referenced by project (warning shown)
- [ ] Network error handling (retry mechanism)
- [ ] Large file upload (progress indication)
- [ ] Large questionnaire (pagination/loading)

### UI/UX
- [ ] Navigation between pages works
- [ ] Create project modal opens/closes
- [ ] Form validation messages shown
- [ ] Loading states displayed
- [ ] Success messages shown
- [ ] Error messages user-friendly
- [ ] Status badges color-coded
- [ ] Responsive layout (desktop)
- [ ] Buttons disabled during operations
- [ ] Data refreshes after operations

---

## Evaluation Metrics

### Answer Quality Metrics

1. **Answerability Rate**
   - Formula: (Questions with is_answerable=true) / Total Questions
   - Target: > 80%

2. **Average Confidence Score**
   - Formula: Average of all confidence_score values
   - Target: > 0.7 (70%)

3. **Citation Coverage**
   - Formula: (Answers with citations) / Total Answerable
   - Target: > 90%

4. **Manual Override Rate**
   - Formula: (MANUAL_UPDATED answers) / Total Answers
   - Target: < 30% (lower is better)

### Evaluation Metrics

1. **Semantic Similarity**
   - Word overlap between AI and human answers
   - Target: > 0.6 (60%)

2. **Keyword Overlap**
   - Important term matching
   - Target: > 0.5 (50%)

3. **Overall Similarity**
   - Weighted combination (60% semantic + 40% keyword)
   - Target: > 0.65 (65%)

### Performance Metrics

1. **Indexing Time**
   - Time to index single document
   - Target: < 30 seconds per document

2. **Answer Generation Time**
   - Time per question
   - Target: < 2 seconds per question

3. **Project Creation Time**
   - Parse questionnaire and create structure
   - Target: < 10 seconds

### System Metrics

1. **Status Accuracy**
   - Projects correctly marked OUTDATED
   - Target: 100%

2. **Citation Accuracy**
   - Citations reference correct documents
   - Target: > 95%

3. **Error Recovery**
   - Failed operations properly logged
   - Target: 100% error tracking

---

## Test Execution

### Automated Testing

```bash
# Backend tests
cd backend
python test_system.py

# Expected output:
# - All documents registered and indexed
# - Project created successfully
# - Answers generated with citations
# - OUTDATED status validation passed
# - Manual updates applied
# - Evaluation completed
```

### Manual Testing

1. **Start Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
# Access API docs: http://localhost:8000/docs
```

2. **Start Frontend**
```bash
cd frontend
npm install
npm run dev
# Access UI: http://localhost:5173
```

3. **Execute Test Scenarios**
- Follow scenarios listed above
- Check off QA checklist items
- Record any issues found

### API Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# List documents
curl http://localhost:8000/documents/list

# Get project status
curl http://localhost:8000/projects/get-project-status/{project_id}

# Generate answer
curl -X POST http://localhost:8000/answers/generate-single-answer/{question_id}
```

---

## Known Limitations (Demo Implementation)

1. **Vector Search**: Uses simple keyword matching instead of embeddings
2. **Answer Generation**: Concatenates chunks instead of using LLM
3. **Storage**: JSON files instead of database
4. **Authentication**: Not implemented
5. **File Parsing**: Basic PDF parsing, limited format support
6. **Concurrency**: Single-threaded async processing
7. **Caching**: No caching layer

## Future Enhancements

1. **LLM Integration**: Add OpenAI/Anthropic for answer generation
2. **Embeddings**: Use sentence-transformers for semantic search
3. **Database**: Migrate to PostgreSQL + Pinecone
4. **Real-time Updates**: WebSocket support for live progress
5. **Advanced Parsing**: Better extraction with layout analysis
6. **Batch Operations**: Parallel processing for large questionnaires
7. **Export**: PDF/Excel export of answers and reports
8. **Audit Trail**: Track all changes and user actions

---

## Issue Reporting Template

When reporting issues during testing:

```
**Title**: Brief description

**Environment**:
- OS: [Windows/Mac/Linux]
- Python version:
- Node version:
- Browser (if frontend):

**Steps to Reproduce**:
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**:
What should happen

**Actual Behavior**:
What actually happened

**Screenshots/Logs**:
[Attach if applicable]

**Priority**: [High/Medium/Low]
```

---

## Test Results Template

```
**Test Date**: YYYY-MM-DD
**Tester**: Name
**Environment**: Development/Staging/Production

**Scenarios Passed**: X / Y
**QA Checklist**: X / Y items passed

**Issues Found**:
1. Issue 1 - [Priority]
2. Issue 2 - [Priority]

**Metrics**:
- Answerability Rate: X%
- Average Confidence: X%
- Citation Coverage: X%
- Average Similarity: X%

**Notes**:
Additional observations
```
