import { useState, useEffect } from 'react';
import { api, Document } from '../services/api';
import { useToast } from './ToastContainer';

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
  const [loading, setLoading] = useState(true);
  const toast = useToast();

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
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (documentScope === 'SELECTED_DOCS' && selectedDocs.length === 0) {
      toast.warning('Please select at least one document');
      return;
    }

    setCreating(true);

    try {
      const result = await api.createProject({
        name,
        questionnaire_id: questionnaireId,
        document_scope: documentScope,
        selected_document_ids: documentScope === 'SELECTED_DOCS' ? selectedDocs : undefined,
      });
      toast.success(`Project creation started. Request ID: ${result.request_id}`);
      onCreated();
    } catch (error) {
      console.error('Failed to create project:', error);
      toast.error('Failed to create project');
    } finally {
      setCreating(false);
    }
  };

  const toggleDocument = (docId: string) => {
    if (selectedDocs.includes(docId)) {
      setSelectedDocs(selectedDocs.filter(id => id !== docId));
    } else {
      setSelectedDocs([...selectedDocs, docId]);
    }
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div 
      onClick={handleBackdropClick}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.6)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '20px',
        animation: 'fadeIn 0.2s ease-in-out',
      }}
    >
      <div style={{
        backgroundColor: 'white',
        borderRadius: 'var(--radius-xl)',
        padding: '0',
        maxWidth: '650px',
        width: '100%',
        maxHeight: '90vh',
        overflow: 'hidden',
        boxShadow: 'var(--shadow-xl)',
        animation: 'fadeIn 0.3s ease-in-out',
      }}>
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, var(--primary-700), var(--primary-900))',
          padding: '24px 32px',
          borderBottom: '1px solid var(--gray-200)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h2 style={{ 
                margin: 0,
                fontSize: '24px', 
                fontWeight: 700,
                color: 'white',
                marginBottom: '4px',
              }}>
                🚀 Create New Project
              </h2>
              <p style={{ margin: 0, fontSize: '14px', color: 'rgba(255, 255, 255, 0.8)' }}>
                Set up a new questionnaire project
              </p>
            </div>
            <button
              onClick={onClose}
              style={{
                width: '36px',
                height: '36px',
                borderRadius: 'var(--radius-full)',
                background: 'rgba(255, 255, 255, 0.2)',
                border: 'none',
                color: 'white',
                fontSize: '20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                transition: 'all var(--transition-base)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
              }}
            >
              ✕
            </button>
          </div>
        </div>

        {/* Content */}
        <div style={{ padding: '32px', maxHeight: 'calc(90vh - 150px)', overflow: 'auto' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <div style={{ 
                fontSize: '48px', 
                marginBottom: '16px',
                animation: 'pulse 2s ease-in-out infinite',
              }}>
                ⚙
              </div>
              <p style={{ color: 'var(--gray-600)', fontSize: '16px', fontWeight: 500 }}>
                Loading project options...
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              {/* Project Name */}
              <div style={{ marginBottom: '24px' }}>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '8px', 
                  fontWeight: 600,
                  fontSize: '14px',
                  color: 'var(--gray-700)',
                }}>
                  📝 Project Name <span style={{ color: 'var(--error-main)' }}>*</span>
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  placeholder="e.g., Q1 2026 Due Diligence Review"
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    border: '2px solid var(--gray-300)',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '15px',
                    fontWeight: 500,
                  }}
                />
              </div>

              {/* Questionnaire Selection */}
              <div style={{ marginBottom: '24px' }}>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '8px', 
                  fontWeight: 600,
                  fontSize: '14px',
                  color: 'var(--gray-700)',
                }}>
                  📋 Questionnaire <span style={{ color: 'var(--error-main)' }}>*</span>
                </label>
                {questionnaires.length === 0 ? (
                  <div style={{
                    padding: '16px',
                    background: 'var(--warning-light)',
                    border: '1px solid var(--warning-main)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--gray-700)',
                    fontSize: '14px',
                  }}>
                    ⚠️ No indexed questionnaires available. Please upload and index a questionnaire first.
                  </div>
                ) : (
                  <select
                    value={questionnaireId}
                    onChange={(e) => setQuestionnaireId(e.target.value)}
                    required
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid var(--gray-300)',
                      borderRadius: 'var(--radius-md)',
                      fontSize: '15px',
                      fontWeight: 500,
                      cursor: 'pointer',
                    }}
                  >
                    <option value="">Select a questionnaire...</option>
                    {questionnaires.map(q => (
                      <option key={q.id} value={q.id}>{q.name}</option>
                    ))}
                  </select>
                )}
              </div>

              {/* Document Scope */}
              <div style={{ marginBottom: '24px' }}>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '12px', 
                  fontWeight: 600,
                  fontSize: '14px',
                  color: 'var(--gray-700)',
                }}>
                  📁 Document Scope <span style={{ color: 'var(--error-main)' }}>*</span>
                </label>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <label style={{ 
                    flex: 1,
                    padding: '16px',
                    border: documentScope === 'ALL_DOCS' 
                      ? '2px solid var(--primary-600)' 
                      : '2px solid var(--gray-300)',
                    borderRadius: 'var(--radius-md)',
                    cursor: 'pointer',
                    transition: 'all var(--transition-base)',
                    background: documentScope === 'ALL_DOCS' 
                      ? 'var(--primary-50)' 
                      : 'white',
                  }}>
                    <input
                      type="radio"
                      value="ALL_DOCS"
                      checked={documentScope === 'ALL_DOCS'}
                      onChange={(e) => setDocumentScope(e.target.value as 'ALL_DOCS')}
                      style={{ marginRight: '8px' }}
                    />
                    <span style={{ 
                      fontWeight: 600,
                      color: documentScope === 'ALL_DOCS' 
                        ? 'var(--primary-700)' 
                        : 'var(--gray-700)',
                    }}>
                      All Documents
                    </span>
                    <div style={{ 
                      fontSize: '12px', 
                      color: 'var(--gray-600)',
                      marginTop: '4px',
                      marginLeft: '24px',
                    }}>
                      Use all indexed documents
                    </div>
                  </label>
                  <label style={{ 
                    flex: 1,
                    padding: '16px',
                    border: documentScope === 'SELECTED_DOCS' 
                      ? '2px solid var(--primary-600)' 
                      : '2px solid var(--gray-300)',
                    borderRadius: 'var(--radius-md)',
                    cursor: 'pointer',
                    transition: 'all var(--transition-base)',
                    background: documentScope === 'SELECTED_DOCS' 
                      ? 'var(--primary-50)' 
                      : 'white',
                  }}>
                    <input
                      type="radio"
                      value="SELECTED_DOCS"
                      checked={documentScope === 'SELECTED_DOCS'}
                      onChange={(e) => setDocumentScope(e.target.value as 'SELECTED_DOCS')}
                      style={{ marginRight: '8px' }}
                    />
                    <span style={{ 
                      fontWeight: 600,
                      color: documentScope === 'SELECTED_DOCS' 
                        ? 'var(--primary-700)' 
                        : 'var(--gray-700)',
                    }}>
                      Selected Documents
                    </span>
                    <div style={{ 
                      fontSize: '12px', 
                      color: 'var(--gray-600)',
                      marginTop: '4px',
                      marginLeft: '24px',
                    }}>
                      Choose specific documents
                    </div>
                  </label>
                </div>
              </div>

              {/* Document Selection */}
              {documentScope === 'SELECTED_DOCS' && (
                <div style={{ marginBottom: '24px' }}>
                  <label style={{ 
                    display: 'block', 
                    marginBottom: '8px', 
                    fontWeight: 600,
                    fontSize: '14px',
                    color: 'var(--gray-700)',
                  }}>
                    Select Documents <span style={{ color: 'var(--error-main)' }}>*</span>
                    {selectedDocs.length > 0 && (
                      <span style={{
                        marginLeft: '8px',
                        padding: '2px 8px',
                        borderRadius: 'var(--radius-full)',
                        fontSize: '11px',
                        fontWeight: 700,
                        background: 'var(--primary-100)',
                        color: 'var(--primary-700)',
                      }}>
                        {selectedDocs.length} selected
                      </span>
                    )}
                  </label>
                  {documents.length === 0 ? (
                    <div style={{
                      padding: '16px',
                      background: 'var(--warning-light)',
                      border: '1px solid var(--warning-main)',
                      borderRadius: 'var(--radius-md)',
                      color: 'var(--gray-700)',
                      fontSize: '14px',
                    }}>
                      ⚠️ No indexed documents available. Please upload and index documents first.
                    </div>
                  ) : (
                    <div style={{
                      border: '2px solid var(--gray-300)',
                      borderRadius: 'var(--radius-md)',
                      maxHeight: '240px',
                      overflow: 'auto',
                      background: 'var(--gray-50)',
                    }}>
                      {documents.map((doc, index) => (
                        <label
                          key={doc.id}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            padding: '12px 16px',
                            cursor: 'pointer',
                            borderBottom: index < documents.length - 1 ? '1px solid var(--gray-200)' : 'none',
                            background: selectedDocs.includes(doc.id) ? 'var(--primary-50)' : 'white',
                            transition: 'all var(--transition-fast)',
                          }}
                          onMouseEnter={(e) => {
                            if (!selectedDocs.includes(doc.id)) {
                              e.currentTarget.style.background = 'var(--gray-100)';
                            }
                          }}
                          onMouseLeave={(e) => {
                            if (!selectedDocs.includes(doc.id)) {
                              e.currentTarget.style.background = 'white';
                            }
                          }}
                        >
                          <input
                            type="checkbox"
                            checked={selectedDocs.includes(doc.id)}
                            onChange={() => toggleDocument(doc.id)}
                            style={{ 
                              marginRight: '12px',
                              width: '18px',
                              height: '18px',
                              cursor: 'pointer',
                            }}
                          />
                          <div style={{ flex: 1 }}>
                            <div style={{ 
                              fontWeight: 600,
                              fontSize: '14px',
                              color: 'var(--gray-900)',
                              marginBottom: '2px',
                            }}>
                              {doc.name}
                            </div>
                            <div style={{ 
                              fontSize: '12px',
                              color: 'var(--gray-600)',
                            }}>
                              {doc.file_type.toUpperCase()} • {(doc.file_size / 1024).toFixed(0)} KB
                            </div>
                          </div>
                        </label>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </form>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '20px 32px',
          borderTop: '1px solid var(--gray-200)',
          background: 'var(--gray-50)',
          display: 'flex',
          gap: '12px',
          justifyContent: 'flex-end',
        }}>
          <button
            type="button"
            onClick={onClose}
            disabled={creating}
            style={{
              padding: '12px 24px',
              border: '2px solid var(--gray-300)',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'white',
              color: 'var(--gray-700)',
              fontWeight: 600,
              fontSize: '15px',
              cursor: creating ? 'not-allowed' : 'pointer',
              opacity: creating ? 0.5 : 1,
            }}
          >
            Cancel
          </button>
          <button
            type="submit"
            onClick={handleSubmit}
            disabled={creating || loading || questionnaires.length === 0}
            style={{
              padding: '12px 32px',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              background: creating 
                ? 'var(--gray-400)' 
                : 'linear-gradient(135deg, var(--primary-600), var(--primary-700))',
              color: 'white',
              fontWeight: 600,
              fontSize: '15px',
              cursor: (creating || loading || questionnaires.length === 0) ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              boxShadow: creating ? 'none' : 'var(--shadow-md)',
            }}
          >
            {creating ? (
              <>
                <span style={{ animation: 'spin 1s linear infinite' }}>⚙</span>
                Creating...
              </>
            ) : (
              <>
                <span>🚀</span>
                Create Project
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
