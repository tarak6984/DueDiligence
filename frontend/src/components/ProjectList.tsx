import { useEffect, useState } from 'react';
import { api, Project } from '../services/api';

interface ProjectListProps {
  onSelectProject: (project: Project) => void;
}

export default function ProjectList({ onSelectProject }: ProjectListProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const data = await api.listProjects();
      setProjects(data.projects);
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'READY': return '#4caf50';
      case 'CREATING': return '#ff9800';
      case 'GENERATING': return '#2196f3';
      case 'OUTDATED': return '#ff5722';
      case 'ERROR': return '#f44336';
      default: return '#9e9e9e';
    }
  };

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading projects...</div>;
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2>Projects</h2>
      {projects.length === 0 ? (
        <p>No projects yet. Create your first project to get started.</p>
      ) : (
        <div style={{ display: 'grid', gap: '15px' }}>
          {projects.map(project => (
            <div
              key={project.id}
              onClick={() => onSelectProject(project)}
              style={{
                border: '1px solid #ddd',
                borderRadius: '8px',
                padding: '20px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                backgroundColor: '#fff',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
                e.currentTarget.style.borderColor = '#2196f3';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow = 'none';
                e.currentTarget.style.borderColor = '#ddd';
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div>
                  <h3 style={{ margin: '0 0 10px 0' }}>{project.name}</h3>
                  <p style={{ margin: '5px 0', color: '#666' }}>
                    Questions: {project.answered_questions} / {project.total_questions}
                  </p>
                  <p style={{ margin: '5px 0', color: '#666', fontSize: '14px' }}>
                    Scope: {project.document_scope}
                  </p>
                </div>
                <div>
                  <span
                    style={{
                      padding: '5px 12px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: 'bold',
                      color: '#fff',
                      backgroundColor: getStatusColor(project.status),
                    }}
                  >
                    {project.status}
                  </span>
                </div>
              </div>
              <div style={{ marginTop: '10px', fontSize: '12px', color: '#999' }}>
                Created: {new Date(project.created_at).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
