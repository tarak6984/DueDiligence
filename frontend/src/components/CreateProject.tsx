import { useState, useEffect } from 'react';
import { api, Document } from '../services/api';

interface CreateProjectProps {
  onClose: () => void;
  onCreated: () => void;
}

export default function CreateProject({ onClose, onCreated }: CreateProjectProps) {
  const [name, setName] = useState('');
  const [questionnaireId, setQuestionnaireId] = useState('');
  const [documentScope, setDocumentScope] = useState<'ALL_DOCS' | 'SELECTED_DOCS'>('ALL_DOCS');
  const [selectedDocs, setSelectedDocs] = useState<string[]>([]);
  const [questionnaires, setQuestionnaires] = useState<Document[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [questData, docData] = await Promise.all([
        api.listDocuments(true),
        api.listDocuments(false),
      ]);
      setQuestionnaires(questData.documents.filter(d => d.indexing_status === 'INDEXED'));
      setDocuments(docData.documents.filter(d => d.indexing_status === 'INDEXED'));
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);

    try {
      const result = await api.createProject({
        name,
        questionnaire_id: questionnaireId,
        document_scope: documentScope,
        selected_document_ids: documentScope === 'SELECTED_DOCS' ? selectedDocs : undefined,
      });
      alert(`Project creation started. Request ID: ${result.request_id}`);
      onCreated();
    } catch (error) {
      console.error('Failed to create project:', error);
      alert('Failed to create project');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    }}>
      <div style={{
        backgroundColor: '#fff',
        borderRadius: '8px',
        padding: '30px',
        maxWidth: '600px',
        width: '90%',
        maxHeight: '90vh',
        overflow: 'auto',
      }}>
        <h2>Create New Project</h2>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Project Name *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ddd',
                borderRadius: '4px',
              }}
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Questionnaire *
            </label>
            <select
              value={questionnaireId}
              onChange={(e) => setQuestionnaireId(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ddd',
                borderRadius: '4px',
              }}
            >
              <option value="">Select a questionnaire</option>
              {questionnaires.map(q => (
                <option key={q.id} value={q.id}>{q.name}</option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Document Scope *
            </label>
            <div>
              <label style={{ marginRight: '20px' }}>
                <input
                  type="radio"
                  value="ALL_DOCS"
                  checked={documentScope === 'ALL_DOCS'}
                  onChange={(e) => setDocumentScope(e.target.value as 'ALL_DOCS')}
                />
                {' '}All Documents
              </label>
              <label>
                <input
                  type="radio"
                  value="SELECTED_DOCS"
                  checked={documentScope === 'SELECTED_DOCS'}
                  onChange={(e) => setDocumentScope(e.target.value as 'SELECTED_DOCS')}
                />
                {' '}Selected Documents
              </label>
            </div>
          </div>

          {documentScope === 'SELECTED_DOCS' && (
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                Select Documents *
              </label>
              <div style={{
                border: '1px solid #ddd',
                borderRadius: '4px',
                padding: '10px',
                maxHeight: '200px',
                overflow: 'auto',
              }}>
                {documents.map(doc => (
                  <label key={doc.id} style={{ display: 'block', marginBottom: '5px' }}>
                    <input
                      type="checkbox"
                      checked={selectedDocs.includes(doc.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedDocs([...selectedDocs, doc.id]);
                        } else {
                          setSelectedDocs(selectedDocs.filter(id => id !== doc.id));
                        }
                      }}
                    />
                    {' '}{doc.name}
                  </label>
                ))}
              </div>
            </div>
          )}

          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: '10px 20px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                backgroundColor: '#fff',
                cursor: 'pointer',
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={creating}
              style={{
                padding: '10px 20px',
                border: 'none',
                borderRadius: '4px',
                backgroundColor: '#2196f3',
                color: '#fff',
                cursor: creating ? 'not-allowed' : 'pointer',
              }}
            >
              {creating ? 'Creating...' : 'Create Project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
