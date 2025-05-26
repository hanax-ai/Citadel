
import React from 'react';
import { useConnection, ConnectionStatus } from '@/lib/hooks/useAgentEvents';

interface ConnectionStatusProps {
  className?: string;
}

const ConnectionStatusComponent: React.FC<ConnectionStatusProps> = ({ className = '' }) => {
  const { status, error, reconnect } = useConnection();

  const getStatusColor = (status: ConnectionStatus): string => {
    switch (status) {
      case 'connected':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 border-green-300 dark:border-green-800';
      case 'connecting':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300 border-yellow-300 dark:border-yellow-800';
      case 'disconnected':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600';
      case 'error':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300 border-red-300 dark:border-red-800';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600';
    }
  };

  const getStatusIcon = (status: ConnectionStatus): React.ReactNode => {
    switch (status) {
      case 'connected':
        return (
          <svg className="w-4 h-4 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
          </svg>
        );
      case 'connecting':
        return (
          <svg className="w-4 h-4 text-yellow-600 dark:text-yellow-400 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        );
      case 'disconnected':
        return (
          <svg className="w-4 h-4 text-gray-600 dark:text-gray-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd"></path>
          </svg>
        );
      case 'error':
        return (
          <svg className="w-4 h-4 text-red-600 dark:text-red-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path>
          </svg>
        );
      default:
        return null;
    }
  };

  const getStatusText = (status: ConnectionStatus): string => {
    switch (status) {
      case 'connected':
        return 'Connected to server';
      case 'connecting':
        return 'Connecting to server...';
      case 'disconnected':
        return 'Disconnected from server';
      case 'error':
        return 'Connection error';
      default:
        return 'Unknown status';
    }
  };

  return (
    <div className={`flex flex-col ${className}`}>
      <div className={`flex items-center space-x-2 p-2 rounded-md border ${getStatusColor(status)}`}>
        <span>{getStatusIcon(status)}</span>
        <span className="text-sm font-medium">{getStatusText(status)}</span>
        
        {status === 'error' && (
          <button 
            onClick={reconnect}
            className="ml-auto text-xs bg-blue-500 hover:bg-blue-600 text-white py-1 px-2 rounded transition-colors"
          >
            Reconnect
          </button>
        )}
      </div>
      
      {status === 'error' && error && (
        <div className="mt-2 p-2 text-xs bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md text-red-700 dark:text-red-300">
          {error}
        </div>
      )}
    </div>
  );
};

export default ConnectionStatusComponent;
