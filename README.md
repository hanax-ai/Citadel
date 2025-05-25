# Citadel

Citadel is a comprehensive AI agent framework that integrates advanced technologies for building, orchestrating, and deploying intelligent agents with sophisticated user interfaces. The project combines LangGraph for agent orchestration, LangChain for LLM integration, AG-UI for standardized agent-UI communication, and CopilotKit for frontend components.

## Overview

Citadel provides a complete stack for developing AI agent applications with the following key features:

- **Agent Orchestration**: Complex, stateful agent workflows using LangGraph
- **LLM Integration**: Powerful language model capabilities via LangChain
- **Standardized Communication**: Event-driven protocol between agents and UI via AG-UI
- **Modern Frontend**: React components and hooks for AI interfaces via CopilotKit
- **Document Processing**: Advanced PDF processing with text extraction, metadata, and OCR
- **Web Crawling**: Specialized crawlers for websites and PDF documents

## Project Architecture

Citadel follows a modular architecture with several key components:

```
Citadel/
├── citadel-frontend/       # React/Next.js frontend with CopilotKit
├── citadel_api/            # FastAPI backend for agent endpoints
├── citadel_core/           # Core utilities, crawlers, and PDF processing
├── citadel_frontend/       # Protocol layer for frontend integration
├── citadel_lang/           # Language model abstractions
├── citadel_langchain/      # LangChain extensions and components
├── citadel_langgraph/      # LangGraph workflows and agent orchestration
├── citadel_llm/            # LLM integration, classifiers, and processors
├── docs/                   # Documentation and architecture diagrams
├── examples/               # Example applications and demos
├── scripts/                # Utility scripts and demos
└── tests/                  # Test suite for all components
```

### Key Components

#### AG-UI Protocol Layer

The AG-UI (Agent User Interaction Protocol) serves as the standardized communication layer between AI backend agents and frontend applications:

- Lightweight, event-driven architecture for agent-UI communication
- 16 standardized event types for message streaming, tool calls, state updates, and lifecycle signals
- Transport-agnostic design supporting HTTP SSE, WebSockets, and other mechanisms
- Efficient state synchronization through snapshots and deltas

#### LangGraph Enhancements

Citadel extends LangGraph's capabilities for complex agent workflows:

- Custom nodes for specialized agent behaviors
- Enhanced state management for persistent agent memory
- Coordination mechanisms for multi-agent systems
- Event-driven feedback loops for continuous improvement
- Workflow templates for common agent patterns

#### Integration Layer

The integration layer connects all components into a cohesive system:

- Standardized API contracts between components
- Event transformation and routing
- State synchronization between backend and frontend
- Tool registration and execution framework
- Observability and tracing capabilities

#### CopilotKit Frontend

The frontend leverages CopilotKit for AI-powered user interfaces:

- Pre-built React components for chat interfaces and sidebars
- Hooks for state management and agent actions
- Real-time updates via AG-UI events
- Multi-agent orchestration through CoAgents framework

## Installation

### Prerequisites

- Python 3.9+
- Node.js 18+
- Git

### Backend Installation

```bash
# Clone the repository
git clone https://github.com/hanax-ai/Citadel.git
cd Citadel

# Install the Python package and dependencies
pip install -e .

# Install optional OCR dependencies
pip install -e ".[ocr]"

# Install development dependencies
pip install -e ".[dev]"
```

### Frontend Installation

```bash
# Navigate to the frontend directory
cd citadel-frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

## Usage

### Starting the Backend

```bash
# Start the FastAPI backend
cd /path/to/Citadel
python -m citadel_api.main
```

The API will be available at http://localhost:8000 with documentation at http://localhost:8000/docs.

### Starting the Frontend

```bash
# Start the Next.js development server
cd /path/to/Citadel/citadel-frontend
npm run dev
```

The frontend will be available at http://localhost:3000.

### Running Examples

```bash
# Run the full demo
python examples/full_demo.py

# Run the PDF processing demo
python scripts/pdf_demo.py --pdf path/to/document.pdf --ocr
```

## Core Features

### PDF Processing

Citadel includes comprehensive PDF processing capabilities:

- Text extraction from PDF documents
- Metadata extraction (author, title, creation date, etc.)
- Document structure identification (headings, paragraphs, tables)
- Image processing with OCR (when enabled)
- Content chunking for LLM integration

Example:

```python
from citadel_core.pdf_processing import PDFProcessor

