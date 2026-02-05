import { useEffect, useState } from 'react';
import { api, Document } from '../services/api';

export default function DocumentManager() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

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

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>, isQuestionnaire: boolean) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const document = await api.uploadDocument(file, isQuestionnaire);
      alert(`Document uploaded: ${document.name}`);
      
      // Auto-index the document
      await api.indexDocument(document.id);
      alert('Document indexing started');
      
      // Reload documents after a delay
      setTimeout(loadDocuments, 2000);
    } catch (error) {
      console.error('Failed to upload document:', error);
      alert('Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleIndex = async (documentId: string) => {
    try {
      const result = await api.indexDocument(documentId);
      alert(`Indexing started. Request ID: ${result.request_id}`);
      setTimeout(loadDocuments, 2000);
    } catch (error) {
      console.error('Failed to index document:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'INDEXED': return '#4caf50';
      case 'INDEXING': return '#2196f3';
      case 'PENDING': return '#ff9800';
      case 'FAILED': return '#f44336';
      default: return '#9e9e9e';
    }
  };

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading documents...</div>;
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2>Document Management</h2>
      
      <div style={{ marginBottom: '30px', padding: '20px', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
        <h3>Upload Documents</h3>
        <div style={{ display: 'flex', gap: '20px', marginTop: '15px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Upload Reference Document
            </label>
            <input
              type="file"
              accept=".pdf,.docx,.xlsx,.pptx"
              onChange={(e) => handleFileUpload(e, false)}
              disabled={uploading}
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Upload Questionnaire
            </label>
            <input
              type="file"
              accept=".pdf,.docx,.xlsx,.pptx"
              onChange={(e) => handleFileUpload(e, true)}
              disabled={uploading}
            />
          </div>
        </div>
        {uploading && <p style={{ marginTop: '10px', color: '#2196f3' }}>Uploading...</p>}
      </div>

      <h3>Documents ({documents.length})</h3>
      <div style={{ display: 'grid', gap: '10px', marginTop: '15px' }}>
        {documents.map(doc => (
          <div
            key={doc.id}
            style={{
              border: '1px solid #ddd',
              borderRadius: '8px',
              padding: '15px',
              backgroundColor: '#fff',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <strong>{doc.name}</strong>
                  {doc.is_questionnaire && (
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '11px',
                      backgroundColor: '#e3f2fd',
                      color: '#1976d2',
                    }}>
                      QUESTIONNAIRE
                    </span>
                  )}
                </div>
                <div style={{ marginTop: '5px', fontSize: '12px', color: '#666' }}>
                  Type: {doc.file_type} | Size: {(doc.file_size / 1024).toFixed(0)} KB
                </div>
                <div style={{ marginTop: '5px', fontSize: '12px', color: '#999' }}>
                  Uploaded: {new Date(doc.uploaded_at).toLocaleString()}
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span
                  style={{
                    padding: '5px 12px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    fontWeight: 'bold',
                    color: '#fff',
                    backgroundColor: getStatusColor(doc.indexing_status),
                  }}
                >
                  {doc.indexing_status}
                </span>
                {doc.indexing_status === 'PENDING' && (
                  <button
                    onClick={() => handleIndex(doc.id)}
                    style={{
                      padding: '5px 12px',
                      fontSize: '12px',
                      backgroundColor: '#2196f3',
                      color: '#fff',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                    }}
                  >
                    Index Now
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
