
"""
End-to-end example demonstrating the full capabilities of Project Citadel.

This example showcases:
1. Enhanced agent capabilities with multi-step reasoning
2. Memory components for context retention
3. Feedback loops for self-improvement
4. Team coordination for complex tasks
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from citadel_core.logging import get_logger
from citadel_llm.models import LLMManager, GenerationResult
from citadel_langchain.memory import ConversationMemory, EntityMemory
from citadel_langgraph.nodes import ReActAgentNode, ReflectionNode, PlanningNode
from citadel_langgraph.state.agent_state import create_react_agent_state, create_multi_agent_state
from citadel_langgraph.feedback import FeedbackCollector, FeedbackOrchestrator
from citadel_langgraph.coordination import (
    TeamCoordinator,
    ResearcherAgent,
    PlannerAgent,
    ExecutorAgent,
    CriticAgent,
)
from citadel_langgraph.coordination.team_coordinator import RoundRobinStrategy


# Configure logging
logger = get_logger("citadel.examples.full_demo")
logger.setLevel(logging.INFO)


async def run_enhanced_agent_example():
    """Run an example with an enhanced agent using multi-step reasoning."""
    logger.info("Running enhanced agent example...")
    
    # Initialize LLM manager
    llm_manager = LLMManager()
    
    # Create memory components
    conversation_memory = ConversationMemory(k=5)
    entity_memory = EntityMemory()
    
    # Create agent node with enhanced capabilities
    agent = ReActAgentNode(
        name="research_agent",
        llm_manager=llm_manager,
        model_name="deepseek-r1:latest",
        system_message="You are a helpful research assistant with expertise in AI and technology.",
        tools=[
            {
                "name": "web_search",
                "description": "Search the web for information",
                "parameters": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
                },
            },
        ],
        reasoning_steps=3,  # Enhanced with more reasoning steps
    )
    
    # Create reflection node
    reflection_node = ReflectionNode(
        name="reflection",
        llm_manager=llm_manager,
        model_name="deepseek-r1:latest",
    )
    
    # Create planning node
    planning_node = PlanningNode(
        name="planning",
        llm_manager=llm_manager,
        model_name="deepseek-r1:latest",
    )
    
    # Create feedback collector
    feedback_collector = FeedbackCollector(
        feedback_store_path="./feedback_store",
    )
    
    # Create initial state
    state = create_react_agent_state(
        system_message="You are a helpful research assistant with expertise in AI and technology.",
        tools=[
            {
                "name": "web_search",
                "description": "Search the web for information",
            },
        ],
    )
    
    # Add a message to the state
    state["messages"] = [HumanMessage(content="What are the latest developments in AI?")]
    
    # Run planning
    logger.info("Creating a plan...")
    state = planning_node(state)
    logger.info(f"Plan created: {state.get('plan', [])}")
    
    # Run the agent
    logger.info("Running the agent...")
    state = agent(state)
    
    # Simulate action execution
    state["action_result"] = "Found information about GPT-4, DALL-E 3, and other recent AI models."
    
    # Run the agent again
    state = agent(state)
    
    # Simulate action execution
    state["action_result"] = "GPT-4 is a large language model with advanced reasoning capabilities."
    
    # Run the agent again
    state = agent(state)
    
    # Run reflection
    logger.info("Running reflection...")
    state = reflection_node(state)
    logger.info(f"Reflection: {state.get('reflection', '')}")
    
    # Update memory
    for i in range(0, len(state["messages"]), 2):
        if i + 1 < len(state["messages"]):
            conversation_memory.save_context(
                {"input": state["messages"][i].content},
                {"output": state["messages"][i+1].content}
            )
    
    # Load memory variables
    memory_variables = conversation_memory.load_memory_variables({})
    logger.info(f"Memory variables: {memory_variables}")
    
    # Collect feedback
    feedback_entry = feedback_collector.collect_feedback(
        query=state["messages"][0].content,
        response=state["messages"][-1].content,
        feedback="Good response, but could include more specific examples.",
        rating=4,
    )
    logger.info(f"Feedback collected: {feedback_entry}")
    
    return state


async def run_team_coordination_example():
    """Run an example with team coordination."""
    logger.info("Running team coordination example...")
    
    # Initialize LLM manager
    llm_manager = LLMManager()
    
    # Create agent configs
    agent_configs = {
        "researcher": {
            "system_message": "You are a researcher agent specialized in gathering information.",
            "tools": [
                {
                    "name": "web_search",
                    "description": "Search the web for information",
                },
            ],
        },
        "planner": {
            "system_message": "You are a planner agent specialized in creating plans.",
            "tools": [],
        },
        "executor": {
            "system_message": "You are an executor agent specialized in executing actions.",
            "tools": [],
        },
        "critic": {
            "system_message": "You are a critic agent specialized in evaluating work.",
            "tools": [],
        },
    }
    
    # Create a selection strategy
    selection_strategy = RoundRobinStrategy(list(agent_configs.keys()))
    
    # Create the team coordinator
    coordinator = TeamCoordinator(
        name="ai_research_team",
        agent_configs=agent_configs,
        agent_selection_strategy=selection_strategy,
        llm_manager=llm_manager,
        model_name="deepseek-r1:latest",
    )
    
    # Create specialized agents
    researcher = ResearcherAgent(
        name="researcher",
        llm_manager=llm_manager,
        model_name="deepseek-r1:latest",
    )
    
    planner = PlannerAgent(
        name="planner",
        llm_manager=llm_manager,
        model_name="deepseek-r1:latest",
    )
    
    executor = ExecutorAgent(
        name="executor",
        llm_manager=llm_manager,
        model_name="deepseek-r1:latest",
    )
    
    critic = CriticAgent(
        name="critic",
        llm_manager=llm_manager,
        model_name="deepseek-r1:latest",
    )
    
    # Create initial state
    state = create_multi_agent_state(agent_configs)
    
    # Add a task to the state
    state["shared_memory"] = {"task": "Research the latest developments in AI"}
    
    # Run the coordinator to select an agent
    logger.info("Selecting an agent...")
    state = coordinator(state)
    logger.info(f"Selected agent: {state.get('active_agent', '')}")
    
    # Simulate the researcher agent
    logger.info("Researcher agent is researching...")
    researcher_state = state["agent_states"]["researcher"]
    researcher_state = researcher.research_topic(researcher_state, "latest developments in AI")
    state["agent_states"]["researcher"] = researcher_state
    
    # Update shared memory with research results
    state = coordinator.update_shared_memory(
        state,
        key="research_results",
        value={"topic": "AI", "findings": "Found information about GPT-4, DALL-E 3, and other recent AI models."},
        agent_id="researcher",
    )
    
    # Send a message from researcher to planner
    state = coordinator.send_message(
        state,
        from_agent="researcher",
        to_agent="planner",
        message="I've completed the research on AI developments. Here are my findings: GPT-4, DALL-E 3, and other recent models.",
    )
    
    # Run the coordinator again to select the next agent
    state = coordinator(state)
    logger.info(f"Selected agent: {state.get('active_agent', '')}")
    
    # Simulate the planner agent
    logger.info("Planner agent is creating a plan...")
    planner_state = state["agent_states"]["planner"]
    planner_state = planner.create_plan(planner_state, "Create a report on AI developments")
    state["agent_states"]["planner"] = planner_state
    
    # Broadcast the plan to all agents
    state = coordinator.broadcast_message(
        state,
        from_agent="planner",
        message="Here's the plan: 1. Organize research findings, 2. Create report outline, 3. Write report sections, 4. Review and finalize.",
    )
    
    # Run the coordinator again to select the next agent
    state = coordinator(state)
    logger.info(f"Selected agent: {state.get('active_agent', '')}")
    
    # Simulate the executor agent
    logger.info("Executor agent is executing the plan...")
    executor_state = state["agent_states"]["executor"]
    executor_state = executor.execute_action(
        executor_state,
        action="write_report",
        action_input={"title": "Latest AI Developments", "content": "Report content..."},
    )
    state["agent_states"]["executor"] = executor_state
    
    # Update shared memory with report
    state = coordinator.update_shared_memory(
        state,
        key="report",
        value={"title": "Latest AI Developments", "content": "Report content..."},
        agent_id="executor",
    )
    
    # Run the coordinator again to select the next agent
    state = coordinator(state)
    logger.info(f"Selected agent: {state.get('active_agent', '')}")
    
    # Simulate the critic agent
    logger.info("Critic agent is evaluating the report...")
    critic_state = state["agent_states"]["critic"]
    critic_state = critic.critique_work(
        critic_state,
        work=state["shared_memory"]["report"]["content"],
        criteria=["Accuracy", "Clarity", "Completeness"],
    )
    state["agent_states"]["critic"] = critic_state
    
    # Send feedback to the executor
    state = coordinator.send_message(
        state,
        from_agent="critic",
        to_agent="executor",
        message="The report is good, but could use more specific examples and details.",
    )
    
    return state


async def main():
    """Run the full demo."""
    logger.info("Starting Project Citadel full demo...")
    
    # Run enhanced agent example
    enhanced_agent_state = await run_enhanced_agent_example()
    logger.info("Enhanced agent example completed.")
    
    # Run team coordination example
    team_coordination_state = await run_team_coordination_example()
    logger.info("Team coordination example completed.")
    
    logger.info("Demo completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
