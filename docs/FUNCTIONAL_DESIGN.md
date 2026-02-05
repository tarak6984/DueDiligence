# Questionnaire Agent - Functional Design

## User Flows

### 1. Document Upload and Indexing

**Actors**: User, System

**Preconditions**: None

**Flow**:
1. User navigates to Documents page
2. User selects file (PDF, DOCX, XLSX, or PPTX)
3. User indicates if file is a questionnaire
4. User clicks upload
5. System saves file to object storage
6. System creates document record with PENDING status
7. User clicks "Index Document"
8. System creates async request
9. System parses document and extracts text
10. System creates answer chunks (Layer 1, ~1000 chars)
11. System creates citation chunks (Layer 2, ~300 chars)
12. System adds chunks to vector indices
13. System updates document status to INDEXED
14. System marks ALL_DOCS projects as OUTDATED
15. User sees updated status in UI

**Postconditions**: Document is indexed and available for answer generation

**Edge Cases**:
- Unsupported file type → Error message
- Parsing failure → Status set to FAILED with error message
- Large files → Progress tracking via async request

---

### 2. Project Creation

**Actors**: User, System

**Preconditions**: At least one questionnaire document is indexed

**Flow**:
1. User clicks "Create New Project"
2. System displays project creation modal
3. System loads available questionnaires (INDEXED status)
4. System loads available reference documents
5. User enters project name
6. User selects questionnaire
7. User chooses document scope:
   - ALL_DOCS: Use all indexed documents
   - SELECTED_DOCS: User selects specific documents
8. User clicks "Create Project"
9. System creates async request
10. System parses questionnaire to extract structure
11. System creates project record with CREATING status
12. System creates sections based on questionnaire structure
13. System creates questions within each section
14. System creates PENDING answers for all questions
15. System updates project status to READY
16. User sees success message with request ID
17. User refreshes to see new project in list

**Postconditions**: Project is created with all questions ready for answer generation

**Edge Cases**:
- Questionnaire parsing fails → Project status ERROR
- Invalid document scope (SELECTED_DOCS with no selections) → Validation error
- Questionnaire not indexed → Not shown in dropdown

---

### 3. Answer Generation

**Actors**: User, System

**Preconditions**: Project exists with status READY

**Flow - Generate All Answers**:
1. User opens project detail page
2. User clicks "Generate All Answers"
3. System creates async request
4. System updates project status to GENERATING
5. For each question:
   a. System retrieves question text
   b. System determines document scope (ALL_DOCS or SELECTED_DOCS)
   c. System searches Layer 1 index for relevant chunks
   d. If no relevant chunks found:
      - Answer marked as MISSING_DATA
      - is_answerable = false
   e. If relevant chunks found:
      - System generates answer text from top chunks
      - System searches Layer 2 index for precise citations
      - System calculates confidence score
      - Answer status set to GENERATED
      - is_answerable = true
6. System updates project status to READY
7. System updates answered_questions count
8. User sees updated project with generated answers

**Flow - Generate Single Answer**:
1. User selects a specific question
2. User clicks "Generate Answer"
3. System follows steps 5a-5e above for that question
4. System returns answer immediately (synchronous)
5. User sees answer displayed with citations

**Postconditions**: Answers are generated with citations and confidence scores

**Edge Cases**:
- No relevant documents → Answer marked MISSING_DATA
- Generation fails for some questions → Failed count tracked
- Project becomes OUTDATED during generation → Generation continues

---

### 4. Answer Review and Manual Override

**Actors**: User (Reviewer), System

**Preconditions**: Answer exists with status GENERATED

**Flow - Approve Answer**:
1. User views answer in project detail
2. User reviews AI answer, citations, and confidence
3. User clicks "Confirm"
4. System updates answer status to CONFIRMED
5. User sees updated status badge

**Flow - Reject Answer**:
1. User views answer and determines it's incorrect
2. User clicks "Reject"
3. System updates answer status to REJECTED
4. User can optionally add review notes
5. System saves notes

**Flow - Manual Edit**:
1. User views AI-generated answer
2. User clicks "Edit Answer"
3. System shows text editor
4. User modifies answer text
5. User optionally adds review notes
6. User clicks "Save"
7. System saves manual_answer field
8. System updates status to MANUAL_UPDATED
9. System preserves original AI answer for comparison
10. User sees both AI and manual answers

**Postconditions**: Answer status reflects review decision, manual overrides preserved

**Edge Cases**:
- Manual answer is empty → Validation error
- Status transitions are idempotent (can confirm multiple times)

---

### 5. Project Update and Regeneration

**Actors**: User, System

**Preconditions**: Project exists

**Flow**:
1. User opens project settings
2. User changes document scope:
   - From ALL_DOCS to SELECTED_DOCS
   - From SELECTED_DOCS to ALL_DOCS
   - Modifies selected document list
3. User clicks "Update Project"
4. System creates async request
5. System updates project configuration
6. System marks project status as OUTDATED
7. User sees "Regenerate Answers" prompt
8. User clicks "Regenerate All Answers"
9. System follows answer generation flow
10. System regenerates all answers with new document scope

