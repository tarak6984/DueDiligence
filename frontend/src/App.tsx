import { useState } from 'react';
import ProjectList from './components/ProjectList';
import ProjectDetail from './components/ProjectDetail';
import DocumentManager from './components/DocumentManager';
import CreateProject from './components/CreateProject';
import ChatInterface from './components/ChatInterface';
import { Project } from './services/api';

type View = 'projects' | 'documents' | 'chat';

export default function App() {
  const [view, setView] = useState<View>('projects');
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleSelectProject = (project: Project) => {
    setSelectedProject(project);
  };

  const handleBack = () => {
    setSelectedProject(null);
    setRefreshKey(prev => prev + 1);
  };

  const handleProjectCreated = () => {
    setShowCreateProject(false);
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--gray-50)' }}>
      {/* Header */}
      <header style={{
        background: 'linear-gradient(135deg, var(--primary-700), var(--primary-900))',
        color: '#fff',
        padding: '0',
        boxShadow: 'var(--shadow-lg)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 32px' }}>
          <div 
            onClick={() => { setView('projects'); setSelectedProject(null); }}
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '12px',
              cursor: 'pointer',
              transition: 'all var(--transition-base)',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.opacity = '0.9';
              e.currentTarget.style.transform = 'scale(0.98)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.opacity = '1';
              e.currentTarget.style.transform = 'scale(1)';
            }}
          >
            <div style={{
              width: '40px',
              height: '40px',
              background: 'rgba(255, 255, 255, 0.2)',
              borderRadius: 'var(--radius-md)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '20px',
              fontWeight: 'bold',
              backdropFilter: 'blur(10px)',
            }}>
              📋
            </div>
            <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 700, letterSpacing: '-0.5px' }}>
              Questionnaire Agent
            </h1>
          </div>
          <nav style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={() => { setView('projects'); setSelectedProject(null); }}
              style={{
                padding: '10px 24px',
                backgroundColor: view === 'projects' ? 'rgba(255, 255, 255, 1)' : 'rgba(255, 255, 255, 0.1)',
                color: view === 'projects' ? 'var(--primary-700)' : '#fff',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '15px',
                backdropFilter: 'blur(10px)',
                transition: 'all var(--transition-base)',
              }}
            >
              📁 Projects
            </button>
            <button
              onClick={() => { setView('documents'); setSelectedProject(null); }}
              style={{
                padding: '10px 24px',
                backgroundColor: view === 'documents' ? 'rgba(255, 255, 255, 1)' : 'rgba(255, 255, 255, 0.1)',
                color: view === 'documents' ? 'var(--primary-700)' : '#fff',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '15px',
                backdropFilter: 'blur(10px)',
                transition: 'all var(--transition-base)',
              }}
            >
              📄 Documents
            </button>
            <button
              onClick={() => { setView('chat'); setSelectedProject(null); }}
              style={{
                padding: '10px 24px',
                backgroundColor: view === 'chat' ? 'rgba(255, 255, 255, 1)' : 'rgba(255, 255, 255, 0.1)',
                color: view === 'chat' ? 'var(--primary-700)' : '#fff',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '15px',
                backdropFilter: 'blur(10px)',
                transition: 'all var(--transition-base)',
              }}
            >
              💬 Chat
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: '1400px', margin: '0 auto', padding: '32px' }} className="fade-in">
        {view === 'projects' && !selectedProject && (
          <>
            <div style={{ marginBottom: '32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <h2 style={{ fontSize: '28px', fontWeight: 700, color: 'var(--gray-900)', marginBottom: '8px' }}>
                  Your Projects
                </h2>
                <p style={{ color: 'var(--gray-600)', fontSize: '15px' }}>
                  Manage questionnaires and generate AI-powered responses
                </p>
              </div>
              <button
                onClick={() => setShowCreateProject(true)}
                style={{
                  padding: '12px 24px',
                  background: 'linear-gradient(135deg, var(--success-main), var(--success-dark))',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 'var(--radius-md)',
                  cursor: 'pointer',
                  fontWeight: 600,
                  fontSize: '15px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  boxShadow: 'var(--shadow-md)',
                }}
              >
                <span style={{ fontSize: '18px' }}>+</span>
                Create New Project
              </button>
            </div>
            <ProjectList key={refreshKey} onSelectProject={handleSelectProject} />
          </>
        )}
        
        {view === 'projects' && selectedProject && (
          <ProjectDetail project={selectedProject} onBack={handleBack} />
        )}
        
        {view === 'documents' && (
          <DocumentManager key={refreshKey} />
        )}

        {view === 'chat' && (
          <div>
            <div style={{ marginBottom: '32px' }}>
              <h2 style={{ fontSize: '28px', fontWeight: 700, color: 'var(--gray-900)', marginBottom: '8px' }}>
                Document Chat
              </h2>
              <p style={{ color: 'var(--gray-600)', fontSize: '15px' }}>
                Ask questions about your indexed documents
              </p>
            </div>
            <ChatInterface />
          </div>
        )}
      </main>

      {/* Create Project Modal */}
      {showCreateProject && (
        <CreateProject
          onClose={() => setShowCreateProject(false)}
          onCreated={handleProjectCreated}
        />
      )}
    </div>
  );
}
