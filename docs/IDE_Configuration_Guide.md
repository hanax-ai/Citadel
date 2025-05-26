# Project Citadel IDE Configuration Guide

## Overview

This document provides recommended IDE configurations for Project Citadel development. Based on the project's architecture and technology stack, these configurations will optimize the development experience and ensure consistency across the team.

## Supported IDEs

The following IDEs are recommended for Project Citadel development:

1. **Visual Studio Code** (Primary recommendation)
2. **PyCharm Professional** (Alternative for Python-focused development)
3. **WebStorm** (Alternative for JavaScript/React development)

## Visual Studio Code Configuration

### Required Extensions

| Extension | Purpose | Configuration Notes |
|-----------|---------|---------------------|
| Python | Python language support | Configure with Python 3.10+ interpreter |
| Pylance | Python type checking and IntelliSense | Enable strict type checking |
| ESLint | JavaScript/TypeScript linting | Use project's ESLint configuration |
| Prettier | Code formatting | Use project's Prettier configuration |
| Tailwind CSS IntelliSense | Tailwind CSS support | Required for UI development |
| React Developer Tools | React debugging | For CopilotKit integration work |
| REST Client | API testing | For testing FastAPI endpoints |
| Markdown All in One | Markdown support | For documentation |
| Mermaid Preview | Diagram visualization | For architecture diagrams |
| Docker | Container management | For development containers |
| Kubernetes | Kubernetes integration | For deployment configuration |
| GitLens | Git integration | For version control |
| Live Share | Collaborative editing | For pair programming |

### settings.json Configuration

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.pylintArgs": [
    "--disable=C0111"
  ],
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": [
    "--line-length=88"
  ],
  "python.analysis.typeCheckingMode": "strict",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true,
    "source.fixAll.eslint": true
  },
  "editor.rulers": [88, 100],
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/.coverage": true,
    "**/*.pyc": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/.venv": true
  },
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[javascript]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescript]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[json]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[markdown]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "javascript.updateImportsOnFileMove.enabled": "always",
  "typescript.updateImportsOnFileMove.enabled": "always"
}
```

### launch.json Configuration

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": false
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": false
    },
    {
      "name": "Next.js: debug server-side",
      "type": "node-terminal",
      "request": "launch",
      "command": "npm run dev"
    },
    {
      "name": "Next.js: debug client-side",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000"
    },
    {
      "name": "Next.js: debug full stack",
      "type": "node-terminal",
      "request": "launch",
      "command": "npm run dev",
      "serverReadyAction": {
        "pattern": "started server on .+, url: (https?://.+)",
        "uriFormat": "%s",
        "action": "debugWithChrome"
      }
    }
  ]
}
```