**Postconditions**: Project uses new document scope, answers regenerated

**Edge Cases**:
- User doesn't regenerate → Answers remain OUTDATED
- Some answers change, some stay same → All marked as regenerated

---

### 6. Evaluation Against Human Ground Truth

**Actors**: User, System

**Preconditions**: Project has generated or manual answers

**Flow - Single Answer Evaluation**:
1. User selects a question
2. User enters human ground truth answer
3. User clicks "Evaluate"
4. System retrieves AI/manual answer
5. System calculates semantic similarity (word overlap)
6. System calculates keyword overlap (important terms)
7. System computes weighted similarity score
8. System generates qualitative explanation
9. System saves evaluation result
10. User sees similarity metrics and explanation

**Flow - Bulk Evaluation**:
1. User prepares JSON/CSV with question_id → human_answer mapping
2. User uploads evaluation data
3. System evaluates each answer
4. System generates evaluation report
5. User views report with:
   - Average similarity score
   - Distribution (high/medium/low similarity)
   - Per-question breakdown
6. User exports report

**Postconditions**: Evaluation results stored and available for analysis

**Edge Cases**:
- No AI answer exists → Error message
- Human answer is very different → Low similarity score with explanation

---

### 7. Document Addition Impact

**Actors**: User, System

**Preconditions**: Projects exist with ALL_DOCS scope

**Flow**:
1. User uploads and indexes new document
2. During indexing completion:
   a. System queries all projects with ALL_DOCS scope
   b. System filters projects with status READY
   c. System updates each project status to OUTDATED
   d. System saves updated_at timestamp
3. User views project list
4. User sees OUTDATED badge on affected projects
5. User opens outdated project
6. User sees "Document corpus changed - regenerate answers" message
7. User regenerates answers to incorporate new document

**Postconditions**: Projects correctly marked as needing regeneration

**Edge Cases**:
- SELECTED_DOCS projects → Not affected
- Projects already GENERATING → Marked OUTDATED after completion

---

## API Behaviors

### Async Operations

All long-running operations return immediately with a request_id:
```json
{
  "request_id": "req_abc123",
  "status": "pending",
  "message": "Operation initiated"
}
```

Clients poll `/requests/get-request-status/{request_id}` to track progress:
```json
{
  "id": "req_abc123",
  "status": "IN_PROGRESS",
  "progress": 45,
  "result": null
}
```

When complete:
```json
{
  "id": "req_abc123",
  "status": "COMPLETED",
  "progress": 100,
  "result": { "project_id": "proj_xyz", ... }
}
```

### Idempotency

- Answer status updates are idempotent (confirming confirmed answer is OK)
- Document re-indexing deletes old chunks first
- Project updates preserve existing data unless explicitly changed

### Error Handling

All errors return consistent format:
```json
{
  "detail": "Human-readable error message"
}
```

HTTP status codes:
- 200: Success
- 400: Bad request (validation error)
- 404: Resource not found
- 500: Internal server error

---

## Status Transition Rules

### Project Status

| Current Status | Allowed Transitions | Trigger |
|---------------|---------------------|---------|
| CREATING | READY, ERROR | Creation completes/fails |
| READY | GENERATING, OUTDATED | Generate answers / Config change |
| GENERATING | READY, ERROR | Generation completes/fails |
| OUTDATED | GENERATING | User regenerates |
| ERROR | CREATING | User retries |

### Answer Status

| Current Status | Allowed Transitions | Trigger |
|---------------|---------------------|---------|
| PENDING | GENERATED, MISSING_DATA | Answer generation |
| GENERATED | CONFIRMED, REJECTED, MANUAL_UPDATED | Review actions |
| CONFIRMED | MANUAL_UPDATED | User edits |
| REJECTED | MANUAL_UPDATED | User provides answer |
| MANUAL_UPDATED | CONFIRMED | User confirms |

### Document Indexing Status

| Current Status | Allowed Transitions | Trigger |
|---------------|---------------------|---------|
| PENDING | INDEXING | Indexing started |
| INDEXING | INDEXED, FAILED | Indexing completes/fails |
| INDEXED | INDEXING | Re-index requested |
| FAILED | INDEXING | Retry requested |

---

## Edge Cases and Special Scenarios

1. **Empty Document Corpus**: Answer generation returns all MISSING_DATA answers

2. **Malformed Questionnaire**: Parser creates default section structure

3. **Concurrent Operations**: Last write wins, tracked via updated_at timestamps

4. **Large Questionnaires**: Async processing with progress tracking

5. **Document Deletion**: 
   - Removes chunks from indices
   - Projects referencing deleted doc show warning
   - Answers remain but may be invalid

6. **Network Failures**: Frontend retries with exponential backoff

7. **Partial Generation Failure**: Some answers succeed, failed count tracked

8. **Citation Unavailable**: Answer generated without citations, lower confidence
