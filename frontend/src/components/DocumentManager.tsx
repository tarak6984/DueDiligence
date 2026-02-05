import { useEffect, useState, useRef } from 'react';
import { api, Document } from '../services/api';
import { useToast } from './ToastContainer';
import ConfirmDialog from './ConfirmDialog';

export default function DocumentManager() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [uploadType, setUploadType] = useState<'reference' | 'questionnaire'>('reference');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [deletingDocument, setDeletingDocument] = useState<string | null>(null);
  const toast = useToast();

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const data = await api.listDocuments();
      setDocuments(data.documents);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file: File, isQuestionnaire: boolean) => {
    setUploading(true);
    try {
      const document = await api.uploadDocument(file, isQuestionnaire);
      toast.success(`Document uploaded: ${document.name}`);
      
      await api.indexDocument(document.id);
      toast.info('Document indexing started');
      
      setTimeout(loadDocuments, 2000);
    } catch (error) {
      console.error('Failed to upload document:', error);
      toast.error('Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>, isQuestionnaire: boolean) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileUpload(file, isQuestionnaire);
    }
    // Reset input
    event.target.value = '';
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0], uploadType === 'questionnaire');
    }
  };

  const handleIndex = async (documentId: string) => {
    try {
      const result = await api.indexDocument(documentId);
      toast.info(`Indexing started. Request ID: ${result.request_id}`);
      setTimeout(loadDocuments, 2000);
    } catch (error) {
      console.error('Failed to index document:', error);
      toast.error('Failed to index document');
    }
  };

  const handleDeleteDocument = async (documentId: string) => {
    try {
      await api.deleteDocument(documentId);
      toast.success('Document deleted successfully');
      setDeletingDocument(null);
      loadDocuments();
    } catch (error) {
      console.error('Failed to delete document:', error);
      toast.error('Failed to delete document');
      setDeletingDocument(null);
    }
  };

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'INDEXED': 
        return { color: 'white', bg: 'var(--success-dark)', icon: '✓' };
      case 'INDEXING': 
        return { color: 'white', bg: 'var(--primary-700)', icon: '⚙' };
      case 'PENDING': 
        return { color: 'white', bg: 'var(--warning-dark)', icon: '○' };
      case 'FAILED': 
        return { color: 'white', bg: 'var(--error-dark)', icon: '✕' };
      default: 
        return { color: 'white', bg: 'var(--gray-700)', icon: '?' };
    }
  };

  const getFileIcon = (fileType: string) => {
    if (fileType.includes('pdf')) return '📄';
    if (fileType.includes('word') || fileType.includes('docx')) return '📝';
    if (fileType.includes('excel') || fileType.includes('xlsx')) return '📊';
    if (fileType.includes('powerpoint') || fileType.includes('pptx')) return '📑';
    return '📁';
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const handleDocumentClick = (doc: Document) => {
    // Open document in new tab
    const downloadUrl = api.getDocumentDownloadUrl(doc.id);
    window.open(downloadUrl, '_blank');
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        padding: '60px',
        color: 'var(--gray-600)',
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            fontSize: '48px', 
            marginBottom: '16px',
            animation: 'pulse 2s ease-in-out infinite',
          }}>
            📚
          </div>
          <p style={{ fontSize: '16px', fontWeight: 500 }}>Loading documents...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '28px', fontWeight: 700, color: 'var(--gray-900)', marginBottom: '8px' }}>
          Document Management
        </h2>
        <p style={{ color: 'var(--gray-600)', fontSize: '15px' }}>
          Upload and manage reference documents and questionnaires
        </p>
      </div>

      {/* Upload Section */}
      <div style={{ 
        background: 'white',
        borderRadius: 'var(--radius-lg)',
        padding: '32px',
        marginBottom: '32px',
        boxShadow: 'var(--shadow-md)',
      }}>
        <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--gray-900)', marginBottom: '20px' }}>
          📤 Upload Documents
        </h3>
        
        {/* Upload Type Selector */}
        <div style={{ marginBottom: '20px', display: 'flex', gap: '12px' }}>
          <button
            onClick={() => setUploadType('reference')}
            style={{
              padding: '10px 20px',
              background: uploadType === 'reference' 
                ? 'linear-gradient(135deg, var(--primary-600), var(--primary-700))' 
                : 'var(--gray-100)',
              color: uploadType === 'reference' ? 'white' : 'var(--gray-700)',
              border: uploadType === 'reference' ? 'none' : '1px solid var(--gray-300)',
              borderRadius: 'var(--radius-md)',
              fontWeight: 600,
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <span>📄</span> Reference Document
          </button>
          <button
            onClick={() => setUploadType('questionnaire')}
            style={{
              padding: '10px 20px',
              background: uploadType === 'questionnaire' 
                ? 'linear-gradient(135deg, var(--primary-600), var(--primary-700))' 
                : 'var(--gray-100)',
              color: uploadType === 'questionnaire' ? 'white' : 'var(--gray-700)',
              border: uploadType === 'questionnaire' ? 'none' : '1px solid var(--gray-300)',
              borderRadius: 'var(--radius-md)',
              fontWeight: 600,
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <span>📋</span> Questionnaire
          </button>
        </div>

        {/* Drag & Drop Zone */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          style={{
            border: dragActive 
              ? '3px dashed var(--primary-500)' 
              : '2px dashed var(--gray-300)',
            borderRadius: 'var(--radius-lg)',
            padding: '48px 24px',
            textAlign: 'center',
            backgroundColor: dragActive ? 'var(--primary-50)' : 'var(--gray-50)',
            cursor: uploading ? 'not-allowed' : 'pointer',
            transition: 'all var(--transition-base)',
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.xlsx,.pptx"
            onChange={(e) => handleInputChange(e, uploadType === 'questionnaire')}
            disabled={uploading}
            style={{ display: 'none' }}
          />
          
          {uploading ? (
            <>
              <div style={{ 
                fontSize: '48px', 
                marginBottom: '16px',
                animation: 'spin 2s linear infinite',
              }}>
                ⚙
              </div>
              <p style={{ fontSize: '18px', fontWeight: 600, color: 'var(--primary-600)', marginBottom: '8px' }}>
                Uploading...
              </p>
              <p style={{ fontSize: '14px', color: 'var(--gray-600)' }}>
                Please wait while we process your document
              </p>
            </>
          ) : (
            <>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>
                {dragActive ? '📥' : '📂'}
              </div>
              <p style={{ fontSize: '18px', fontWeight: 600, color: 'var(--gray-900)', marginBottom: '8px' }}>
                {dragActive ? 'Drop your file here' : 'Drag & drop your file here'}
              </p>
              <p style={{ fontSize: '14px', color: 'var(--gray-600)', marginBottom: '16px' }}>
                or click to browse
              </p>
              <div style={{ 
                display: 'inline-flex',
                gap: '8px',
                padding: '8px 16px',
                background: 'white',
                borderRadius: 'var(--radius-md)',
                fontSize: '12px',
                color: 'var(--gray-600)',
                border: '1px solid var(--gray-300)',
              }}>
                <span>Supported formats:</span>
                <strong>PDF, DOCX, XLSX, PPTX</strong>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Documents List */}
      <div style={{
        background: 'white',
        borderRadius: 'var(--radius-lg)',
        padding: '24px',
        boxShadow: 'var(--shadow-md)',
      }}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '20px',
        }}>
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--gray-900)' }}>
            📚 Documents
          </h3>
          <span style={{
            padding: '6px 12px',
            borderRadius: 'var(--radius-full)',
            fontSize: '12px',
            fontWeight: 700,
            background: 'var(--primary-50)',
            color: 'var(--primary-700)',
          }}>
            {documents.length} {documents.length === 1 ? 'document' : 'documents'}
          </span>
        </div>

        {documents.length === 0 ? (
          <div style={{ 
            textAlign: 'center',
            padding: '48px 24px',
            color: 'var(--gray-500)',
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
            <p style={{ fontSize: '16px', fontWeight: 500 }}>No documents uploaded yet</p>
            <p style={{ fontSize: '14px', marginTop: '8px' }}>Upload your first document to get started</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {documents.map((doc, index) => {
              const statusConfig = getStatusConfig(doc.indexing_status);
              return (
                <div
                  key={doc.id}
                  style={{
                    border: '1px solid var(--gray-200)',
                    borderRadius: 'var(--radius-md)',
                    padding: '20px',
                    background: 'var(--gray-50)',
                    transition: 'all var(--transition-base)',
                    animation: `fadeIn 0.3s ease-in-out ${index * 0.05}s both`,
                    cursor: 'pointer',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'white';
                    e.currentTarget.style.boxShadow = 'var(--shadow-md)';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'var(--gray-50)';
                    e.currentTarget.style.boxShadow = 'none';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', gap: '16px' }}>
                    <div 
                      style={{ flex: 1, cursor: 'pointer' }}
                      onClick={() => handleDocumentClick(doc)}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                        <span style={{ fontSize: '32px' }}>{getFileIcon(doc.file_type)}</span>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
                            <strong style={{ fontSize: '16px', color: 'var(--gray-900)' }}>
                              {doc.name}
                            </strong>
                            {doc.is_questionnaire && (
                              <span style={{
                                padding: '4px 10px',
                                borderRadius: 'var(--radius-full)',
                                fontSize: '10px',
                                fontWeight: 700,
                                textTransform: 'uppercase',
                                letterSpacing: '0.5px',
                                backgroundColor: 'var(--primary-100)',
                                color: 'var(--primary-700)',
                                border: '1px solid var(--primary-300)',
                              }}>
                                📋 QUESTIONNAIRE
                              </span>
                            )}
                          </div>
                          <div style={{ display: 'flex', gap: '16px', fontSize: '13px', color: 'var(--gray-600)' }}>
                            <span>📎 {doc.file_type.toUpperCase()}</span>
                            <span>💾 {formatFileSize(doc.file_size)}</span>
                            <span>📅 {new Date(doc.uploaded_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexShrink: 0 }}>
                      <span
                        style={{
                          padding: '6px 14px',
                          borderRadius: 'var(--radius-full)',
                          fontSize: '11px',
                          fontWeight: 700,
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px',
                          color: statusConfig.color,
                          backgroundColor: statusConfig.bg,
                          boxShadow: 'var(--shadow-sm)',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                        }}
                      >
                        <span>{statusConfig.icon}</span>
                        <span>{doc.indexing_status}</span>
                      </span>
                      {doc.indexing_status === 'PENDING' && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleIndex(doc.id);
                          }}
                          style={{
                            padding: '8px 16px',
                            fontSize: '13px',
                            background: 'linear-gradient(135deg, var(--primary-600), var(--primary-700))',
                            color: '#fff',
                            border: 'none',
                            borderRadius: 'var(--radius-md)',
                            fontWeight: 600,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            boxShadow: 'var(--shadow-sm)',
                          }}
                        >
                          <span>⚡</span> Index Now
                        </button>
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setDeletingDocument(doc.id);
                        }}
                        style={{
                          width: '36px',
                          height: '36px',
                          borderRadius: 'var(--radius-full)',
                          background: 'var(--error-light)',
                          border: 'none',
                          color: 'var(--error-dark)',
                          fontSize: '16px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          cursor: 'pointer',
                          transition: 'all var(--transition-base)',
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background = 'var(--error-dark)';
                          e.currentTarget.style.color = 'white';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background = 'var(--error-light)';
                          e.currentTarget.style.color = 'var(--error-dark)';
                        }}
                        title="Delete document"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      {deletingDocument && (
        <ConfirmDialog
          title="Delete Document"
          message="Are you sure you want to delete this document? This action cannot be undone and may affect projects using this document."
          confirmText="Delete"
          cancelText="Cancel"
          type="danger"
          onConfirm={() => handleDeleteDocument(deletingDocument)}
          onCancel={() => setDeletingDocument(null)}
        />
      )}
    </div>
  );
}
