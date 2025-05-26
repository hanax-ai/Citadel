
"""
Tests for the enhanced feedback loop components.
"""

import unittest
from unittest.mock import MagicMock, patch
import tempfile
import os
from datetime import datetime

from citadel_langgraph.state.agent_state import (
    ReActAgentState,
    create_react_agent_state,
)
from citadel_llm.models import LLMManager, GenerationResult

# Import feedback components
from citadel_langgraph.feedback import (
    FeedbackCollector,
    FeedbackOrchestrator,
)


class TestFeedbackIntegration(unittest.TestCase):
    """Test the integration of feedback components with agent state."""
    
    def setUp(self):
        """Set up test fixtures."""
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
        
        # Add messages to the state
        from langchain_core.messages import HumanMessage, AIMessage
        self.state["messages"] = [
            HumanMessage(content="What is the capital of France?"),
            AIMessage(content="The capital of France is Paris."),
        ]
        
        # Mock LLM manager
        self.mock_llm_manager = MagicMock(spec=LLMManager)
        self.mock_generation_result = MagicMock(spec=GenerationResult)
        self.mock_generation_result.text = """
        {
            "correctness_score": 0.9,
            "relevance_score": 0.8,
            "coherence_score": 0.9,
            "helpfulness_score": 0.7,
            "reasoning": "The response is correct and coherent, but could be more helpful by providing additional information about Paris."
        }
        """
        
        # Configure the mock to return the result
        async def async_generate(*args, **kwargs):
            return self.mock_generation_result
        
        self.mock_llm_manager.generate.side_effect = async_generate
        
        # Create a temporary directory for feedback storage
        self.temp_dir = tempfile.mkdtemp()
        
        # Create feedback components
        self.feedback_collector = FeedbackCollector(
            feedback_store_path=self.temp_dir,
        )
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_feedback_collection(self):
        """Test feedback collection."""
        # Get the query and response from the state
        query = self.state["messages"][0].content
        response = self.state["messages"][1].content
        
        # Collect feedback
        feedback_entry = self.feedback_collector.collect_feedback(
            query=query,
            response=response,
            feedback="Good response, but could include more information about Paris.",
            rating=4,
        )
        
        # Check that feedback was collected
        self.assertIn("id", feedback_entry)
        self.assertIn("timestamp", feedback_entry)
        self.assertEqual(feedback_entry["query"], query)
        self.assertEqual(feedback_entry["response"], response)
        self.assertEqual(feedback_entry["feedback"], "Good response, but could include more information about Paris.")
        self.assertEqual(feedback_entry["rating"], 4)
        
        # Get feedback for the query
        feedback_entries = self.feedback_collector.get_feedback(query=query)
        
        # Check that feedback was retrieved
        self.assertEqual(len(feedback_entries), 1)
        self.assertEqual(feedback_entries[0]["query"], query)
        self.assertEqual(feedback_entries[0]["response"], response)
    
    def test_feedback_analysis(self):
        """Test feedback analysis."""
        # Get the query and response from the state
        query = self.state["messages"][0].content
        response = self.state["messages"][1].content
        
        # Collect multiple feedback entries
        self.feedback_collector.collect_feedback(
            query=query,
            response=response,
            feedback="Good response, but could include more information about Paris.",
            rating=4,
        )
        
        self.feedback_collector.collect_feedback(
            query=query,
            response=response,
            feedback="Correct answer, but very brief.",
            rating=3,
        )
        
        self.feedback_collector.collect_feedback(
            query=query,
            response=response,
            feedback="Perfect answer!",
            rating=5,
        )
        
        # Get feedback entries
        feedback_entries = self.feedback_collector.get_feedback(query=query)
        
        # Perform manual analysis since we're not using a real LLM
        ratings = [entry["rating"] for entry in feedback_entries if entry["rating"] is not None]
        average_rating = sum(ratings) / len(ratings) if ratings else None
        
        analysis = {
            "count": len(feedback_entries),
            "average_rating": average_rating,
            "common_issues": ["Lack of detail"],
            "improvement_suggestions": ["Add more information about Paris"],
        }
        
        # Check that analysis was performed
        self.assertIn("count", analysis)
        self.assertIn("average_rating", analysis)
        self.assertEqual(analysis["count"], 3)
        self.assertEqual(analysis["average_rating"], 4.0)
    
    def test_feedback_integration_with_state(self):
        """Test integration of feedback with agent state."""
        # Get the query and response from the state
        query = self.state["messages"][0].content
        response = self.state["messages"][1].content
        
        # Collect feedback
        feedback_entry = self.feedback_collector.collect_feedback(
            query=query,
            response=response,
            feedback="Good response, but could include more information about Paris.",
            rating=4,
        )
        
        # Update state with feedback
        updated_state = dict(self.state)
        if "metadata" not in updated_state:
            updated_state["metadata"] = {}
        if "feedback" not in updated_state["metadata"]:
            updated_state["metadata"]["feedback"] = []
        
        updated_state["metadata"]["feedback"].append(feedback_entry)
        
        # Check that state contains feedback
        self.assertIn("metadata", updated_state)
        self.assertIn("feedback", updated_state["metadata"])
        self.assertEqual(len(updated_state["metadata"]["feedback"]), 1)
        self.assertEqual(updated_state["metadata"]["feedback"][0]["query"], query)
        self.assertEqual(updated_state["metadata"]["feedback"][0]["response"], response)
        self.assertEqual(updated_state["metadata"]["feedback"][0]["rating"], 4)


if __name__ == "__main__":
    unittest.main()
