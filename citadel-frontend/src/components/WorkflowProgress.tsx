
import React from 'react';
import { useConnection } from '@/lib/hooks/useAgentEvents';

interface WorkflowProgressProps {
  progress: any[];
}

const WorkflowProgress: React.FC<WorkflowProgressProps> = ({ progress }) => {
  const { status: connectionStatus } = useConnection();
  
  // Show connection error message if there's a connection error
  if (connectionStatus === 'error') {
    return (
      <div className="flex flex-col items-center justify-center h-40 bg-gray-100 dark:bg-gray-700 rounded-lg">
        <p className="text-gray-500 dark:text-gray-400">Unable to fetch workflow progress</p>
        <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">Check your connection to the server</p>
      </div>
    );
  }

  // Show loading state if connecting
  if (connectionStatus === 'connecting' && (!progress || progress.length === 0)) {
    return (
      <div className="flex items-center justify-center h-40 bg-gray-100 dark:bg-gray-700 rounded-lg">
        <div className="flex items-center space-x-2">
          <svg className="animate-spin h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-gray-500 dark:text-gray-400">Loading workflow progress...</p>
        </div>
      </div>
    );
  }

  if (!progress || progress.length === 0) {
    return (
      <div className="flex items-center justify-center h-40 bg-gray-100 dark:bg-gray-700 rounded-lg">
        <p className="text-gray-500 dark:text-gray-400">No workflow progress to display</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
      {progress.map((event, index) => (
        <ProgressEvent key={index} event={event} />
      ))}
    </div>
  );
};

interface ProgressEventProps {
  event: any;
}

const ProgressEvent: React.FC<ProgressEventProps> = ({ event }) => {
  if (!event) return null;
  
  const { type, timestamp, data } = event;
  
  // Format timestamp if available
  const formattedTime = timestamp 
    ? new Date(timestamp).toLocaleTimeString() 
    : '';

  return (
    <div className="border-l-4 pl-4 py-2 border-blue-500 dark:border-blue-700">
      <div className="flex justify-between items-start">
        <span className="font-medium text-sm">{getEventTypeLabel(type)}</span>
        {formattedTime && (
          <span className="text-xs text-gray-500 dark:text-gray-400">{formattedTime}</span>
        )}
      </div>
      
      <div className="mt-2">
        {renderEventContent(type, data)}
      </div>
    </div>
  );
};

// Helper function to get a user-friendly label for event types
function getEventTypeLabel(type: string): string {
  if (!type) return 'Unknown Event';
  
  switch (type) {
    case 'message_start':
      return 'Started Message';
    case 'message_content':
      return 'Content Update';
    case 'message_end':
      return 'Completed Message';
    case 'tool_start':
      return 'Tool Execution Started';
    case 'tool_end':
      return 'Tool Execution Completed';
    case 'step_start':
      return 'Step Started';
    case 'step_end':
      return 'Step Completed';
    default:
      return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }
}

// Helper function to render different content based on event type
function renderEventContent(type: string, data: any): React.ReactNode {
  if (!data) return null;

  try {
    switch (type) {
      case 'message_content':
        return (
          <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded">
            <p className="text-sm whitespace-pre-wrap">{data.content}</p>
          </div>
        );
      
      case 'tool_start':
        return (
          <div className="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded border border-yellow-200 dark:border-yellow-800">
            <p className="text-sm font-medium">{data.tool || 'Unknown Tool'}</p>
            {data.input && (
              <pre className="mt-2 text-xs overflow-auto max-h-40">
                {JSON.stringify(data.input, null, 2)}
              </pre>
            )}
          </div>
        );
      
      case 'tool_end':
        return (
          <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded border border-green-200 dark:border-green-800">
            <p className="text-sm font-medium">{data.tool || 'Unknown Tool'} - Result</p>
            {data.output && (
              <pre className="mt-2 text-xs overflow-auto max-h-40">
                {JSON.stringify(data.output, null, 2)}
              </pre>
            )}
          </div>
        );
      
      case 'step_start':
        return (
          <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded">
            <p className="text-sm">{data.name || 'Unknown Step'}</p>
            {data.description && (
              <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">{data.description}</p>
            )}
          </div>
        );
      
      default:
        // For other event types, just show the data as JSON
        return (
          <pre className="bg-gray-100 dark:bg-gray-700 p-2 rounded text-xs overflow-auto max-h-40">
            {JSON.stringify(data, null, 2)}
          </pre>
        );
    }
  } catch (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 p-3 rounded border border-red-200 dark:border-red-800">
        <p className="text-sm text-red-700 dark:text-red-300">Error rendering content: {String(error)}</p>
      </div>
    );
  }
}

export default WorkflowProgress;
