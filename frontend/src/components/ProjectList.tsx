import { useEffect, useState } from 'react';
import { api, Project } from '../services/api';
import { useToast } from './ToastContainer';
import ConfirmDialog from './ConfirmDialog';

interface ProjectListProps {
  onSelectProject: (project: Project) => void;
}

export default function ProjectList({ onSelectProject }: ProjectListProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingProject, setDeletingProject] = useState<string | null>(null);
  const toast = useToast();

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

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'READY': 
        return { color: 'white', bg: 'var(--success-dark)', icon: '✓' };
      case 'CREATING': 
        return { color: 'white', bg: 'var(--warning-dark)', icon: '⚙' };
      case 'GENERATING': 
        return { color: 'white', bg: 'var(--primary-700)', icon: '🤖' };
      case 'OUTDATED': 
        return { color: 'white', bg: 'var(--error-dark)', icon: '⚠' };
      case 'ERROR': 
        return { color: 'white', bg: 'var(--error-dark)', icon: '✕' };
      default: 
        return { color: 'white', bg: 'var(--gray-700)', icon: '○' };
    }
  };

  const getProgressPercentage = (answered: number, total: number) => {
    return total > 0 ? (answered / total) * 100 : 0;
  };

  const handleDeleteProject = async (projectId: string) => {
    try {
      await api.deleteProject(projectId);
      toast.success('Project deleted successfully');
      setDeletingProject(null);
      loadProjects();
    } catch (error) {
      console.error('Failed to delete project:', error);
      toast.error('Failed to delete project');
      setDeletingProject(null);
    }
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
            📊
          </div>
          <p style={{ fontSize: '16px', fontWeight: 500 }}>Loading projects...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {projects.length === 0 ? (
        <div style={{
          background: 'white',
          borderRadius: 'var(--radius-xl)',
          padding: '60px',
          textAlign: 'center',
          boxShadow: 'var(--shadow-sm)',
        }}>
          <div style={{ fontSize: '64px', marginBottom: '24px' }}>📋</div>
          <h3 style={{ fontSize: '24px', color: 'var(--gray-900)', marginBottom: '12px', fontWeight: 600 }}>
            No projects yet
          </h3>
          <p style={{ color: 'var(--gray-600)', fontSize: '16px', maxWidth: '400px', margin: '0 auto' }}>
            Create your first project to start automating questionnaire responses with AI
          </p>
        </div>
      ) : (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))',
          gap: '24px' 
        }}>
          {projects.map((project, index) => {
            const statusConfig = getStatusConfig(project.status);
            const progress = getProgressPercentage(project.answered_questions, project.total_questions);
            
            return (
              <div
                key={project.id}
                style={{
                  background: 'white',
                  border: '1px solid var(--gray-200)',
                  borderRadius: 'var(--radius-lg)',
                  padding: '24px',
                  cursor: 'pointer',
                  transition: 'all var(--transition-base)',
                  position: 'relative',
                  overflow: 'hidden',
                  animation: `fadeIn 0.3s ease-in-out ${index * 0.1}s both`,
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-4px)';
                  e.currentTarget.style.boxShadow = 'var(--shadow-lg)';
                  e.currentTarget.style.borderColor = 'var(--primary-300)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
                  e.currentTarget.style.borderColor = 'var(--gray-200)';
                }}
              >
                {/* Status Badge and Delete Button */}
                <div style={{ 
                  position: 'absolute', 
                  top: '16px', 
                  right: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '6px 12px',
                    borderRadius: 'var(--radius-full)',
                    fontSize: '11px',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    color: statusConfig.color,
                    backgroundColor: statusConfig.bg,
                    boxShadow: 'var(--shadow-sm)',
                  }}>
                    <span>{statusConfig.icon}</span>
                    <span>{project.status}</span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setDeletingProject(project.id);
                    }}
                    style={{
                      width: '32px',
                      height: '32px',
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
                    title="Delete project"
                  >
                    🗑️
                  </button>
                </div>

                {/* Project Name */}
                <h3 
                  onClick={() => onSelectProject(project)}
                  style={{ 
                  margin: '0 0 12px 0',
                  fontSize: '20px',
                  fontWeight: 700,
                  color: 'var(--gray-900)',
                  paddingRight: '120px',
                  lineHeight: 1.3,
                }}>
                  {project.name}
                </h3>

                {/* Progress Bar */}
                <div 
                  onClick={() => onSelectProject(project)}
                  style={{ marginBottom: '16px' }}>
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    marginBottom: '8px',
                  }}>
                    <span style={{ 
                      fontSize: '13px', 
                      fontWeight: 600,
                      color: 'var(--gray-700)',
                    }}>
                      Progress
                    </span>
                    <span style={{ 
                      fontSize: '13px', 
                      fontWeight: 700,
                      color: 'var(--primary-600)',
                    }}>
                      {project.answered_questions} / {project.total_questions}
                    </span>
                  </div>
                  <div style={{
                    width: '100%',
                    height: '8px',
                    backgroundColor: 'var(--gray-200)',
                    borderRadius: 'var(--radius-full)',
                    overflow: 'hidden',
                  }}>
                    <div style={{
                      width: `${progress}%`,
                      height: '100%',
                      background: progress === 100 
                        ? 'linear-gradient(90deg, var(--success-main), var(--success-light))'
                        : 'linear-gradient(90deg, var(--primary-600), var(--primary-400))',
                      borderRadius: 'var(--radius-full)',
                      transition: 'width 0.5s ease-in-out',
                    }} />
                  </div>
                </div>

                {/* Metadata */}
                <div 
                  onClick={() => onSelectProject(project)}
                  style={{ 
                  display: 'flex', 
                  gap: '16px',
                  paddingTop: '16px',
                  borderTop: '1px solid var(--gray-200)',
                }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ 
                      fontSize: '11px', 
                      color: 'var(--gray-500)',
                      textTransform: 'uppercase',
                      fontWeight: 600,
                      letterSpacing: '0.5px',
                      marginBottom: '4px',
                    }}>
                      Scope
                    </div>
                    <div style={{ 
                      fontSize: '13px', 
                      color: 'var(--gray-700)',
                      fontWeight: 600,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                    }}>
                      <span>📁</span>
                      {project.document_scope}
                    </div>
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ 
                      fontSize: '11px', 
                      color: 'var(--gray-500)',
                      textTransform: 'uppercase',
                      fontWeight: 600,
                      letterSpacing: '0.5px',
                      marginBottom: '4px',
                    }}>
                      Created
                    </div>
                    <div style={{ 
                      fontSize: '13px', 
                      color: 'var(--gray-700)',
                      fontWeight: 600,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                    }}>
                      <span>📅</span>
                      {new Date(project.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      {deletingProject && (
        <ConfirmDialog
          title="Delete Project"
          message="Are you sure you want to delete this project? This action cannot be undone."
          confirmText="Delete"
          cancelText="Cancel"
          type="danger"
          onConfirm={() => handleDeleteProject(deletingProject)}
          onCancel={() => setDeletingProject(null)}
        />
      )}
    </div>
  );
}
