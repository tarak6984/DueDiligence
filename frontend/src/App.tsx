import { useState } from 'react';
import ProjectList from './components/ProjectList';
import ProjectDetail from './components/ProjectDetail';
import DocumentManager from './components/DocumentManager';
import CreateProject from './components/CreateProject';
import { Project } from './services/api';

type View = 'projects' | 'documents';

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
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* Header */}
      <header style={{
        backgroundColor: '#1976d2',
        color: '#fff',
        padding: '20px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: 0, fontSize: '24px' }}>Questionnaire Agent</h1>
          <nav style={{ display: 'flex', gap: '20px' }}>
            <button
              onClick={() => { setView('projects'); setSelectedProject(null); }}
              style={{
                padding: '8px 16px',
                backgroundColor: view === 'projects' ? '#fff' : 'transparent',
                color: view === 'projects' ? '#1976d2' : '#fff',
                border: '2px solid #fff',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: 'bold',
              }}
            >
              Projects
            </button>
            <button
              onClick={() => { setView('documents'); setSelectedProject(null); }}
              style={{
                padding: '8px 16px',
                backgroundColor: view === 'documents' ? '#fff' : 'transparent',
                color: view === 'documents' ? '#1976d2' : '#fff',
                border: '2px solid #fff',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: 'bold',
              }}
            >
              Documents
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
        {view === 'projects' && !selectedProject && (
          <>
            <div style={{ marginBottom: '20px' }}>
              <button
                onClick={() => setShowCreateProject(true)}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#4caf50',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  fontSize: '16px',
                }}
              >
                + Create New Project
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
