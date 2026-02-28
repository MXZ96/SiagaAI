/**
 * LoadingSpinner - Reusable loading indicator
 */

export default function LoadingSpinner({ size = 'md', text = 'Memuat...' }) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16'
  };

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className={`animate-spin rounded-full border-2 border-gray-300 border-t-primary-500 ${sizeClasses[size]}`}></div>
      {text && <p className="text-gray-500 mt-2 text-sm">{text}</p>}
    </div>
  );
}

/**
 * LoadingOverlay - Full screen loading
 */
export function LoadingOverlay({ isLoading, text = 'Memuat...' }) {
  if (!isLoading) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="bg-dark-card rounded-2xl p-8 flex flex-col items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-gray-600 border-t-primary-500"></div>
        <p className="text-dark-text mt-4 font-medium">{text}</p>
      </div>
    </div>
  );
}

/**
 * PageLoader - Full page loading state
 */
export function PageLoader({ text = 'Memuat halaman...' }) {
  return (
    <div className="min-h-screen bg-dark-bg flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-gray-600 border-t-primary-500 mx-auto mb-4"></div>
        <p className="text-dark-muted text-lg">{text}</p>
      </div>
    </div>
  );
}
