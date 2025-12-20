import React, { useState } from 'react';
import { CheckCircle, AlertCircle, Info, X } from 'lucide-react';

/**
 * Toast Notification Component
 * Shows temporary notifications with different types
 */
const Toast = ({ type = 'info', message = '', onClose, autoClose = true, duration = 3000 }) => {
  const [isVisible, setIsVisible] = useState(true);

  React.useEffect(() => {
    if (autoClose) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        setTimeout(onClose, 300); // Wait for fade out animation
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [autoClose, duration, onClose]);

  const getToastConfig = () => {
    switch (type) {
      case 'success':
        return {
          icon: CheckCircle,
          className: 'toast-success',
          iconColor: 'text-green-400',
        };
      case 'error':
        return {
          icon: AlertCircle,
          className: 'toast-error',
          iconColor: 'text-red-400',
        };
      case 'warning':
        return {
          icon: AlertCircle,
          className: 'toast-warning',
          iconColor: 'text-yellow-400',
        };
      default:
        return {
          icon: Info,
          className: 'toast-info',
          iconColor: 'text-blue-400',
        };
    }
  };

  const config = getToastConfig();
  const Icon = config.icon;

  if (!isVisible) return null;

  return (
    <div
      className={`toast ${config.className} ${
        isVisible ? 'animate-slide-in-right' : 'animate-fade-out'
      }`}
    >
      <div className="flex items-start gap-3">
        <Icon size={20} className={config.iconColor} />
        <div className="flex-1">
          <p className="text-sm text-white">{message}</p>
        </div>
        <button
          onClick={() => {
            setIsVisible(false);
            setTimeout(onClose, 300);
          }}
          className="text-slate-400 hover:text-white transition-colors"
        >
          <X size={16} />
        </button>
      </div>
    </div>
  );
};

/**
 * Toast Container Component
 * Manages multiple toasts
 */
export const ToastContainer = ({ toasts = [], removeToast }) => {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-3">
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          type={toast.type}
          message={toast.message}
          onClose={() => removeToast(toast.id)}
          autoClose={toast.autoClose !== false}
          duration={toast.duration || 3000}
        />
      ))}
    </div>
  );
};

/**
 * Hook to manage toasts
 */
export const useToast = () => {
  const [toasts, setToasts] = useState([]);

  const addToast = (type, message, options = {}) => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [
      ...prev,
      {
        id,
        type,
        message,
        ...options,
      },
    ]);
  };

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };

  return {
    toasts,
    addToast,
    removeToast,
    success: (message, options) => addToast('success', message, options),
    error: (message, options) => addToast('error', message, options),
    warning: (message, options) => addToast('warning', message, options),
    info: (message, options) => addToast('info', message, options),
  };
};

export default Toast;
