import { useEffect } from 'react';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

interface ToastProps {
  message: string;
  type: ToastType;
  onClose: () => void;
  duration?: number;
}

export default function Toast({ message, type, onClose, duration = 4000 }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const getToastConfig = () => {
    switch (type) {
      case 'success':
        return {
          icon: '✓',
          bgGradient: 'linear-gradient(135deg, var(--success-main), var(--success-dark))',
          bgColor: 'var(--success-light)',
          borderColor: 'var(--success-main)',
        };
      case 'error':
        return {
          icon: '✕',
          bgGradient: 'linear-gradient(135deg, var(--error-main), var(--error-dark))',
          bgColor: 'var(--error-light)',
          borderColor: 'var(--error-main)',
        };
      case 'warning':
        return {
          icon: '⚠',
          bgGradient: 'linear-gradient(135deg, var(--warning-main), var(--warning-dark))',
          bgColor: 'var(--warning-light)',
          borderColor: 'var(--warning-main)',
        };
      case 'info':
        return {
          icon: 'ℹ',
          bgGradient: 'linear-gradient(135deg, var(--primary-600), var(--primary-700))',
          bgColor: 'var(--primary-100)',
          borderColor: 'var(--primary-500)',
        };
    }
  };

  const config = getToastConfig();

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        minWidth: '320px',
        maxWidth: '500px',
        padding: '16px 20px',
        background: 'white',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-xl)',
        border: `2px solid ${config.borderColor}`,
        animation: 'slideIn 0.3s ease-out',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Progress bar */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          height: '4px',
          width: '100%',
          background: config.bgGradient,
          animation: `progressBar ${duration}ms linear`,
        }}
      />

      {/* Icon */}
      <div
        style={{
          width: '36px',
          height: '36px',
          borderRadius: 'var(--radius-full)',
          background: config.bgGradient,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: '18px',
          fontWeight: 'bold',
          flexShrink: 0,
        }}
      >
        {config.icon}
      </div>

      {/* Message */}
      <div style={{ flex: 1, fontSize: '15px', fontWeight: 500, color: 'var(--gray-900)' }}>
        {message}
      </div>

      {/* Close button */}
      <button
        onClick={onClose}
        style={{
          width: '28px',
          height: '28px',
          borderRadius: 'var(--radius-full)',
          background: 'var(--gray-100)',
          border: 'none',
          color: 'var(--gray-600)',
          fontSize: '16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          transition: 'all var(--transition-base)',
          flexShrink: 0,
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = 'var(--gray-200)';
          e.currentTarget.style.color = 'var(--gray-900)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = 'var(--gray-100)';
          e.currentTarget.style.color = 'var(--gray-600)';
        }}
      >
        ✕
      </button>

      <style>{`
        @keyframes progressBar {
          from {
            width: 100%;
          }
          to {
            width: 0%;
          }
        }
      `}</style>
    </div>
  );
}
