
# Project Citadel Phase 3 Enhancements

This document describes the enhancements implemented in Phase 3 of Project Citadel, focusing on expanding agent capabilities, improving reasoning mechanisms, and enhancing multi-agent coordination.

## 1. Tool Usage Enhancements

### ToolRegistry

The `ToolRegistry` class provides a centralized registry for managing tools available to agents. It allows for:

- Registering individual tools or collections of tools
- Retrieving tools by name
- Getting descriptions of all registered tools
- Executing tools by name with appropriate arguments

```python
from citadel_langgraph.tools import ToolRegistry, WebSearchTool, CalculatorTool

# Create a registry
registry = ToolRegistry()

# Register tools
registry.register_tools([
    WebSearchTool(),
    CalculatorTool(),
])

# Execute a tool
results = registry.execute_tool("web_search", query="Project Citadel")
```

### Tool Selection Strategies

Tool selection strategies allow for intelligent selection of tools based on the current state:

- `AllToolsStrategy`: Provides all registered tools to the agent
- `TaskBasedToolStrategy`: Selects tools based on keywords in the task description
- `DynamicToolStrategy`: Uses a custom function to select tools based on the current state

```python
from citadel_langgraph.tools import ToolSelectionStrategy, TaskBasedToolStrategy

# Create a task-based strategy
strategy = TaskBasedToolStrategy(
    registry,
    task_tool_mapping={
        "search": ["web_search"],
        "calculate": ["calculator"],
        "file": ["file_operation"],
    },
    default_tools=["calculator"],
)

# Use the strategy in an agent
agent = ReActAgentNode(
    name="agent",
    tool_selection_strategy=strategy,
)
```

### Implemented Tools

#### WebSearchTool

A tool for performing web searches to gather information.

```python
from citadel_langgraph.tools import WebSearchTool

search_tool = WebSearchTool()
results = search_tool("Project Citadel")
```

#### CalculatorTool

A tool for performing mathematical calculations.

```python
from citadel_langgraph.tools import CalculatorTool

calc_tool = CalculatorTool()
result = calc_tool("2 + 2 * 3")
```

#### FileOperationTool

A tool for reading, writing, and manipulating files.

```python
from citadel_langgraph.tools import FileOperationTool

file_tool = FileOperationTool(base_directory="/path/to/files")
file_tool(operation="write", path="test.txt", content="Hello, world!")
content = file_tool(operation="read", path="test.txt")
```

## 2. Reasoning Mechanism Enhancements

### Enhanced ReActAgentNode

The `ReActAgentNode` has been enhanced with step-by-step reasoning capabilities:

- Multiple reasoning steps before taking action
- More detailed prompting for complex problem-solving
- Integration with tool selection strategies
- Improved parsing of agent outputs

```python
from citadel_langgraph.nodes import ReActAgentNode

agent = ReActAgentNode(
    name="reasoning_agent",
    reasoning_steps=3,  # Perform 3 reasoning steps before action
)
```

### ReflectionNode

The `ReflectionNode` allows agents to reflect on their actions and improve their reasoning:

- Analyzes the agent's step history
- Identifies patterns, strengths, and weaknesses
- Suggests improvements for future steps

```python
from citadel_langgraph.nodes import ReflectionNode

reflection_node = ReflectionNode(name="reflection")
reflected_state = reflection_node(agent_state)
```

### PlanningNode

The `PlanningNode` enables agents to plan multi-step tasks:

- Creates detailed plans with steps, tools, and expected outcomes
- Considers available tools and task requirements
- Structures plans for efficient execution

```python
from citadel_langgraph.nodes import PlanningNode

planning_node = PlanningNode(name="planning")
planned_state = planning_node(agent_state)
```

## 3. Multi-Agent Coordination Enhancements

### TeamCoordinator

The `TeamCoordinator` manages multiple agents in a workflow:

- Selects the next agent to execute based on a strategy
- Facilitates message passing between agents
- Manages shared memory for collaborative work

```python
from citadel_langgraph.coordination import TeamCoordinator
from citadel_langgraph.coordination.team_coordinator import RoundRobinStrategy

coordinator = TeamCoordinator(
    name="team_coordinator",
    agent_configs={
        "researcher": {...},
        "planner": {...},
        "executor": {...},
        "critic": {...},
    },
    agent_selection_strategy=RoundRobinStrategy(["researcher", "planner", "executor", "critic"]),
)
```

