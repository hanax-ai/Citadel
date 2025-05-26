
"""
Tests for the multi-agent coordination components.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from citadel_langgraph.coordination import (
    TeamCoordinator,
    ResearcherAgent,
    PlannerAgent,
    ExecutorAgent,
    CriticAgent,
)
from citadel_langgraph.coordination.team_coordinator import (
    RoundRobinStrategy,
    TaskBasedStrategy,
    DynamicStrategy,
)
from citadel_langgraph.state.agent_state import (
    MultiAgentState,
    create_multi_agent_state,
)
from citadel_llm.models import LLMManager, GenerationResult

# Use GenerationResult instead of LLMResult
LLMResult = GenerationResult


class TestTeamCoordinator(unittest.TestCase):
    """Test the TeamCoordinator."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock LLM manager
        self.mock_llm_manager = MagicMock(spec=LLMManager)
        
        # Create agent configs
        self.agent_configs = {
            "researcher": {
                "system_message": "You are a researcher agent.",
                "tools": [
                    {
                        "name": "web_search",
                        "description": "Search the web for information",
                    },
                ],
            },
            "planner": {
                "system_message": "You are a planner agent.",
                "tools": [],
            },
            "executor": {
                "system_message": "You are an executor agent.",
                "tools": [],
            },
            "critic": {
                "system_message": "You are a critic agent.",
                "tools": [],
            },
        }
        
        # Create a selection strategy
        self.selection_strategy = RoundRobinStrategy(list(self.agent_configs.keys()))
        
        # Create the team coordinator
        self.coordinator = TeamCoordinator(
            name="test_coordinator",
            agent_configs=self.agent_configs,
            agent_selection_strategy=self.selection_strategy,
            llm_manager=self.mock_llm_manager,
            model_name="test_model",
        )
        
        # Create a test state
        self.state = create_multi_agent_state(self.agent_configs)
    
    def test_coordinator_initialization(self):
        """Test coordinator initialization."""
        self.assertEqual(self.coordinator.name, "test_coordinator")
        self.assertEqual(self.coordinator.model_name, "test_model")
        self.assertEqual(self.coordinator.agent_configs, self.agent_configs)
    
    def test_agent_selection(self):
        """Test agent selection."""
        result_state = self.coordinator(self.state)
        
        # Check that an agent was selected
        self.assertTrue("active_agent" in result_state)
        self.assertEqual(result_state["active_agent"], "researcher")  # First agent in round-robin
        
        # Check that execution history was updated
        self.assertTrue("execution_history" in result_state)
        self.assertEqual(len(result_state["execution_history"]), 1)
        self.assertEqual(result_state["execution_history"][0]["selected_agent"], "researcher")
    
    def test_send_message(self):
        """Test sending a message between agents."""
        result_state = self.coordinator.send_message(
            self.state,
            from_agent="researcher",
            to_agent="planner",
            message="Here's some research information",
        )
        
        # Check that the message was added to messages
        self.assertTrue("messages" in result_state)
        self.assertEqual(len(result_state["messages"]), 1)
        self.assertEqual(result_state["messages"][0]["from"], "researcher")
        self.assertEqual(result_state["messages"][0]["to"], "planner")
        self.assertEqual(result_state["messages"][0]["content"], "Here's some research information")
        
        # Check that the message was added to the recipient's messages
        recipient_state = result_state["agent_states"]["planner"]
        self.assertTrue("messages" in recipient_state)
        self.assertGreaterEqual(len(recipient_state["messages"]), 1)
        # Check that the last message has the expected content
        self.assertEqual(recipient_state["messages"][-1].content, "Here's some research information")
    
    def test_broadcast_message(self):
        """Test broadcasting a message to all agents."""
        result_state = self.coordinator.broadcast_message(
            self.state,
            from_agent="planner",
            message="Here's the plan for everyone",
        )
        
        # Check that the message was sent to all other agents
        self.assertTrue("messages" in result_state)
        self.assertEqual(len(result_state["messages"]), 3)  # 3 recipients (excluding sender)
        
        # Check that each recipient got the message
        for agent_id, agent_state in result_state["agent_states"].items():
            if agent_id != "planner":  # Exclude sender
                self.assertTrue("messages" in agent_state)
                self.assertGreaterEqual(len(agent_state["messages"]), 1)
                # Check that the last message has the expected content
                self.assertEqual(agent_state["messages"][-1].content, "Here's the plan for everyone")
    
    def test_update_shared_memory(self):
        """Test updating shared memory."""
        result_state = self.coordinator.update_shared_memory(
            self.state,
            key="research_results",
            value={"topic": "AI", "findings": "Some findings"},
            agent_id="researcher",
        )
        
        # Check that the memory was updated
        self.assertTrue("shared_memory" in result_state)
        self.assertTrue("research_results" in result_state["shared_memory"])
        self.assertEqual(result_state["shared_memory"]["research_results"]["topic"], "AI")
        
        # Check that metadata was updated
        self.assertTrue("memory_metadata" in result_state)
        self.assertTrue("research_results" in result_state["memory_metadata"])
        self.assertEqual(result_state["memory_metadata"]["research_results"]["updated_by"], "researcher")


