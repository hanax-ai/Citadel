
# Project Citadel Examples

This directory contains examples demonstrating the capabilities of Project Citadel.

## Full Demo

The `full_demo.py` file provides a comprehensive demonstration of Project Citadel's capabilities, including:

1. **Enhanced Agent Capabilities**
   - Multi-step reasoning
   - Reflection
   - Planning

2. **Memory Components**
   - Conversation memory
   - Entity memory

3. **Feedback Loops**
   - Feedback collection
   - Response evaluation
   - Self-improvement

4. **Team Coordination**
   - Multiple specialized agents working together
   - Message passing between agents
   - Shared memory

### Running the Full Demo

To run the full demo, use the following command:

```bash
python examples/full_demo.py
```

This will execute both the enhanced agent example and the team coordination example, demonstrating the full capabilities of Project Citadel.

### Expected Output

The demo will output logs showing the execution of each component, including:

- Planning steps
- Agent reasoning
- Reflection
- Memory updates
- Feedback collection
- Team coordination

Example output:

```
INFO - citadel.examples.full_demo - Starting Project Citadel full demo...
INFO - citadel.examples.full_demo - Running enhanced agent example...
INFO - citadel.examples.full_demo - Creating a plan...
INFO - citadel.examples.full_demo - Plan created: [...]
INFO - citadel.examples.full_demo - Running the agent...
INFO - citadel.examples.full_demo - Running reflection...
INFO - citadel.examples.full_demo - Reflection: [...]
INFO - citadel.examples.full_demo - Memory variables: [...]
INFO - citadel.examples.full_demo - Feedback collected: [...]
INFO - citadel.examples.full_demo - Enhanced agent example completed.
INFO - citadel.examples.full_demo - Running team coordination example...
INFO - citadel.examples.full_demo - Selecting an agent...
INFO - citadel.examples.full_demo - Selected agent: researcher
INFO - citadel.examples.full_demo - Researcher agent is researching...
INFO - citadel.examples.full_demo - Selected agent: planner
INFO - citadel.examples.full_demo - Planner agent is creating a plan...
INFO - citadel.examples.full_demo - Selected agent: executor
INFO - citadel.examples.full_demo - Executor agent is executing the plan...
INFO - citadel.examples.full_demo - Selected agent: critic
INFO - citadel.examples.full_demo - Critic agent is evaluating the report...
INFO - citadel.examples.full_demo - Team coordination example completed.
INFO - citadel.examples.full_demo - Demo completed successfully!
```

## Creating Your Own Examples

You can use the full demo as a template for creating your own examples. The key components you'll need to include are:

1. Initialize the LLM manager
2. Create memory components
3. Create agent nodes
4. Create feedback components
5. Create team coordination components
6. Set up the initial state
7. Run the components in sequence

For more detailed information on each component, refer to the documentation in the respective modules.
