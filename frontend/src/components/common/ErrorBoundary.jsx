import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null,
      errorInfo: null,
      errorId: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { 
      hasError: true,
      errorId: Date.now().toString()
    };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // Log error to monitoring service
    this.logErrorToService(error, errorInfo);
  }

  logErrorToService = (error, errorInfo) => {
    const errorData = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      errorId: this.state.errorId
    };

    console.error('Error logged:', errorData);
    
    // In production, send to error tracking service
    if (process.env.NODE_ENV === 'production') {
      // Example: Send to error tracking service
      // errorTrackingService.logError(errorData);
    }
  };

  handleRetry = () => {
    this.setState({ 
      hasError: false, 
      error: null, 
      errorInfo: null,
      errorId: null
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
            {/* Error Icon */}
            <div className="flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.864-.833-2.634 0L4.18 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>

            {/* Error Message */}
            <div className="text-center">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                A apărut o eroare neașteptată
              </h2>
              
              <p className="text-gray-600 mb-6">
                Ne pare rău, dar ceva nu a mers bine. Încercați să reîmprospătați pagina 
                sau contactați suportul dacă problema persistă.
              </p>

              {/* Error ID for support */}
              {this.state.errorId && (
                <div className="bg-gray-100 rounded-lg p-3 mb-6">
                  <p className="text-xs text-gray-500 mb-1">ID Eroare pentru suport:</p>
                  <p className="text-sm font-mono text-gray-700">{this.state.errorId}</p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="space-y-3">
                <button
                  onClick={this.handleRetry}
                  className="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-green-700 transition-colors min-h-[44px] flex items-center justify-center"
                >
                  🔄 Încercați din nou
                </button>
                
                <button
                  onClick={this.handleReload}
                  className="w-full border border-gray-300 text-gray-700 py-3 px-4 rounded-lg font-medium hover:bg-gray-50 transition-colors min-h-[44px] flex items-center justify-center"
                >
                  ↻ Reîmprospătați pagina
                </button>
              </div>

              {/* Contact Support */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <p className="text-sm text-gray-500 mb-3">
                  Aveți nevoie de ajutor?
                </p>
                <div className="flex flex-col space-y-2 text-sm">
                  <div className="flex items-center justify-center space-x-2 text-gray-600">
                    <span>📧</span>
                    <span>suport@pefocdelemne.ro</span>
                  </div>
                  <div className="flex items-center justify-center space-x-2 text-gray-600">
                    <span>📞</span>
                    <span>0700 123 456</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Development Error Details */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-6 p-4 bg-gray-100 rounded-lg">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 mb-2">
                  Detalii tehnice (doar în development)
                </summary>
                <div className="text-xs text-gray-600 space-y-2">
                  <div>
                    <strong>Eroare:</strong>
                    <pre className="mt-1 whitespace-pre-wrap">{this.state.error.message}</pre>
                  </div>
                  <div>
                    <strong>Stack:</strong>
                    <pre className="mt-1 whitespace-pre-wrap text-xs">{this.state.error.stack}</pre>
                  </div>
                  {this.state.errorInfo && (
                    <div>
                      <strong>Component Stack:</strong>
                      <pre className="mt-1 whitespace-pre-wrap text-xs">{this.state.errorInfo.componentStack}</pre>
                    </div>
                  )}
                </div>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Higher-order component for wrapping components with error boundary
export const withErrorBoundary = (Component, fallback = null) => {
  return function WrappedComponent(props) {
    return (
      <ErrorBoundary fallback={fallback}>
        <Component {...props} />
      </ErrorBoundary>
    );
  };
};

// Lightweight error boundary for specific sections
export const SectionErrorBoundary = ({ children, title = "Această secțiune" }) => {
  return (
    <ErrorBoundary
      fallback={
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-red-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.864-.833-2.634 0L4.18 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <div>
              <h4 className="text-sm font-medium text-red-800">
                {title} nu poate fi afișată
              </h4>
              <p className="text-sm text-red-700 mt-1">
                A apărut o eroare neașteptată. Reîmprospătați pagina pentru a încerca din nou.
              </p>
            </div>
          </div>
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  );
};

export default ErrorBoundary;