### Specialized Agent Roles

#### ResearcherAgent

Specialized for gathering and analyzing information.

```python
from citadel_langgraph.coordination import ResearcherAgent

researcher = ResearcherAgent(name="researcher")
research_results = researcher.research_topic(state, "Project Citadel")
```

#### PlannerAgent

Specialized for creating detailed plans and strategies.

```python
from citadel_langgraph.coordination import PlannerAgent

planner = PlannerAgent(name="planner")
planned_state = planner.create_plan(state, "Implement Project Citadel")
```

#### ExecutorAgent

Specialized for executing plans and performing actions.

```python
from citadel_langgraph.coordination import ExecutorAgent

executor = ExecutorAgent(name="executor", tool_registry=registry)
result_state = executor.execute_plan(state, plan)
```

#### CriticAgent

Specialized for evaluating and providing feedback.

```python
from citadel_langgraph.coordination import CriticAgent

critic = CriticAgent(name="critic")
critique = critic.critique_work(state, work="Project Citadel implementation")
```

### Message Passing System

The message passing system allows agents to communicate with each other:

- Direct messages between specific agents
- Broadcasting messages to all agents
- Structured message format with metadata

```python
# Send a message from one agent to another
updated_state = coordinator.send_message(
    state,
    from_agent="researcher",
    to_agent="planner",
    message="Here's the research information",
)

# Broadcast a message to all agents
updated_state = coordinator.broadcast_message(
    state,
    from_agent="planner",
    message="Here's the plan for everyone",
)
```

## Integration with Existing Components

These enhancements integrate seamlessly with the existing memory components and feedback loops:

- Tools can access and update memory components
- Reasoning mechanisms can utilize feedback from evaluators
- Multi-agent coordination works with existing workflow structures

## Usage Example

```python
from citadel_langgraph.tools import ToolRegistry, WebSearchTool, CalculatorTool
from citadel_langgraph.coordination import TeamCoordinator, ResearcherAgent, PlannerAgent, ExecutorAgent, CriticAgent
from citadel_langgraph.coordination.team_coordinator import RoundRobinStrategy

# Create tool registry
registry = ToolRegistry()
registry.register_tools([
    WebSearchTool(),
    CalculatorTool(),
])

# Create specialized agents
researcher = ResearcherAgent(name="researcher")
planner = PlannerAgent(name="planner")
executor = ExecutorAgent(name="executor", tool_registry=registry)
critic = CriticAgent(name="critic")

# Create team coordinator
coordinator = TeamCoordinator(
    name="team_coordinator",
    agent_configs={
        "researcher": {"system_message": "You are a researcher agent."},
        "planner": {"system_message": "You are a planner agent."},
        "executor": {"system_message": "You are an executor agent."},
        "critic": {"system_message": "You are a critic agent."},
    },
    agent_selection_strategy=RoundRobinStrategy(["researcher", "planner", "executor", "critic"]),
)

# Create initial state
state = create_multi_agent_state(coordinator.agent_configs)

# Execute the workflow
while True:
    # Select the next agent
    state = coordinator(state)
    active_agent = state["active_agent"]
    
    # Execute the active agent
    if active_agent == "researcher":
        agent_state = state["agent_states"][active_agent]
        result_state = researcher(agent_state)
        state["agent_states"][active_agent] = result_state
        
        # Share research results
        coordinator.update_shared_memory(
            state,
            key="research_results",
            value=result_state.get("research_results"),
            agent_id=active_agent,
        )
    
    elif active_agent == "planner":
        # Similar execution for other agents...
        pass
    
    # Check if workflow is complete
    if state.get("status") == "completed":
        break
```

## Conclusion

The Phase 3 enhancements significantly improve the capabilities of agents in Project Citadel:

1. Expanded tool usage provides agents with more ways to interact with the world
2. Improved reasoning mechanisms enable more sophisticated problem-solving
3. Enhanced multi-agent coordination allows for complex collaborative workflows

These enhancements make the agents more capable and effective in performing complex tasks, setting the foundation for future improvements in Phase 4.