### tasks.json Configuration

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Install Python Dependencies",
      "type": "shell",
      "command": "${workspaceFolder}/.venv/bin/pip install -r requirements.txt",
      "problemMatcher": []
    },
    {
      "label": "Install Node Dependencies",
      "type": "shell",
      "command": "npm install",
      "options": {
        "cwd": "${workspaceFolder}/frontend"
      },
      "problemMatcher": []
    },
    {
      "label": "Run Python Tests",
      "type": "shell",
      "command": "${workspaceFolder}/.venv/bin/pytest",
      "group": {
        "kind": "test",
        "isDefault": true
      },
      "problemMatcher": []
    },
    {
      "label": "Run JavaScript Tests",
      "type": "shell",
      "command": "npm test",
      "options": {
        "cwd": "${workspaceFolder}/frontend"
      },
      "group": "test",
      "problemMatcher": []
    },
    {
      "label": "Start Development Environment",
      "dependsOrder": "sequence",
      "dependsOn": [
        "Install Python Dependencies",
        "Install Node Dependencies"
      ],
      "problemMatcher": []
    }
  ]
}
```

## PyCharm Professional Configuration

### Required Plugins

| Plugin | Purpose |
|--------|---------|
| Pylint | Code linting |
| Black | Code formatting |
| Mypy | Type checking |
| JavaScript and TypeScript | JavaScript/TypeScript support |
| React | React support |
| Docker | Container management |
| Kubernetes | Kubernetes integration |
| Markdown | Markdown support |
| PlantUML | Diagram visualization |

### Project Settings

1. **Python Interpreter**: Configure a virtual environment with Python 3.10+
2. **Project Structure**: Mark directories appropriately (Sources, Tests, Resources)
3. **Code Style**:
   - Python: Use Black formatter with line length 88
   - JavaScript/TypeScript: Use Prettier
4. **Inspections**:
   - Enable Pylint
   - Enable Mypy type checking
   - Enable ESLint for JavaScript/TypeScript
5. **Run Configurations**:
   - FastAPI: `uvicorn app.main:app --reload --port 8000`
   - Next.js: `npm run dev` in the frontend directory
   - Tests: Configure pytest for Python tests and Jest for JavaScript tests

## WebStorm Configuration (for Frontend Development)

### Required Plugins

| Plugin | Purpose |
|--------|---------|
| ESLint | JavaScript/TypeScript linting |
| Prettier | Code formatting |
| Tailwind CSS | Tailwind CSS support |
| React | React support |
| CopilotKit | CopilotKit integration |

### Project Settings

1. **Node.js**: Configure with the project's Node.js version
2. **Code Style**:
   - JavaScript/TypeScript: Use Prettier with project configuration
3. **Inspections**:
   - Enable ESLint
4. **Run Configurations**:
   - Next.js: `npm run dev`
   - Tests: `npm test`
   - Build: `npm run build`

## Project-Specific Configuration Files

### .editorconfig

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space

[*.{py,pyi}]
indent_size = 4
max_line_length = 88

[*.{js,jsx,ts,tsx,json,yml,yaml,html,css,md}]
indent_size = 2
max_line_length = 100
```

### pyproject.toml

```toml
[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[tool.pylint.messages_control]
disable = "C0111"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
```

### .eslintrc.js

```javascript
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
    'next/core-web-vitals',
    'prettier'
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaFeatures: {
      jsx: true
    },
    ecmaVersion: 2021,
    sourceType: 'module'
  },
  plugins: ['react', '@typescript-eslint', 'react-hooks'],
  rules: {
    'react/react-in-jsx-scope': 'off',
    'react/prop-types': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-explicit-any': 'warn',
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn'
  },
  settings: {
    react: {
      version: 'detect'
    }
  }
};
```

### .prettierrc

```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "bracketSpacing": true,
  "arrowParens": "avoid"
}
```

## Language Server Protocol (LSP) Configuration

For editors that support LSP, configure the following language servers:

1. **Python**: Pylance or Pyright
   - Enable strict type checking
   - Configure with Python 3.10+

2. **JavaScript/TypeScript**: TypeScript Language Server
   - Enable strict type checking
   - Configure with project's tsconfig.json

3. **JSON**: JSON Language Server
   - Enable schema validation

4. **YAML**: YAML Language Server
   - Enable schema validation for Kubernetes resources

## Development Container Configuration

For consistent development environments, use the following Dev Container configuration:

### .devcontainer/devcontainer.json

```json
{
  "name": "Project Citadel Development",
  "dockerComposeFile": "docker-compose.yml",
  "service": "app",
  "workspaceFolder": "/workspace",
  "settings": {
    "python.defaultInterpreterPath": "/usr/local/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "python.analysis.typeCheckingMode": "strict",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true,
      "source.fixAll.eslint": true
    }
  },
  "extensions": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "ms-azuretools.vscode-docker",
    "ms-kubernetes-tools.vscode-kubernetes-tools",
    "eamodio.gitlens",
    "yzhang.markdown-all-in-one",
    "bierner.markdown-mermaid"
  ],
  "forwardPorts": [8000, 3000],
  "postCreateCommand": "pip install -r requirements.txt && cd frontend && npm install",
  "remoteUser": "vscode"
}
```

### .devcontainer/docker-compose.yml

```yaml
version: '3'
services:
  app:
    build:
      context: ..
      dockerfile: .devcontainer/Dockerfile
    volumes:
      - ..:/workspace:cached
    command: sleep infinity
    environment:
      - PYTHONPATH=/workspace
    networks:
      - citadel-network
    depends_on:
      - postgres
      - redis
      - qdrant

  postgres:
    image: postgres:15
    restart: unless-stopped
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_USER: postgres
      POSTGRES_DB: citadel
    networks:
      - citadel-network

  redis:
    image: redis:7
    restart: unless-stopped
    volumes:
      - redis-data:/data
    networks:
      - citadel-network

  qdrant:
    image: qdrant/qdrant:v1.6.1
    restart: unless-stopped
    volumes:
      - qdrant-data:/qdrant/storage
    networks:
      - citadel-network

networks:
  citadel-network:

volumes:
  postgres-data:
  redis-data:
  qdrant-data:
```

