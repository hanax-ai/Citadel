
"use client";

import { useState } from "react";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import AgentState from "@/components/AgentState";
import WorkflowProgress from "@/components/WorkflowProgress";
import ConnectionStatus from "@/components/ConnectionStatus";
import { useAgentEvents } from "@/lib/hooks/useAgentEvents";

export default function Home() {
  const [agentState, setAgentState] = useState<any>(null);
  const [workflowProgress, setWorkflowProgress] = useState<any[]>([]);
  
  // Initialize agent events listener with error handling
  const { ConnectionProvider } = useAgentEvents({
    onAgentStateUpdate: (state) => setAgentState(state),
    onWorkflowProgressUpdate: (progress) => {
      if (progress) {
        setWorkflowProgress((prev) => [...prev, progress]);
      }
    },
    onError: (error) => {
      console.error("Agent event error:", error);
      // Error is now handled by the connection status
    }
  });

  return (
    <ConnectionProvider>
      <main className="flex min-h-screen flex-col items-center p-4 md:p-8 lg:p-12">
        <h1 className="text-3xl font-bold mb-4">Project Citadel</h1>
        
        {/* Connection Status Indicator */}
        <div className="w-full max-w-6xl mb-4">
          <ConnectionStatus />
        </div>
        
        <div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Agent State Panel */}
          <div className="md:col-span-1 bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <h2 className="text-xl font-semibold mb-4">Agent State</h2>
            <AgentState state={agentState} />
          </div>
          
          {/* Workflow Progress Panel */}
          <div className="md:col-span-2 bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <h2 className="text-xl font-semibold mb-4">Workflow Progress</h2>
            <WorkflowProgress progress={workflowProgress} />
          </div>
        </div>
        
        {/* CopilotKit Chat Interface */}
        <div className="fixed bottom-4 right-4">
          <CopilotChat
            className="shadow-md"
            placeholder="Ask Project Citadel..."
            messageClassName="prose dark:prose-invert"
          />
        </div>
      </main>
    </ConnectionProvider>
  );
}
