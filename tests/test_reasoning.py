
"""
Tests for the enhanced reasoning mechanisms.
"""

import unittest
from unittest.mock import MagicMock, patch

from citadel_langgraph.nodes import (
    ReActAgentNode,
    ReflectionNode,
    PlanningNode,
)
from citadel_langgraph.state.agent_state import (
    ReActAgentState,
    create_react_agent_state,
)
from citadel_llm.models import LLMManager, GenerationResult

# Use GenerationResult instead of LLMResult
LLMResult = GenerationResult


class TestReActAgentNode(unittest.TestCase):
    """Test the enhanced ReActAgentNode."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock LLM manager
        self.mock_llm_manager = MagicMock(spec=LLMManager)
        self.mock_llm_result = MagicMock(spec=LLMResult)
        self.mock_llm_result.text = (
            "Thought: I need to search for information about AI.\n"
            "Action: web_search\n"
            "Action Input: {\"query\": \"latest AI developments\"}"
        )
        
        # Configure the mock to return the result
        async def async_generate(*args, **kwargs):
            return self.mock_llm_result
        
        self.mock_llm_manager.generate.side_effect = async_generate
        
        # Create the agent node
        self.agent_node = ReActAgentNode(
            name="test_agent",
            llm_manager=self.mock_llm_manager,
            model_name="test_model",
            system_message="You are a helpful assistant.",
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
            reasoning_steps=2,
        )
        
        # Create a test state
        self.state = create_react_agent_state(
            system_message="You are a helpful assistant.",
            tools=[
                {
                    "name": "web_search",
                    "description": "Search the web for information",
                },
            ],
        )
        
        # Add a message to the state
        from langchain_core.messages import HumanMessage
        self.state["messages"] = [HumanMessage(content="Tell me about the latest AI developments")]
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent_node.name, "test_agent")
        self.assertEqual(self.agent_node.model_name, "test_model")
        self.assertEqual(self.agent_node.system_message, "You are a helpful assistant.")
        self.assertEqual(len(self.agent_node.tools), 1)
        self.assertEqual(self.agent_node.reasoning_steps, 2)
    
    def test_agent_execution(self):
        """Test agent execution with step-by-step reasoning."""
        result_state = self.agent_node(self.state)
        
        # Check that the LLM was called
        self.mock_llm_manager.generate.assert_called()
        
        # Check that the state was updated correctly
        self.assertEqual(result_state["thought"], self.mock_llm_result.text)
        self.assertEqual(result_state["action"], "web_search")
        self.assertEqual(result_state["action_input"], {"query": "latest AI developments"})
        
        # Check that reasoning steps were recorded
        self.assertTrue("reasoning_steps" in result_state)
        self.assertEqual(len(result_state["reasoning_steps"]), 1)
        
        # Check that step history was updated
        self.assertTrue("step_history" in result_state)
        self.assertEqual(len(result_state["step_history"]), 1)
        
        # Check that current step was updated
        self.assertEqual(result_state["current_step"], "execute_action")


class TestReflectionNode(unittest.TestCase):
    """Test the ReflectionNode."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock LLM manager
        self.mock_llm_manager = MagicMock(spec=LLMManager)
        self.mock_llm_result = MagicMock(spec=LLMResult)
        self.mock_llm_result.text = (
            "Reflection on previous steps:\n"
            "1. The search query was effective in finding relevant information.\n"
            "2. I could have been more specific in my query to get more targeted results.\n"
            "3. Next time, I should consider using multiple search queries to get a broader perspective."
        )
        
        # Configure the mock to return the result
        async def async_generate(*args, **kwargs):
            return self.mock_llm_result
        
        self.mock_llm_manager.generate.side_effect = async_generate
        
        # Create the reflection node
        self.reflection_node = ReflectionNode(
            name="test_reflection",
            llm_manager=self.mock_llm_manager,
            model_name="test_model",
        )
        
        # Create a test state with step history
        self.state = create_react_agent_state()
        self.state["step_history"] = [
            {
                "step": "initialize",
                "thought": "I need to search for information about AI.",
                "action": "web_search",
                "action_input": {"query": "latest AI developments"},
            },
            {
                "step": "execute_action",
                "thought": "I found some information about AI. Now I need to summarize it.",
                "action": None,
                "action_input": None,
            },
        ]
    
    def test_reflection_node_initialization(self):
        """Test reflection node initialization."""
        self.assertEqual(self.reflection_node.name, "test_reflection")
        self.assertEqual(self.reflection_node.model_name, "test_model")
    
    def test_reflection_generation(self):
        """Test reflection generation."""
        result_state = self.reflection_node(self.state)
        
        # Check that the LLM was called
        self.mock_llm_manager.generate.assert_called()
        
        # Check that the state was updated correctly
        self.assertEqual(result_state["reflection"], self.mock_llm_result.text)
        
        # Check that reflections history was updated
        self.assertTrue("reflections" in result_state)
        self.assertEqual(len(result_state["reflections"]), 1)
        self.assertEqual(result_state["reflections"][0]["reflection"], self.mock_llm_result.text)


class TestPlanningNode(unittest.TestCase):
    """Test the PlanningNode."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock LLM manager
        self.mock_llm_manager = MagicMock(spec=LLMManager)
        self.mock_llm_result = MagicMock(spec=LLMResult)
        self.mock_llm_result.text = (
            "Step 1: Search for information about AI developments\n"
            "- Use the web_search tool\n"
            "- This will provide an overview of recent AI advancements\n\n"
            "Step 2: Analyze the search results\n"
            "- Identify key trends and breakthroughs\n"
            "- Note important companies and researchers\n\n"
            "Step 3: Summarize the findings\n"
            "- Create a concise summary of the latest developments\n"
            "- Highlight the most significant advancements"
        )
        
        # Configure the mock to return the result
        async def async_generate(*args, **kwargs):
            return self.mock_llm_result
        
        self.mock_llm_manager.generate.side_effect = async_generate
        
        # Create the planning node
        self.planning_node = PlanningNode(
            name="test_planning",
            llm_manager=self.mock_llm_manager,
            model_name="test_model",
        )
        
        # Create a test state
        self.state = create_react_agent_state()
        
        # Add a message to the state
        from langchain_core.messages import HumanMessage
        self.state["messages"] = [HumanMessage(content="Tell me about the latest AI developments")]
        
        # Add tools to the state
        self.state["tools"] = [
            {
                "name": "web_search",
                "description": "Search the web for information",
            },
        ]
    
    def test_planning_node_initialization(self):
        """Test planning node initialization."""
        self.assertEqual(self.planning_node.name, "test_planning")
        self.assertEqual(self.planning_node.model_name, "test_model")
    
    def test_plan_generation(self):
        """Test plan generation."""
        result_state = self.planning_node(self.state)
        
        # Check that the LLM was called
        self.mock_llm_manager.generate.assert_called()
        
        # Check that the state was updated correctly
        self.assertTrue("plan" in result_state)
        self.assertEqual(len(result_state["plan"]), 3)  # 3 steps in the plan
        
        # Check that the plan was added to messages
        self.assertEqual(len(result_state["messages"]), 2)
        self.assertTrue("I've created a plan" in result_state["messages"][1].content)


if __name__ == "__main__":
    unittest.main()
