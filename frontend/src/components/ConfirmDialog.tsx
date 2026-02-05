interface ConfirmDialogProps {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
  type?: 'danger' | 'warning' | 'info';
}

export default function ConfirmDialog({
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  onConfirm,
  onCancel,
  type = 'danger',
}: ConfirmDialogProps) {
  const getTypeConfig = () => {
    switch (type) {
      case 'danger':
        return {
          icon: '⚠️',
          confirmBg: 'linear-gradient(135deg, var(--error-main), var(--error-dark))',
          iconBg: 'var(--error-light)',
          iconColor: 'var(--error-dark)',
        };
      case 'warning':
        return {
          icon: '⚠️',
          confirmBg: 'linear-gradient(135deg, var(--warning-main), var(--warning-dark))',
          iconBg: 'var(--warning-light)',
          iconColor: 'var(--warning-dark)',
        };
      case 'info':
        return {
          icon: 'ℹ️',
          confirmBg: 'linear-gradient(135deg, var(--primary-600), var(--primary-700))',
          iconBg: 'var(--primary-100)',
          iconColor: 'var(--primary-700)',
        };
    }
  };

  const config = getTypeConfig();

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onCancel();
    }
  };

  return (
    <div
      onClick={handleBackdropClick}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.6)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        padding: '20px',
        animation: 'fadeIn 0.2s ease-in-out',
      }}
    >
      <div
        style={{
          backgroundColor: 'white',
          borderRadius: 'var(--radius-xl)',
          maxWidth: '450px',
          width: '100%',
          boxShadow: 'var(--shadow-xl)',
          animation: 'fadeIn 0.3s ease-in-out',
          overflow: 'hidden',
        }}
      >
        {/* Icon and Title */}
        <div style={{ padding: '32px 32px 24px 32px', textAlign: 'center' }}>
          <div
            style={{
              width: '64px',
              height: '64px',
              borderRadius: 'var(--radius-full)',
              background: config.iconBg,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 20px auto',
              fontSize: '32px',
            }}
          >
            {config.icon}
          </div>
          <h2
            style={{
              margin: '0 0 12px 0',
              fontSize: '22px',
              fontWeight: 700,
              color: 'var(--gray-900)',
            }}
          >
            {title}
          </h2>
          <p
            style={{
              margin: 0,
              fontSize: '15px',
              color: 'var(--gray-600)',
              lineHeight: 1.6,
            }}
          >
            {message}
          </p>
        </div>

        {/* Actions */}
        <div
          style={{
            padding: '20px 32px',
            background: 'var(--gray-50)',
            borderTop: '1px solid var(--gray-200)',
            display: 'flex',
            gap: '12px',
            justifyContent: 'flex-end',
          }}
        >
          <button
            onClick={onCancel}
            style={{
              padding: '10px 24px',
              border: '2px solid var(--gray-300)',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'white',
              color: 'var(--gray-700)',
              fontWeight: 600,
              fontSize: '15px',
              cursor: 'pointer',
            }}
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            style={{
              padding: '10px 24px',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              background: config.confirmBg,
              color: 'white',
              fontWeight: 600,
              fontSize: '15px',
              cursor: 'pointer',
              boxShadow: 'var(--shadow-md)',
            }}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
