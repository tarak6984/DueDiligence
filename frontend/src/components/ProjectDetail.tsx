import { useEffect, useState } from 'react';
import { api, Project, Section, Answer } from '../services/api';
import { useToast } from './ToastContainer';

interface ProjectDetailProps {
  project: Project;
  onBack: () => void;
}

export default function ProjectDetail({ project, onBack }: ProjectDetailProps) {
  const [sections, setSections] = useState<Section[]>([]);
  const [answers, setAnswers] = useState<Record<string, Answer>>({});
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [expandedAnswers, setExpandedAnswers] = useState<Set<string>>(new Set());
  const toast = useToast();

  useEffect(() => {
    loadProjectData();
  }, [project.id]);

  useEffect(() => {
    // Auto-expand all sections by default
    if (sections.length > 0) {
      setExpandedSections(new Set(sections.map(s => s.id)));
    }
  }, [sections]);

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
      toast.info(`Answer generation started. Request ID: ${result.request_id}`);
      setTimeout(() => {
        loadProjectData();
        setGenerating(false);
      }, 3000);
    } catch (error) {
      console.error('Failed to generate answers:', error);
      toast.error('Failed to generate answers');
      setGenerating(false);
    }
  };

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
      } else {
        newSet.add(sectionId);
      }
      return newSet;
    });
  };

  const toggleAnswer = (questionId: string) => {
    setExpandedAnswers(prev => {
      const newSet = new Set(prev);
      if (newSet.has(questionId)) {
        newSet.delete(questionId);
      } else {
        newSet.add(questionId);
      }
      return newSet;
    });
  };

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'GENERATED': 
        return { color: 'white', bg: 'var(--success-dark)', icon: '✓' };
      case 'CONFIRMED': 
        return { color: 'white', bg: 'var(--primary-700)', icon: '✓✓' };
      case 'MANUAL_UPDATED': 
        return { color: 'white', bg: 'var(--warning-dark)', icon: '✎' };
      case 'REJECTED': 
        return { color: 'white', bg: 'var(--error-dark)', icon: '✕' };
      case 'MISSING_DATA': 
        return { color: 'white', bg: 'var(--error-dark)', icon: '⚠' };
      case 'PENDING': 
        return { color: 'white', bg: 'var(--gray-700)', icon: '○' };
      default: 
        return { color: 'white', bg: 'var(--gray-700)', icon: '○' };
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'var(--success-main)';
    if (score >= 0.6) return 'var(--warning-main)';
    return 'var(--error-main)';
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        padding: '60px' 
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            fontSize: '48px', 
            marginBottom: '16px',
            animation: 'pulse 2s ease-in-out infinite' 
          }}>
            📊
          </div>
          <p style={{ fontSize: '16px', fontWeight: 500, color: 'var(--gray-600)' }}>
            Loading project details...
          </p>
        </div>
      </div>
    );
  }

  const progress = project.total_questions > 0 
    ? (project.answered_questions / project.total_questions) * 100 
    : 0;

  return (
    <div className="fade-in">
      {/* Header */}
      <div style={{ 
        background: 'white',
        borderRadius: 'var(--radius-lg)',
        padding: '24px',
        marginBottom: '24px',
        boxShadow: 'var(--shadow-md)',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '20px' }}>
          <button 
            onClick={onBack} 
            style={{ 
              padding: '10px 20px',
              background: 'var(--gray-100)',
              color: 'var(--gray-700)',
              border: '1px solid var(--gray-300)',
              borderRadius: 'var(--radius-md)',
              fontWeight: 600,
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <span>←</span> Back to Projects
          </button>
          <button
            onClick={handleGenerateAll}
            disabled={generating}
            style={{
              padding: '10px 20px',
              background: generating 
                ? 'var(--gray-400)' 
                : 'linear-gradient(135deg, var(--primary-600), var(--primary-700))',
              color: '#fff',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              fontWeight: 600,
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              boxShadow: generating ? 'none' : 'var(--shadow-md)',
            }}
          >
            {generating ? (
              <>
                <span style={{ animation: 'spin 1s linear infinite' }}>⚙</span>
                Generating...
              </>
            ) : (
              <>
                <span>🤖</span>
                Generate All Answers
              </>
            )}
          </button>
        </div>

        <h2 style={{ 
          fontSize: '28px', 
          fontWeight: 700, 
          color: 'var(--gray-900)',
          marginBottom: '16px',
        }}>
          {project.name}
        </h2>

        {/* Progress Bar */}
        <div>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: '8px',
          }}>
            <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--gray-700)' }}>
              Overall Progress
            </span>
            <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--primary-600)' }}>
              {project.answered_questions} / {project.total_questions} questions
            </span>
          </div>
          <div style={{
            width: '100%',
            height: '10px',
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
      </div>

      {/* Sections */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {sections.map((section, sectionIndex) => {
          const isExpanded = expandedSections.has(section.id);
          const sectionAnswers = section.questions.map(q => answers[q.id]).filter(Boolean);
          const answeredCount = sectionAnswers.length;
          
          return (
            <div 
              key={section.id} 
              style={{
                background: 'white',
                borderRadius: 'var(--radius-lg)',
                overflow: 'hidden',
                boxShadow: 'var(--shadow-sm)',
                border: '1px solid var(--gray-200)',
                animation: `fadeIn 0.3s ease-in-out ${sectionIndex * 0.05}s both`,
              }}
            >
              {/* Section Header */}
              <div
                onClick={() => toggleSection(section.id)}
                style={{
                  padding: '20px 24px',
                  background: isExpanded 
                    ? 'linear-gradient(135deg, var(--primary-50), var(--primary-100))' 
                    : 'var(--gray-50)',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  borderBottom: isExpanded ? '1px solid var(--gray-200)' : 'none',
                  transition: 'all var(--transition-base)',
                }}
              >
                <div style={{ flex: 1 }}>
                  <h3 style={{
                    fontSize: '18px',
                    fontWeight: 700,
                    color: 'var(--primary-700)',
                    marginBottom: '6px',
                  }}>
                    {section.order}. {section.title}
                  </h3>
                  <p style={{ 
                    fontSize: '13px', 
                    color: 'var(--gray-600)',
                    fontWeight: 500,
                  }}>
                    {answeredCount} / {section.questions.length} questions answered
                  </p>
                </div>
                <div style={{ 
                  fontSize: '20px',
                  color: 'var(--primary-600)',
                  transition: 'transform var(--transition-base)',
                  transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                }}>
                  ▼
                </div>
              </div>

              {/* Section Content */}
              {isExpanded && (
                <div style={{ padding: '16px' }}>
                  {section.questions.map((question, qIndex) => {
                    const answer = answers[question.id];
                    const isAnswerExpanded = expandedAnswers.has(question.id);
                    const statusConfig = answer ? getStatusConfig(answer.status) : getStatusConfig('PENDING');
                    
                    return (
                      <div
                        key={question.id}
                        style={{
                          border: '1px solid var(--gray-200)',
                          borderRadius: 'var(--radius-md)',
                          marginBottom: qIndex < section.questions.length - 1 ? '12px' : '0',
                          overflow: 'hidden',
                          transition: 'all var(--transition-base)',
                        }}
                      >
                        {/* Question Header */}
                        <div
                          onClick={() => answer && toggleAnswer(question.id)}
                          style={{
                            padding: '16px',
                            background: answer ? 'white' : 'var(--gray-50)',
                            cursor: answer ? 'pointer' : 'default',
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', gap: '12px' }}>
                            <p style={{ 
                              fontWeight: 600, 
                              fontSize: '14px',
                              color: 'var(--gray-900)',
                              flex: 1,
                              lineHeight: 1.5,
                            }}>
                              <span style={{ color: 'var(--primary-600)', marginRight: '8px' }}>
                                {section.order}.{question.order}
                              </span>
                              {question.text}
                            </p>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
                              <span
                                style={{
                                  padding: '4px 10px',
                                  borderRadius: 'var(--radius-full)',
                                  fontSize: '10px',
                                  fontWeight: 700,
                                  textTransform: 'uppercase',
                                  letterSpacing: '0.5px',
                                  color: statusConfig.color,
                                  backgroundColor: statusConfig.bg,
                                  boxShadow: 'var(--shadow-sm)',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '4px',
                                }}
                              >
                                <span>{statusConfig.icon}</span>
                                <span>{answer?.status || 'PENDING'}</span>
                              </span>
                              {answer && (
                                <span style={{ 
                                  fontSize: '16px',
                                  color: 'var(--gray-400)',
                                  transition: 'transform var(--transition-base)',
                                  transform: isAnswerExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                                }}>
                                  ▼
                                </span>
                              )}
                            </div>
                          </div>

                          {/* Confidence Score (always visible if exists) */}
                          {answer?.confidence_score !== undefined && (
                            <div style={{ 
                              marginTop: '12px',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                            }}>
                              <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--gray-600)' }}>
                                Confidence:
                              </span>
                              <div style={{ flex: 1, maxWidth: '200px' }}>
                                <div style={{
                                  height: '6px',
                                  backgroundColor: 'var(--gray-200)',
                                  borderRadius: 'var(--radius-full)',
                                  overflow: 'hidden',
                                }}>
                                  <div style={{
                                    width: `${answer.confidence_score * 100}%`,
                                    height: '100%',
                                    backgroundColor: getConfidenceColor(answer.confidence_score),
                                    borderRadius: 'var(--radius-full)',
                                    transition: 'width 0.5s ease-in-out',
                                  }} />
                                </div>
                              </div>
                              <span style={{ 
                                fontSize: '12px', 
                                fontWeight: 700,
                                color: getConfidenceColor(answer.confidence_score),
                              }}>
                                {(answer.confidence_score * 100).toFixed(0)}%
                              </span>
                            </div>
                          )}
                        </div>

                        {/* Answer Content (Expanded) */}
                        {answer && isAnswerExpanded && (
                          <div style={{ 
                            padding: '16px',
                            background: 'var(--gray-50)',
                            borderTop: '1px solid var(--gray-200)',
                          }}>
                            {answer.ai_answer && (
                              <div style={{ marginBottom: '16px' }}>
                                <div style={{ 
                                  fontSize: '12px', 
                                  fontWeight: 700,
                                  color: 'var(--gray-700)',
                                  marginBottom: '8px',
                                  textTransform: 'uppercase',
                                  letterSpacing: '0.5px',
                                }}>
                                  AI Answer
                                </div>
                                <div style={{ 
                                  padding: '12px',
                                  background: 'white',
                                  borderRadius: 'var(--radius-md)',
                                  fontSize: '14px',
                                  lineHeight: 1.6,
                                  color: 'var(--gray-800)',
                                  border: '1px solid var(--gray-200)',
                                }}>
                                  {answer.ai_answer}
                                </div>
                              </div>
                            )}
                            
                            {answer.citations && answer.citations.length > 0 && (
                              <div>
                                <div style={{ 
                                  fontSize: '12px', 
                                  fontWeight: 700,
                                  color: 'var(--gray-700)',
                                  marginBottom: '8px',
                                  textTransform: 'uppercase',
                                  letterSpacing: '0.5px',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '6px',
                                }}>
                                  <span>📎</span>
                                  Citations ({answer.citations.reduce((acc, c) => acc + c.references.length, 0)})
                                </div>
                                <div style={{ 
                                  display: 'flex',
                                  flexDirection: 'column',
                                  gap: '12px',
                                }}>
                                  {answer.citations.map((citation, citIdx) => (
                                    <div key={citIdx}>
                                      {/* Citation Text */}
                                      {citation.text && (
                                        <div style={{
                                          fontSize: '12px',
                                          color: 'var(--gray-700)',
                                          fontStyle: 'italic',
                                          marginBottom: '6px',
                                          padding: '8px',
                                          background: 'white',
                                          borderLeft: '3px solid var(--primary-500)',
                                          borderRadius: 'var(--radius-sm)',
                                        }}>
                                          "{citation.text}"
                                        </div>
                                      )}
                                      {/* References */}
                                      <div style={{ 
                                        display: 'flex',
                                        flexWrap: 'wrap',
                                        gap: '6px',
                                        marginLeft: '12px',
                                      }}>
                                        {citation.references.map((ref, refIdx) => (
                                          <div
                                            key={refIdx}
                                            title={`${ref.document_name}\n${ref.text}`}
                                            style={{
                                              padding: '4px 10px',
                                              background: 'white',
                                              border: '1px solid var(--primary-200)',
                                              borderRadius: 'var(--radius-md)',
                                              fontSize: '11px',
                                              color: 'var(--primary-700)',
                                              fontWeight: 600,
                                              cursor: 'help',
                                              transition: 'all var(--transition-base)',
                                            }}
                                            onMouseEnter={(e) => {
                                              e.currentTarget.style.background = 'var(--primary-50)';
                                              e.currentTarget.style.borderColor = 'var(--primary-500)';
                                            }}
                                            onMouseLeave={(e) => {
                                              e.currentTarget.style.background = 'white';
                                              e.currentTarget.style.borderColor = 'var(--primary-200)';
                                            }}
                                          >
                                            📄 {ref.document_name.split('.')[0].substring(0, 20)}
                                            {ref.page_number ? ` - p.${ref.page_number}` : ''}
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
