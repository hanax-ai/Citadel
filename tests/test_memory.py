
"""
Tests for the enhanced memory components.
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

# Import memory components from langchain
from citadel_langchain.memory import (
    BufferMemory,
    ConversationMemory,
    SummaryMemory,
    EntityMemory,
)


class TestMemoryIntegration(unittest.TestCase):
    """Test the integration of memory components with agent state."""
    
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
            HumanMessage(content="Hello, my name is Alice."),
            AIMessage(content="Hello Alice! How can I help you today?"),
            HumanMessage(content="I'm interested in learning about AI."),
            AIMessage(content="That's great! AI is a fascinating field. What specific aspects are you interested in?"),
        ]
        
        # Create memory components
        self.buffer_memory = BufferMemory()
        self.conversation_memory = ConversationMemory(k=2)
        
        # Mock LLM for summary and entity memory
        self.mock_llm_manager = MagicMock(spec=LLMManager)
        self.mock_generation_result = MagicMock(spec=GenerationResult)
        self.mock_generation_result.text = "Alice is a person interested in learning about AI."
        
        # Configure the mock to return the result
        async def async_generate(*args, **kwargs):
            return self.mock_generation_result
        
        self.mock_llm_manager.generate.side_effect = async_generate
    
    def test_buffer_memory_integration(self):
        """Test integration of buffer memory with agent state."""
        # Update memory from state
        for i in range(0, len(self.state["messages"]), 2):
            if i + 1 < len(self.state["messages"]):
                self.buffer_memory.save_context(
                    {"input": self.state["messages"][i].content},
                    {"output": self.state["messages"][i+1].content}
                )
        
        # Load memory variables
        variables = self.buffer_memory.load_memory_variables({})
        
        # Check that memory contains the conversation
        self.assertIn("history", variables)
        
        if self.buffer_memory.return_messages:
            messages = variables["history"]
            self.assertEqual(len(messages), 4)
            self.assertEqual(messages[0].content, "Hello, my name is Alice.")
            self.assertEqual(messages[1].content, "Hello Alice! How can I help you today?")
            self.assertEqual(messages[2].content, "I'm interested in learning about AI.")
            self.assertEqual(messages[3].content, "That's great! AI is a fascinating field. What specific aspects are you interested in?")
        else:
            history = variables["history"]
            self.assertIn("Hello, my name is Alice.", history)
            self.assertIn("Hello Alice! How can I help you today?", history)
            self.assertIn("I'm interested in learning about AI.", history)
            self.assertIn("That's great! AI is a fascinating field.", history)
        
        # Update state with memory
        updated_state = dict(self.state)
        updated_state["memory"] = variables
        
        # Check that state contains memory
        self.assertIn("memory", updated_state)
        self.assertIn("history", updated_state["memory"])
    
    def test_conversation_memory_integration(self):
        """Test integration of conversation memory with agent state."""
        # Update memory from state
        for i in range(0, len(self.state["messages"]), 2):
            if i + 1 < len(self.state["messages"]):
                self.conversation_memory.save_context(
                    {"input": self.state["messages"][i].content},
                    {"output": self.state["messages"][i+1].content}
                )
        
        # Load memory variables
        variables = self.conversation_memory.load_memory_variables({})
        
        # Check that memory contains the conversation
        self.assertIn("conversation", variables)
        
        if self.conversation_memory.return_messages:
            messages = variables["conversation"]
            self.assertEqual(len(messages), 4)  # Only the last 2 exchanges (4 messages)
            self.assertEqual(messages[0].content, "Hello, my name is Alice.")
            self.assertEqual(messages[1].content, "Hello Alice! How can I help you today?")
            self.assertEqual(messages[2].content, "I'm interested in learning about AI.")
            self.assertEqual(messages[3].content, "That's great! AI is a fascinating field. What specific aspects are you interested in?")
        else:
            conversation = variables["conversation"]
            self.assertIn("Hello, my name is Alice.", conversation)
            self.assertIn("Hello Alice! How can I help you today?", conversation)
            self.assertIn("I'm interested in learning about AI.", conversation)
            self.assertIn("That's great! AI is a fascinating field.", conversation)
        
        # Update state with memory
        updated_state = dict(self.state)
        updated_state["memory"] = variables
        
        # Check that state contains memory
        self.assertIn("memory", updated_state)
        self.assertIn("conversation", updated_state["memory"])
    
    def test_memory_persistence(self):
        """Test memory persistence."""
        # Update memory from state
        for i in range(0, len(self.state["messages"]), 2):
            if i + 1 < len(self.state["messages"]):
                self.buffer_memory.save_context(
                    {"input": self.state["messages"][i].content},
                    {"output": self.state["messages"][i+1].content}
                )
        
        # Save memory to file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            self.buffer_memory.save(f.name)
            
            # Load memory from file
            loaded_memory = BufferMemory.load(f.name)
            
            # Check that loaded memory contains the conversation
            variables = loaded_memory.load_memory_variables({})
            self.assertIn("history", variables)
            
            if loaded_memory.return_messages:
                messages = variables["history"]
                self.assertEqual(len(messages), 4)
                self.assertEqual(messages[0].content, "Hello, my name is Alice.")
                self.assertEqual(messages[1].content, "Hello Alice! How can I help you today?")
                self.assertEqual(messages[2].content, "I'm interested in learning about AI.")
                self.assertEqual(messages[3].content, "That's great! AI is a fascinating field. What specific aspects are you interested in?")
            else:
                history = variables["history"]
                self.assertIn("Hello, my name is Alice.", history)
                self.assertIn("Hello Alice! How can I help you today?", history)
                self.assertIn("I'm interested in learning about AI.", history)
                self.assertIn("That's great! AI is a fascinating field.", history)
            
            os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