### .devcontainer/Dockerfile

```dockerfile
FROM python:3.10-bullseye

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get update \
    && apt-get install -y nodejs \
    && apt-get clean -y

# Install development tools
RUN apt-get update \
    && apt-get install -y git curl wget build-essential \
    && apt-get clean -y

# Install Python development tools
RUN pip install --no-cache-dir black pylint mypy pytest

# Create a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Set the working directory
WORKDIR /workspace

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set the default user
USER $USERNAME
```

## Debugging Configuration

### Python Debugging

1. **FastAPI Debugging**:
   - Use the provided launch configuration for FastAPI
   - Set breakpoints in API routes and middleware

2. **LangChain/LangGraph Debugging**:
   - Use the Python debugger with `justMyCode: false` to step into library code
   - Set breakpoints in chain definitions and graph nodes

3. **Crawler Agent Debugging**:
   - Use the Python debugger with appropriate environment variables
   - Set breakpoints in crawler implementation code

### JavaScript/TypeScript Debugging

1. **Next.js Debugging**:
   - Use the provided launch configurations for Next.js
   - Set breakpoints in React components and hooks

2. **CopilotKit Debugging**:
   - Use browser developer tools for frontend debugging
   - Set breakpoints in CopilotKit integration code

3. **AG-UI Protocol Debugging**:
   - Use network monitoring in browser developer tools
   - Set breakpoints in protocol handler code

## MCP (Multi-Cursor Programming) Servers

### What are MCP Servers?

MCP (Multi-Cursor Programming) servers enable real-time collaborative coding by allowing multiple developers to work simultaneously on the same codebase. They facilitate shared cursors, synchronized file navigation, and terminal sharing across different IDE instances. MCP servers are particularly valuable for Project Citadel's distributed development team, enabling:

- Real-time collaborative editing
- Shared terminal sessions
- Synchronized file navigation
- Integrated AI assistance
- Tool-specific functionalities (web scraping, document analysis, design integration)

### Recommended MCP Server Options

For Project Citadel development, we recommend the following MCP server options:

| Server Option | Features | Best For |
|---------------|----------|----------|
| Cursor Live Share | Built-in collaborative editing, terminal sharing, chat | General collaborative coding |
| Custom MCP Server | Tailored to Project Citadel's specific needs | Advanced integration with project-specific tools |
| VSCode Live Share | Microsoft's collaborative coding solution | Teams primarily using VSCode |

### Installation and Configuration

#### Cursor Live Share Setup

