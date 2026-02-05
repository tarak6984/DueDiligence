/**
 * API client for Questionnaire Agent backend
 */

const API_BASE_URL = 'http://localhost:8000';

export interface Project {
  id: string;
  name: string;
  questionnaire_id: string;
  document_scope: 'ALL_DOCS' | 'SELECTED_DOCS';
  selected_document_ids?: string[];
  status: 'CREATING' | 'READY' | 'GENERATING' | 'OUTDATED' | 'ERROR';
  created_at: string;
  updated_at: string;
  total_questions: number;
  answered_questions: number;
  error_message?: string;
}

export interface Document {
  id: string;
  name: string;
  file_type: string;
  file_size: number;
  file_path: string;
  indexing_status: 'PENDING' | 'INDEXING' | 'INDEXED' | 'FAILED';
  is_questionnaire: boolean;
  uploaded_at: string;
  indexed_at?: string;
  error_message?: string;
}

export interface Question {
  id: string;
  project_id: string;
  section_id: string;
  text: string;
  order: number;
  context?: string;
}

export interface Section {
  id: string;
  project_id: string;
  title: string;
  order: number;
  questions: Question[];
}

export interface Reference {
  document_id: string;
  document_name: string;
  chunk_id: string;
  page_number?: number;
  bounding_box?: any;
  text: string;
}

export interface Citation {
  text: string;
  references: Reference[];
}

export interface Answer {
  id: string;
  question_id: string;
  project_id: string;
  status: 'PENDING' | 'GENERATED' | 'CONFIRMED' | 'REJECTED' | 'MANUAL_UPDATED' | 'MISSING_DATA';
  is_answerable: boolean;
  ai_answer?: string;
  citations: Citation[];
  confidence_score?: number;
  manual_answer?: string;
  review_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface AsyncRequest {
  id: string;
  request_type: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
  progress: number;
  result?: any;
  error_message?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface EvaluationResult {
  id: string;
  question_id: string;
  project_id: string;
  ai_answer: string;
  human_answer: string;
  similarity_score: number;
  semantic_similarity: number;
  keyword_overlap: number;
  explanation: string;
  created_at: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Projects
  async listProjects(): Promise<{ projects: Project[]; total: number }> {
    const response = await fetch(`${this.baseUrl}/projects/list`);
    return response.json();
  }

  async getProjectInfo(projectId: string): Promise<{ project: Project; sections: Section[] }> {
    const response = await fetch(`${this.baseUrl}/projects/get-project-info/${projectId}`);
    return response.json();
  }

  async getProjectStatus(projectId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/projects/get-project-status/${projectId}`);
    return response.json();
  }

  async createProject(data: {
    name: string;
    questionnaire_id: string;
    document_scope: 'ALL_DOCS' | 'SELECTED_DOCS';
    selected_document_ids?: string[];
  }): Promise<{ request_id: string }> {
    const response = await fetch(`${this.baseUrl}/projects/create-project-async`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  }

  async updateProject(projectId: string, data: {
    document_scope?: 'ALL_DOCS' | 'SELECTED_DOCS';
    selected_document_ids?: string[];
  }): Promise<{ request_id: string }> {
    const response = await fetch(`${this.baseUrl}/projects/update-project-async/${projectId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  }

  // Answers
  async generateSingleAnswer(questionId: string): Promise<Answer> {
    const response = await fetch(`${this.baseUrl}/answers/generate-single-answer/${questionId}`, {
      method: 'POST',
    });
    return response.json();
  }

  async generateAllAnswers(projectId: string): Promise<{ request_id: string }> {
    const response = await fetch(`${this.baseUrl}/answers/generate-all-answers/${projectId}`, {
      method: 'POST',
    });
    return response.json();
  }

  async updateAnswer(answerId: string, data: {
    status?: string;
    manual_answer?: string;
    review_notes?: string;
  }): Promise<Answer> {
    const response = await fetch(`${this.baseUrl}/answers/update-answer/${answerId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  }

  async getAnswer(answerId: string): Promise<Answer> {
    const response = await fetch(`${this.baseUrl}/answers/get-answer/${answerId}`);
    return response.json();
  }

  async listAnswers(projectId: string): Promise<{ answers: Answer[]; total: number }> {
    const response = await fetch(`${this.baseUrl}/answers/list/${projectId}`);
    return response.json();
  }

  // Documents
  async listDocuments(isQuestionnaire?: boolean): Promise<{ documents: Document[]; total: number }> {
    const url = isQuestionnaire !== undefined
      ? `${this.baseUrl}/documents/list?is_questionnaire=${isQuestionnaire}`
      : `${this.baseUrl}/documents/list`;
    const response = await fetch(url);
    return response.json();
  }

  async getDocument(documentId: string): Promise<Document> {
    const response = await fetch(`${this.baseUrl}/documents/get-document/${documentId}`);
    return response.json();
  }

  async uploadDocument(file: File, isQuestionnaire: boolean = false): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(
      `${this.baseUrl}/documents/upload?is_questionnaire=${isQuestionnaire}`,
      {
        method: 'POST',
        body: formData,
      }
    );
    return response.json();
  }

  async indexDocument(documentId: string): Promise<{ request_id: string }> {
    const response = await fetch(`${this.baseUrl}/documents/index-document-async/${documentId}`, {
      method: 'POST',
    });
    return response.json();
  }

  async deleteDocument(documentId: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/documents/delete/${documentId}`, {
      method: 'DELETE',
    });
    return response.json();
  }

  // Requests
  async getRequestStatus(requestId: string): Promise<AsyncRequest> {
    const response = await fetch(`${this.baseUrl}/requests/get-request-status/${requestId}`);
    return response.json();
  }

  // Evaluation
  async evaluateAnswer(questionId: string, humanAnswer: string): Promise<EvaluationResult> {
    const response = await fetch(`${this.baseUrl}/evaluation/evaluate-answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question_id: questionId, human_answer: humanAnswer }),
    });
    return response.json();
  }

  async evaluateProject(projectId: string, humanAnswers: Record<string, string>): Promise<{
    results: EvaluationResult[];
    total: number;
  }> {
    const response = await fetch(`${this.baseUrl}/evaluation/evaluate-project/${projectId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ human_answers: humanAnswers }),
    });
    return response.json();
  }

  async getEvaluationReport(projectId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/evaluation/get-report/${projectId}`);
    return response.json();
  }
}

export const api = new ApiClient();
