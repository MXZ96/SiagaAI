/**
 * ErrorBoundary - Catch React errors and display fallback UI
 */

import { Component } from 'react';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo
    });
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback({
          error: this.state.error,
          retry: this.handleRetry
        });
      }

      return (
        <div className="min-h-[200px] flex items-center justify-center p-4">
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6 max-w-md w-full">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0">
                <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-red-400 font-semibold">Terjadi Kesalahan</h3>
                <p className="text-red-300/70 text-sm mt-1">
                  {this.props.message || 'Komponen ini mengalami masalah. Silakan coba lagi.'}
                </p>
                <button
                  onClick={this.handleRetry}
                  className="mt-4 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg text-sm font-medium transition-colors"
                >
                  Coba Lagi
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * ErrorMessage - Simple error display component
 */
export function ErrorMessage({ 
  message = 'Terjadi kesalahan', 
  onRetry,
  className = '' 
}) {
  return (
    <div className={`bg-red-500/10 border border-red-500/20 rounded-xl p-4 ${className}`}>
      <div className="flex items-center gap-3">
        <svg className="w-5 h-5 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="text-red-400 text-sm flex-1">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="text-xs text-red-400 hover:text-red-300 underline"
          >
            Coba lagi
          </button>
        )}
      </div>
    </div>
  );
}

/**
 * EmptyState - Display when no data available
 */
export function EmptyState({ 
  icon = '📭',
  title = 'Tidak ada data',
  message = 'Belum ada data untuk ditampilkan',
  action,
  className = '' 
}) {
  return (
    <div className={`flex flex-col items-center justify-center py-8 px-4 ${className}`}>
      <span className="text-4xl mb-3">{icon}</span>
      <h3 className="text-dark-text font-medium">{title}</h3>
      <p className="text-dark-muted text-sm mt-1 text-center max-w-xs">{message}</p>
      {action && (
        <div className="mt-4">
          {action}
        </div>
      )}
    </div>
  );
}
