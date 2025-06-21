import React, { useState, useEffect } from 'react';
import { useNetworkStatus, useConnectionQuality } from '../../hooks/useNetworkStatus';

const NetworkStatusIndicator = () => {
  const { isOnline, connectionType, isSlowConnection } = useNetworkStatus();
  const { quality, latency } = useConnectionQuality();
  const [showIndicator, setShowIndicator] = useState(false);
  const [indicatorType, setIndicatorType] = useState('offline');

  useEffect(() => {
    if (!isOnline) {
      setIndicatorType('offline');
      setShowIndicator(true);
    } else if (isSlowConnection || quality === 'poor') {
      setIndicatorType('slow');
      setShowIndicator(true);
    } else if (quality === 'fair') {
      setIndicatorType('fair');
      setShowIndicator(false); // Don't show for fair connections
    } else {
      setShowIndicator(false);
    }
  }, [isOnline, isSlowConnection, quality]);

  if (!showIndicator) {
    return null;
  }

  const getIndicatorConfig = () => {
    switch (indicatorType) {
      case 'offline':
        return {
          bgColor: 'bg-red-600',
          textColor: 'text-white',
          icon: '📡',
          message: 'Offline - Unele funcții nu sunt disponibile',
          subtitle: 'Verificați conexiunea la internet'
        };
      case 'slow':
        return {
          bgColor: 'bg-yellow-600',
          textColor: 'text-white',
          icon: '🐌',
          message: 'Conexiune lentă detectată',
          subtitle: latency ? `Latență: ${Math.round(latency)}ms` : 'Încărcarea poate fi mai lentă'
        };
      case 'fair':
        return {
          bgColor: 'bg-orange-600',
          textColor: 'text-white',
          icon: '⚠️',
          message: 'Conexiune moderată',
          subtitle: 'Experiența poate fi afectată'
        };
      default:
        return null;
    }
  };

  const config = getIndicatorConfig();
  if (!config) return null;

  return (
    <div 
      className={`${config.bgColor} ${config.textColor} transition-all duration-300 transform`}
      role="alert"
      aria-live="polite"
    >
      <div className="max-w-7xl mx-auto px-4 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-lg" aria-hidden="true">
              {config.icon}
            </span>
            <div className="flex-1">
              <p className="text-sm font-medium">
                {config.message}
              </p>
              {config.subtitle && (
                <p className="text-xs opacity-90">
                  {config.subtitle}
                </p>
              )}
            </div>
          </div>

          {/* Connection details for development */}
          {process.env.NODE_ENV === 'development' && (
            <div className="hidden sm:flex items-center space-x-4 text-xs opacity-75">
              <span>Type: {connectionType}</span>
              <span>Quality: {quality}</span>
              {latency && <span>Latency: {Math.round(latency)}ms</span>}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Compact network status for components
export const CompactNetworkStatus = ({ className = '' }) => {
  const { isOnline, isSlowConnection } = useNetworkStatus();
  const { quality } = useConnectionQuality();

  const getStatusIcon = () => {
    if (!isOnline) {
      return <span className="text-red-500" title="Offline">📡❌</span>;
    } else if (isSlowConnection || quality === 'poor') {
      return <span className="text-yellow-500" title="Conexiune lentă">🐌</span>;
    } else if (quality === 'fair') {
      return <span className="text-orange-500" title="Conexiune moderată">📶</span>;
    } else {
      return <span className="text-green-500" title="Conexiune bună">📶</span>;
    }
  };

  return (
    <div className={`inline-flex items-center ${className}`}>
      {getStatusIcon()}
    </div>
  );
};

export default NetworkStatusIndicator;