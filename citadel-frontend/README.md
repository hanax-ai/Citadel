# Project Citadel Frontend

This is a minimal Next.js frontend with CopilotKit integration for Project Citadel. The frontend communicates with the backend API and provides a user interface for interacting with AI agents and workflows.

## Features

- TypeScript and React-based implementation
- CopilotKit integration for AI assistance
- API clients for communicating with the backend
- Real-time updates using AG-UI protocol events
- Simple chat interface for interacting with agents
- Display of agent state and workflow progress

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Clone the repository
2. Install dependencies:

```bash
npm install
```

3. Configure the environment variables:

Create a `.env.local` file in the root directory with the following content:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Replace the URL with your backend API URL if different.

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Project Structure

- `src/app`: Next.js app router pages
- `src/components`: React components for UI elements
- `src/lib`: Utility functions, API clients, and hooks
  - `src/lib/api.ts`: API client for backend communication
  - `src/lib/hooks`: Custom React hooks

## Backend Integration

The frontend integrates with the Project Citadel backend API, which is implemented using FastAPI. The API provides endpoints for agent and graph workflows, with event streaming for real-time updates.

### API Endpoints

- `/agents/start`: Start a new agent with a task
- `/agents/{agentId}/state`: Get the current state of an agent
- `/agents/{agentId}/stop`: Stop a running agent
- `/agents/{agentId}/events`: SSE endpoint for agent events
- `/workflows/start`: Start a new workflow
- `/workflows/{workflowId}/progress`: Get the progress of a workflow
- `/events`: Global SSE endpoint for all events

### Event Types

The frontend handles the following AG-UI protocol events:

- `run_started`: When an agent run starts
- `text_message_start`: When a text message starts
- `text_message_content`: Content updates for a text message
- `text_message_end`: When a text message ends
- `run_finished`: When an agent run finishes
- `error`: When an error occurs

## License

[MIT](LICENSE)
