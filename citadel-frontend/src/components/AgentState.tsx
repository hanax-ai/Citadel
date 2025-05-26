
import React from 'react';
import { useConnection } from '@/lib/hooks/useAgentEvents';

interface AgentStateProps {
  state: any | null;
}

const AgentState: React.FC<AgentStateProps> = ({ state }) => {
  const { status: connectionStatus } = useConnection();
  
  // Show connection error message if there's a connection error
  if (connectionStatus === 'error') {
    return (
      <div className="flex flex-col items-center justify-center h-40 bg-gray-100 dark:bg-gray-700 rounded-lg">
        <p className="text-gray-500 dark:text-gray-400">Unable to fetch agent state</p>
        <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">Check your connection to the server</p>
      </div>
    );
  }

  // Show loading state if connecting
  if (connectionStatus === 'connecting' && !state) {
    return (
      <div className="flex items-center justify-center h-40 bg-gray-100 dark:bg-gray-700 rounded-lg">
        <div className="flex items-center space-x-2">
          <svg className="animate-spin h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-gray-500 dark:text-gray-400">Loading agent state...</p>
        </div>
      </div>
    );
  }

  if (!state) {
    return (
      <div className="flex items-center justify-center h-40 bg-gray-100 dark:bg-gray-700 rounded-lg">
        <p className="text-gray-500 dark:text-gray-400">No agent running</p>
      </div>
    );
  }

  const { status, currentStep, metadata, error } = state;

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2">
        <span className="font-medium">Status:</span>
        <span className={`px-2 py-1 rounded-full text-sm ${getStatusColor(status)}`}>
          {status}
        </span>
      </div>

      {currentStep && (
        <div>
          <span className="font-medium">Current Step:</span>
          <p className="mt-1 text-sm">{currentStep}</p>
        </div>
      )}

      {error && (
        <div className="p-3 bg-red-100 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
          <span className="font-medium text-red-800 dark:text-red-400">Error:</span>
          <p className="mt-1 text-sm text-red-700 dark:text-red-300">
            {typeof error === 'object' 
              ? (error.message || JSON.stringify(error)) 
              : String(error)
            }
          </p>
        </div>
      )}

      {metadata && Object.keys(metadata).length > 0 && (
        <div>
          <span className="font-medium">Metadata:</span>
          <pre className="mt-1 p-2 bg-gray-100 dark:bg-gray-700 rounded text-xs overflow-auto max-h-40">
            {JSON.stringify(metadata, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

// Helper function to get status color
function getStatusColor(status: string): string {
  switch (status) {
    case 'idle':
      return 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    case 'running':
      return 'bg-blue-200 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300';
    case 'completed':
      return 'bg-green-200 text-green-800 dark:bg-green-900/30 dark:text-green-300';
    case 'failed':
      return 'bg-red-200 text-red-800 dark:bg-red-900/30 dark:text-red-300';
    default:
      return 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
  }
}

export default AgentState;
