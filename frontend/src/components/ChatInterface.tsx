import { useState } from 'react';
import { api } from '../services/api';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  citations?: any[];
  confidence?: number;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          conversation_history: messages
        })
      });

      const data = await response.json();
      
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.answer,
        citations: data.citations,
        confidence: data.confidence_score
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '600px',
      background: 'white',
      borderRadius: 'var(--radius-lg)',
      boxShadow: 'var(--shadow-lg)',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        padding: '20px',
        background: 'linear-gradient(135deg, var(--primary-700), var(--primary-900))',
        color: 'white',
        borderBottom: '1px solid var(--gray-200)'
      }}>
        <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 700 }}>
          💬 Document Chat
        </h3>
        <p style={{ margin: '4px 0 0 0', fontSize: '13px', opacity: 0.9 }}>
          Ask questions about indexed documents
        </p>
      </div>

      {/* Messages */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
      }}>
        {messages.length === 0 && (
          <div style={{
            textAlign: 'center',
            color: 'var(--gray-500)',
            marginTop: '40px'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>💬</div>
            <p>Start a conversation by asking a question</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start'
            }}
          >
            <div style={{
              maxWidth: '70%',
              padding: '12px 16px',
              borderRadius: 'var(--radius-md)',
              background: msg.role === 'user' 
                ? 'linear-gradient(135deg, var(--primary-600), var(--primary-700))'
                : 'var(--gray-100)',
              color: msg.role === 'user' ? 'white' : 'var(--gray-900)',
              fontSize: '14px',
              lineHeight: 1.6
            }}>
              <div>{msg.content}</div>
              
              {msg.confidence !== undefined && (
                <div style={{
                  marginTop: '8px',
                  fontSize: '12px',
                  opacity: 0.8
                }}>
                  Confidence: {(msg.confidence * 100).toFixed(0)}%
                </div>
              )}
              
              {msg.citations && msg.citations.length > 0 && (
                <div style={{
                  marginTop: '8px',
                  fontSize: '12px',
                  opacity: 0.8
                }}>
                  📎 {msg.citations.length} citation(s)
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{
            display: 'flex',
            justifyContent: 'flex-start'
          }}>
            <div style={{
              padding: '12px 16px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--gray-100)',
              color: 'var(--gray-600)',
              fontSize: '14px'
            }}>
              Thinking...
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div style={{
        padding: '20px',
        borderTop: '1px solid var(--gray-200)',
        background: 'var(--gray-50)'
      }}>
        <div style={{ display: 'flex', gap: '12px' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !loading && handleSend()}
            placeholder="Ask a question..."
            disabled={loading}
            style={{
              flex: 1,
              padding: '12px 16px',
              border: '2px solid var(--gray-300)',
              borderRadius: 'var(--radius-md)',
              fontSize: '14px',
              outline: 'none'
            }}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            style={{
              padding: '12px 24px',
              background: 'linear-gradient(135deg, var(--primary-600), var(--primary-700))',
              color: 'white',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              fontSize: '14px',
              fontWeight: 600,
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: (loading || !input.trim()) ? 0.5 : 1
            }}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