1. **Installation**:
   - Install Cursor IDE from [cursor.sh](https://cursor.sh)
   - Enable Live Share in settings

2. **Configuration**:
   ```json
   // settings.json addition for Cursor
   {
     "liveshare.features.enabled": true,
     "liveshare.connection.mode": "direct",
     "liveshare.presence.enabled": true
   }
   ```

3. **Usage**:
   - Start a session: `Ctrl+Shift+P` > `Live Share: Start Session`
   - Join a session: `Ctrl+Shift+P` > `Live Share: Join Session`
   - Share the generated link with collaborators

#### Custom MCP Server Setup

For Project Citadel's specific needs, a custom MCP server can be deployed:

1. **Server Installation**:
   ```bash
   # Clone the MCP server repository
   git clone https://github.com/project-citadel/mcp-server.git
   cd mcp-server
   
   # Install dependencies
   npm install
   
   # Configure environment
   cp .env.example .env
   # Edit .env with appropriate settings
   
   # Start the server
   npm start
   ```

2. **Client Configuration**:
   ```json
   // settings.json addition for custom MCP
   {
     "mcp.server.url": "wss://mcp.project-citadel.com",
     "mcp.server.token": "${env:MCP_TOKEN}",
     "mcp.features.enabled": true,
     "mcp.synchronization.files": true,
     "mcp.synchronization.terminals": true
   }
   ```

3. **Security Considerations**:
   - Use secure WebSocket connections (WSS)
   - Implement token-based authentication
   - Limit shared permissions based on user roles
   - Monitor participant activity
   - End sessions properly to prevent unauthorized access

### Integration with Recommended IDEs

#### Visual Studio Code Integration

1. **Extensions**:
   - Install the MCP Client extension
   - Configure the extension with server details

2. **Configuration**:
   ```json
   // VSCode settings.json addition
   {
     "mcp.server.url": "wss://mcp.project-citadel.com",
     "mcp.server.token": "${env:MCP_TOKEN}",
     "mcp.synchronization.mode": "full",
     "mcp.presence.indicators": true
   }
   ```

3. **Commands**:
   - `Ctrl+Shift+P` > `MCP: Connect to Server`
   - `Ctrl+Shift+P` > `MCP: Start Collaboration Session`
   - `Ctrl+Shift+P` > `MCP: Join Collaboration Session`

#### PyCharm Integration

1. **Plugins**:
   - Install the "Code With Me" plugin
   - Configure with custom MCP server settings

2. **Configuration**:
   - Open Settings > Tools > Code With Me
   - Set custom server URL
   - Configure authentication settings

3. **Usage**:
   - Tools > Code With Me > Start Session
   - Share the generated link with collaborators

#### WebStorm Integration

Similar to PyCharm, use the "Code With Me" plugin with appropriate configuration for the custom MCP server.

### Advanced Features

1. **AI Integration**:
   - Connect AI assistants to the MCP server for shared AI suggestions
   - Configure AI tools for specific workflows (web scraping, document analysis)

2. **Custom Tool Development**:
   - Develop project-specific tools that integrate with the MCP server
   - Create specialized extensions for Project Citadel's unique requirements

3. **Session Recording and Playback**:
   - Record collaborative sessions for later review
   - Use session playback for training and onboarding

## Brave Browser Configuration for Web Searches

### Installation and Setup

Brave Browser provides enhanced privacy features that are valuable for Project Citadel development, particularly when researching sensitive topics or accessing development resources.

1. **Installation**:
   - Download Brave Browser from [brave.com](https://brave.com)
   - Install following the platform-specific instructions
   - Import settings and bookmarks if migrating from another browser

2. **Initial Configuration**:
   ```bash
   # Linux installation (Ubuntu/Debian)
   sudo apt install apt-transport-https curl
   curl -s https://brave-browser-apt-release.s3.brave.com/brave-core.asc | sudo apt-key add -
   echo "deb [arch=amd64] https://brave-browser-apt-release.s3.brave.com/ stable main" | sudo tee /etc/apt/sources.list.d/brave-browser-release.list
   sudo apt update
   sudo apt install brave-browser
   ```

3. **Basic Setup**:
   - Launch Brave Browser
   - Navigate to Settings (`brave://settings/`)
   - Configure sync if working across multiple devices
   - Set as default browser for development work

### Developer-Focused Search Engines Configuration

Configure Brave to use privacy-respecting search engines that are optimized for development queries:

1. **Adding Custom Search Engines**:
   - Navigate to Settings > Search engine
   - Click "Manage search engines and site search"
   - Add the following search engines:

   | Search Engine | Keyword | URL Template |
   |---------------|---------|------------|
   | Brave Search | brave | `https://search.brave.com/search?q=%s` |
   | DuckDuckGo | ddg | `https://duckduckgo.com/?q=%s` |
   | Stack Overflow | so | `https://stackoverflow.com/search?q=%s` |
   | GitHub | gh | `https://github.com/search?q=%s` |
   | MDN Web Docs | mdn | `https://developer.mozilla.org/en-US/search?q=%s` |
   | Python Docs | py | `https://docs.python.org/3/search.html?q=%s` |
   | npm | npm | `https://www.npmjs.com/search?q=%s` |

2. **Setting Default Search Engine**:
   - Set Brave Search as the default search engine
   - Configure keyboard shortcuts for quick access to specialized search engines

3. **Search Engine Usage**:
   - Type the keyword followed by a space in the address bar
   - Enter your search query
   - Example: `so python asyncio error handling` to search Stack Overflow

### Privacy Settings Optimized for Development

Configure Brave's privacy settings to balance security with functionality needed for development:

1. **Shields Configuration**:
   - Navigate to Settings > Shields
   - Configure default shields settings:
     - Standard protection for general browsing
     - Create exceptions for development sites that require cookies or scripts

2. **Development-Specific Privacy Settings**:
   ```
   # Recommended settings for Project Citadel development
   - Aggressive Tracking Prevention: Enabled
   - HTTPS Everywhere: Enabled
   - Block Scripts: Disabled (required for web development)
   - Block Fingerprinting: Standard
   - Cookie blocking: Block cross-site cookies
   ```

3. **Development Domains Exceptions**:
   - Add exceptions for development domains:
     - `localhost`
     - `127.0.0.1`
     - Project Citadel staging environments
     - API testing tools

### Recommended Extensions for Web Development

Install the following extensions to enhance Brave for Project Citadel development:

| Extension | Purpose | Configuration Notes |
|-----------|---------|---------------------|
| React Developer Tools | React debugging | Enable in incognito mode |
| Redux DevTools | State management debugging | Configure to work with Project Citadel's state structure |
| JSON Formatter | API response formatting | Auto-format JSON responses |
| Wappalyzer | Technology stack identification | Useful for competitive analysis |
| Lighthouse | Performance testing | Configure for Project Citadel's performance metrics |
| Web Developer | Various web development tools | Enable specific tools as needed |
| CORS Unblock | API testing | Use only in development environments |
| Grammarly | Documentation writing | Configure for technical writing |

Installation steps:
1. Navigate to the Chrome Web Store
2. Search for the extension
3. Click "Add to Brave"
4. Configure extension settings as needed

### Integration with Development Workflow

Integrate Brave Browser into the Project Citadel development workflow:

1. **Browser Profiles**:
   - Create separate profiles for:
     - Development (with developer extensions)
     - Testing (clean environment)
     - Production (simulating end-user experience)

2. **Workspace Integration**:
   ```json
   // VSCode settings.json addition
   {
     "browser-preview.startUrl": "http://localhost:3000",
     "browser-preview.browser": "brave"
   }
   ```

3. **Command Line Integration**:
   ```bash
   # Add to your shell profile (.bashrc, .zshrc, etc.)
   alias brave-dev="brave-browser --user-data-dir=$HOME/.config/brave-dev"
   alias brave-test="brave-browser --user-data-dir=$HOME/.config/brave-test"
   ```

4. **Keyboard Shortcuts**:
   - Configure custom keyboard shortcuts for development tasks
   - Example: `Ctrl+Shift+D` to open developer tools

5. **Bookmark Organization**:
   - Create development-specific bookmark folders:
     - Project Citadel Documentation
     - API References
     - Testing Environments
     - Design Resources

## Recommended Workflow

1. **Setup**:
   - Clone the repository
   - Open in your preferred IDE
   - Install the recommended extensions
   - Apply the provided configuration files
   - Set up the development container (optional)
   - Configure MCP server for collaborative development
   - Set up Brave Browser with recommended configurations

2. **Development**:
   - Use the provided launch configurations to start the application
   - Use the provided tasks for common operations
   - Follow the project's coding standards and conventions
   - Use the debugging configurations for troubleshooting
   - Leverage MCP servers for collaborative coding sessions
   - Use Brave Browser with configured search engines for efficient research

3. **Testing**:
   - Run tests using the provided tasks
   - Use the debugging configurations for test debugging
   - Use Brave Browser's testing profile for clean environment testing

4. **Deployment**:
   - Use the Kubernetes tools for deployment configuration
   - Follow the project's deployment guidelines

## Conclusion

This IDE configuration guide provides a comprehensive setup for Project Citadel development. By following these recommendations, developers can ensure a consistent and efficient development experience across the team.

The configurations are optimized for the project's technology stack, including Python 3.10+, FastAPI, LangChain, LangGraph, React, Next.js, CopilotKit, and AG-UI Protocol. They provide support for code quality tools, debugging, and deployment, enabling developers to focus on building high-quality features for Project Citadel.

The addition of MCP servers enhances collaborative development capabilities, while the Brave Browser configuration optimizes web searches and research for the development process. These tools together create a powerful, privacy-focused, and collaborative development environment tailored to Project Citadel's specific needs.