class TestAgentRoles(unittest.TestCase):
    """Test the specialized agent roles."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock LLM manager
        self.mock_llm_manager = MagicMock(spec=LLMManager)
        self.mock_llm_result = MagicMock(spec=LLMResult)
        self.mock_llm_result.text = "Mock LLM response"
        
        # Configure the mock to return the result
        async def async_generate(*args, **kwargs):
            return self.mock_llm_result
        
        self.mock_llm_manager.generate.side_effect = async_generate
    
    def test_researcher_agent(self):
        """Test the ResearcherAgent."""
        # Create the researcher agent
        researcher = ResearcherAgent(
            name="test_researcher",
            llm_manager=self.mock_llm_manager,
            model_name="test_model",
        )
        
        # Check initialization
        self.assertEqual(researcher.name, "test_researcher")
        self.assertEqual(researcher.model_name, "test_model")
        self.assertTrue("research" in researcher.system_message.lower())
        
        # Create a test state
        from citadel_langgraph.state.agent_state import create_react_agent_state
        state = create_react_agent_state()
        
        # Test research_topic method
        self.mock_llm_result.text = (
            "Thought: I found information about AI.\n"
            "Action: web_search\n"
            "Action Input: {\"query\": \"AI research\"}"
        )
        
        result_state = researcher.research_topic(state, "AI research")
        
        # Check that the LLM was called
        self.mock_llm_manager.generate.assert_called()
        
        # Check that research results were added
        self.assertTrue("research_results" in result_state)
        self.assertEqual(result_state["research_results"]["topic"], "AI research")
    
    def test_planner_agent(self):
        """Test the PlannerAgent."""
        # Create the planner agent
        planner = PlannerAgent(
            name="test_planner",
            llm_manager=self.mock_llm_manager,
            model_name="test_model",
        )
        
        # Check initialization
        self.assertEqual(planner.name, "test_planner")
        self.assertEqual(planner.model_name, "test_model")
        self.assertTrue("plan" in planner.system_message.lower())
        
        # Create a test state
        from citadel_langgraph.state.agent_state import create_react_agent_state
        state = create_react_agent_state()
        
        # Test create_plan method
        self.mock_llm_result.text = (
            "Step 1: Research AI\n"
            "Step 2: Analyze findings\n"
            "Step 3: Create report"
        )
        
        result_state = planner.create_plan(state, "Create an AI research report")
        
        # Check that the LLM was called
        self.mock_llm_manager.generate.assert_called()
        
        # Check that plan was added
        self.assertTrue("plan" in result_state)
    
    def test_executor_agent(self):
        """Test the ExecutorAgent."""
        # Create a mock tool registry
        from citadel_langgraph.tools import ToolRegistry
        tool_registry = MagicMock(spec=ToolRegistry)
        tool_registry.get_tool_descriptions.return_value = [
            {
                "name": "web_search",
                "description": "Search the web for information",
            },
        ]
        tool_registry.get_all_tools.return_value = {"web_search": MagicMock()}
        tool_registry.get_tool.return_value = MagicMock()
        
        # Create the executor agent
        executor = ExecutorAgent(
            name="test_executor",
            tool_registry=tool_registry,
            llm_manager=self.mock_llm_manager,
            model_name="test_model",
        )
        
        # Check initialization
        self.assertEqual(executor.name, "test_executor")
        self.assertEqual(executor.model_name, "test_model")
        self.assertTrue("execut" in executor.system_message.lower())
        
        # Create a test state
        from citadel_langgraph.state.agent_state import create_react_agent_state
        state = create_react_agent_state()
        
        # Test execute_action method
        result_state = executor.execute_action(
            state,
            action="web_search",
            action_input={"query": "AI research"},
        )
        
        # Check that action was set
        self.assertEqual(result_state["action"], "web_search")
        self.assertEqual(result_state["action_input"], {"query": "AI research"})
    
    def test_critic_agent(self):
        """Test the CriticAgent."""
        # Create the critic agent
        critic = CriticAgent(
            name="test_critic",
            llm_manager=self.mock_llm_manager,
            model_name="test_model",
        )
        
        # Check initialization
        self.assertEqual(critic.name, "test_critic")
        self.assertEqual(critic.model_name, "test_model")
        self.assertTrue("critic" in critic.system_message.lower())
        
        # Create a test state
        from citadel_langgraph.state.agent_state import create_react_agent_state
        state = create_react_agent_state()
        
        # Test critique_work method
        self.mock_llm_result.text = (
            "Strengths:\n"
            "- Well-researched content\n"
            "- Clear explanations\n\n"
            "Weaknesses:\n"
            "- Some technical inaccuracies\n"
            "- Could use more examples\n\n"
            "Suggestions:\n"
            "- Add more examples\n"
            "- Verify technical details"
        )
        
        result_state = critic.critique_work(
            state,
            work="AI is a field of computer science...",
            criteria=["Accuracy", "Clarity", "Completeness"],
        )
        
        # Check that the LLM was called
        self.mock_llm_manager.generate.assert_called()
        
        # Check that critique results were added
        self.assertTrue("critique_results" in result_state)
        self.assertEqual(result_state["critique_results"]["work"], "AI is a field of computer science...")
        self.assertTrue(len(result_state["critique_results"]["strengths"]) > 0)
        self.assertTrue(len(result_state["critique_results"]["weaknesses"]) > 0)
        self.assertTrue(len(result_state["critique_results"]["suggestions"]) > 0)


class TestSelectionStrategies(unittest.TestCase):
    """Test the agent selection strategies."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create agent configs
        self.agent_configs = {
            "researcher": {
                "system_message": "You are a researcher agent.",
            },
            "planner": {
                "system_message": "You are a planner agent.",
            },
            "executor": {
                "system_message": "You are an executor agent.",
            },
            "critic": {
                "system_message": "You are a critic agent.",
            },
        }
        
        # Create a test state
        self.state = create_multi_agent_state(self.agent_configs)
        self.state["active_agent"] = "researcher"
    
    def test_round_robin_strategy(self):
        """Test the RoundRobinStrategy."""
        strategy = RoundRobinStrategy(list(self.agent_configs.keys()))
        
        # First selection should be the next agent after the active one
        next_agent = strategy(self.state)
        self.assertEqual(next_agent, "planner")
        
        # Update state and check next selection
        self.state["active_agent"] = next_agent
        next_agent = strategy(self.state)
        self.assertEqual(next_agent, "executor")
        
        # Test wrapping around
        self.state["active_agent"] = "critic"
        next_agent = strategy(self.state)
        self.assertEqual(next_agent, "researcher")
    
    def test_task_based_strategy(self):
        """Test the TaskBasedStrategy."""
        task_agent_mapping = {
            "research": ["researcher"],
            "plan": ["planner"],
            "execute": ["executor"],
            "critique": ["critic"],
        }
        
        strategy = TaskBasedStrategy(task_agent_mapping, "planner")
        
        # Add a task to the state
        self.state["shared_memory"] = {"task": "Research AI developments"}
        
        # Selection should be based on the task
        next_agent = strategy(self.state)
        self.assertEqual(next_agent, "researcher")
        
        # Change the task
        self.state["shared_memory"] = {"task": "Plan the project"}
        next_agent = strategy(self.state)
        self.assertEqual(next_agent, "planner")
        
        # Test default agent
        self.state["shared_memory"] = {"task": "Something unrelated"}
        next_agent = strategy(self.state)
        self.assertEqual(next_agent, "planner")


if __name__ == "__main__":
    unittest.main()
