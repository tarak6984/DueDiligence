import { useEffect, useState } from 'react';
import { api, Project, Section, Answer } from '../services/api';

interface ProjectDetailProps {
  project: Project;
  onBack: () => void;
}

export default function ProjectDetail({ project, onBack }: ProjectDetailProps) {
  const [sections, setSections] = useState<Section[]>([]);
  const [answers, setAnswers] = useState<Record<string, Answer>>({});
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadProjectData();
  }, [project.id]);

  const loadProjectData = async () => {
    try {
      const [projectInfo, answersList] = await Promise.all([
        api.getProjectInfo(project.id),
        api.listAnswers(project.id),
      ]);

      setSections(projectInfo.sections);
      
      const answersMap: Record<string, Answer> = {};
      answersList.answers.forEach(answer => {
        answersMap[answer.question_id] = answer;
      });
      setAnswers(answersMap);
    } catch (error) {
      console.error('Failed to load project data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateAll = async () => {
    setGenerating(true);
    try {
      const result = await api.generateAllAnswers(project.id);
      alert(`Answer generation started. Request ID: ${result.request_id}`);
      // In production, poll for request status
      setTimeout(() => {
        loadProjectData();
        setGenerating(false);
      }, 3000);
    } catch (error) {
      console.error('Failed to generate answers:', error);
      setGenerating(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'GENERATED': return '#4caf50';
      case 'CONFIRMED': return '#2196f3';
      case 'MANUAL_UPDATED': return '#ff9800';
      case 'REJECTED': return '#f44336';
      case 'MISSING_DATA': return '#ff5722';
      case 'PENDING': return '#9e9e9e';
      default: return '#9e9e9e';
    }
  };

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading project details...</div>;
  }

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ marginBottom: '20px' }}>
        <button onClick={onBack} style={{ marginRight: '10px', padding: '8px 16px' }}>
          ← Back to Projects
        </button>
        <button
          onClick={handleGenerateAll}
          disabled={generating}
          style={{
            padding: '8px 16px',
            backgroundColor: '#2196f3',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: generating ? 'not-allowed' : 'pointer',
          }}
        >
          {generating ? 'Generating...' : 'Generate All Answers'}
        </button>
      </div>

      <h2>{project.name}</h2>
      <p style={{ color: '#666' }}>
        Progress: {project.answered_questions} / {project.total_questions} questions answered
      </p>

      <div style={{ marginTop: '30px' }}>
        {sections.map(section => (
          <div key={section.id} style={{ marginBottom: '40px' }}>
            <h3 style={{
              borderBottom: '2px solid #2196f3',
              paddingBottom: '10px',
              color: '#2196f3',
            }}>
              {section.order}. {section.title}
            </h3>
            
            <div style={{ marginTop: '20px' }}>
              {section.questions.map(question => {
                const answer = answers[question.id];
                return (
                  <div
                    key={question.id}
                    style={{
                      border: '1px solid #ddd',
                      borderRadius: '8px',
                      padding: '15px',
                      marginBottom: '15px',
                      backgroundColor: '#fff',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <div style={{ flex: 1 }}>
                        <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>
                          {section.order}.{question.order} {question.text}
                        </p>
                        
                        {answer ? (
                          <div style={{ marginTop: '10px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                              <span
                                style={{
                                  padding: '4px 8px',
                                  borderRadius: '4px',
                                  fontSize: '11px',
                                  fontWeight: 'bold',
                                  color: '#fff',
                                  backgroundColor: getStatusColor(answer.status),
                                }}
                              >
                                {answer.status}
                              </span>
                              {answer.confidence_score !== undefined && (
                                <span style={{ fontSize: '12px', color: '#666' }}>
                                  Confidence: {(answer.confidence_score * 100).toFixed(0)}%
                                </span>
                              )}
                            </div>
                            
                            {answer.ai_answer && (
                              <div style={{ 
                                padding: '10px',
                                backgroundColor: '#f5f5f5',
                                borderRadius: '4px',
                                fontSize: '14px',
                              }}>
                                {answer.ai_answer}
                              </div>
                            )}
                            
                            {answer.citations && answer.citations.length > 0 && (
                              <div style={{ marginTop: '10px', fontSize: '12px', color: '#666' }}>
                                <strong>Citations:</strong> {answer.citations.length} reference(s)
                              </div>
                            )}
                          </div>
                        ) : (
                          <p style={{ color: '#999', fontStyle: 'italic' }}>No answer yet</p>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