# Create a PDF processor
processor = PDFProcessor(ocr_enabled=True, language='eng')

# Process a PDF
result = processor.process_pdf('path/to/document.pdf')

# Access the extracted information
print(f"Text: {result['text'][:100]}...")
print(f"Metadata: {result['metadata']}")
```

### Web Crawling

Citadel provides specialized crawlers for different content types:

- Base crawler with common functionality
- Academic crawler for research papers
- News crawler for news articles
- PDF crawler for PDF documents

Example:

```python
from citadel_core.crawlers.pdf_crawler import PDFCrawler

# Create a PDF crawler
crawler = PDFCrawler(
    base_url="https://example.com",
    ocr_enabled=True,
    language='eng',
    chunk_size=1000,
    chunk_overlap=100
)

# Crawl PDFs from URLs
results = crawler.crawl([
    "https://example.com/document1.pdf",
    "https://example.com/document2.pdf"
])
```

### Agent Orchestration

Citadel uses LangGraph for complex agent workflows:

```python
from citadel_langgraph.workflows import build_workflow
from citadel_langgraph.agents import ResearchAgent, WritingAgent

# Create a research workflow
workflow = build_workflow(
    agents=[ResearchAgent(), WritingAgent()],
    tools=["web_search", "document_retrieval"],
    memory_type="conversation"
)

# Run the workflow
result = workflow.invoke({
    "task": "Research the impact of AI on healthcare",
    "output_format": "report"
})
```

### Frontend Integration

The frontend uses CopilotKit components for AI interfaces:

```tsx
import { CopilotChat, CopilotSidebar } from '@copilotkit/react-ui';
import { useCopilotAction } from '@copilotkit/react-core';

function CitadelDashboard() {
  // Register actions that the copilot can perform
  const executeSearch = useCopilotAction({
    name: "search",
    description: "Search for information in the system",
    parameters: [
      { name: "query", type: "string", description: "Search query" }
    ],
    handler: async ({ query }) => {
      // Implementation details
      return searchResults;
    }
  });
  
  return (
    <div className="dashboard-container">
      <CopilotSidebar>
        <CopilotChat
          className="citadel-chat"
          placeholder="Ask Citadel anything..."
        />
      </CopilotSidebar>
      
      <main className="dashboard-content">
        {/* Dashboard content */}
      </main>
    </div>
  );
}
```

## Development

### Running Tests

```bash
# Run all tests
python -m unittest discover -s tests

# Run specific test modules
python -m unittest tests.test_pdf_processing
python -m unittest tests.test_langgraph
```

### Code Style

This project follows PEP 8 style guidelines. Use `black` and `isort` to format your code:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Format code
black citadel_core/ citadel_api/ citadel_langgraph/
isort citadel_core/ citadel_api/ citadel_langgraph/
```

## Project Structure Details

### Backend Components

- **citadel_core**: Core utilities, crawlers, and PDF processing
  - `crawlers/`: Web crawlers for different content types
  - `pdf_processing.py`: PDF processing utilities
  - `utils.py`: Common utility functions

- **citadel_api**: FastAPI backend for agent endpoints
  - `main.py`: API entry point
  - `routes/`: API route definitions
  - `models/`: Pydantic models for API requests/responses

- **citadel_langchain**: LangChain extensions and components
  - `chains/`: Custom LangChain chains
  - `loaders/`: Document loaders
  - `splitters/`: Text splitters
  - `vectorstores/`: Vector database integrations
  - `retrievers/`: Custom retrievers

- **citadel_langgraph**: LangGraph workflows and agent orchestration
  - `agents/`: Agent definitions
  - `coordination/`: Multi-agent coordination
  - `nodes/`: Custom graph nodes
  - `state/`: State management
  - `tools/`: Tool definitions
  - `workflows/`: Workflow templates

- **citadel_llm**: LLM integration and processing
  - `classifiers/`: Text classification utilities
  - `extractors/`: Information extraction utilities
  - `processors/`: Text processing utilities
  - `summarizers/`: Text summarization utilities
  - `gateway.py`: LLM provider gateway

### Frontend Components

- **citadel-frontend**: Next.js frontend with CopilotKit
  - `src/app/`: Next.js app router pages
  - `src/components/`: React components
  - `src/lib/`: Utility functions and hooks

- **citadel_frontend**: Protocol layer for frontend integration
  - `protocol/`: AG-UI protocol implementation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
