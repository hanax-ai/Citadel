
"""
Tests for the tools module.
"""

import unittest
import os
import json
from unittest.mock import MagicMock, patch

from citadel_langgraph.tools import (
    ToolRegistry,
    ToolSelectionStrategy,
    WebSearchTool,
    CalculatorTool,
    FileOperationTool,
)
from citadel_langgraph.tools.tool_registry import (
    BaseTool,
    AllToolsStrategy,
    TaskBasedToolStrategy,
    DynamicToolStrategy,
)
from citadel_langgraph.state.agent_state import ReActAgentState


class TestToolRegistry(unittest.TestCase):
    """Test the ToolRegistry class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = ToolRegistry()
        
        # Create mock tools
        self.mock_tool1 = MagicMock(spec=BaseTool)
        self.mock_tool1.name = "tool1"
        self.mock_tool1.description = "Tool 1 description"
        self.mock_tool1.to_dict.return_value = {
            "name": "tool1",
            "description": "Tool 1 description",
        }
        
        self.mock_tool2 = MagicMock(spec=BaseTool)
        self.mock_tool2.name = "tool2"
        self.mock_tool2.description = "Tool 2 description"
        self.mock_tool2.to_dict.return_value = {
            "name": "tool2",
            "description": "Tool 2 description",
        }
    
    def test_register_tool(self):
        """Test registering a tool."""
        self.registry.register_tool(self.mock_tool1)
        self.assertEqual(len(self.registry.get_all_tools()), 1)
        self.assertEqual(self.registry.get_tool("tool1"), self.mock_tool1)
    
    def test_register_tools(self):
        """Test registering multiple tools."""
        self.registry.register_tools([self.mock_tool1, self.mock_tool2])
        self.assertEqual(len(self.registry.get_all_tools()), 2)
        self.assertEqual(self.registry.get_tool("tool1"), self.mock_tool1)
        self.assertEqual(self.registry.get_tool("tool2"), self.mock_tool2)
    
    def test_get_tool_descriptions(self):
        """Test getting tool descriptions."""
        self.registry.register_tools([self.mock_tool1, self.mock_tool2])
        descriptions = self.registry.get_tool_descriptions()
        self.assertEqual(len(descriptions), 2)
        self.assertEqual(descriptions[0]["name"], "tool1")
        self.assertEqual(descriptions[1]["name"], "tool2")
    
    def test_execute_tool(self):
        """Test executing a tool."""
        self.mock_tool1.return_value = "Tool 1 result"
        self.registry.register_tool(self.mock_tool1)
        
        result = self.registry.execute_tool("tool1", arg1="value1")
        
        self.mock_tool1.assert_called_once_with(arg1="value1")
        self.assertEqual(result, "Tool 1 result")
    
    def test_execute_nonexistent_tool(self):
        """Test executing a nonexistent tool."""
        with self.assertRaises(ValueError):
            self.registry.execute_tool("nonexistent_tool")


class TestToolSelectionStrategies(unittest.TestCase):
    """Test the tool selection strategies."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = ToolRegistry()
        
        # Create mock tools
        self.mock_tool1 = MagicMock(spec=BaseTool)
        self.mock_tool1.name = "web_search"
        self.mock_tool1.description = "Search the web"
        self.mock_tool1.to_dict.return_value = {
            "name": "web_search",
            "description": "Search the web",
        }
        
        self.mock_tool2 = MagicMock(spec=BaseTool)
        self.mock_tool2.name = "calculator"
        self.mock_tool2.description = "Perform calculations"
        self.mock_tool2.to_dict.return_value = {
            "name": "calculator",
            "description": "Perform calculations",
        }
        
        self.mock_tool3 = MagicMock(spec=BaseTool)
        self.mock_tool3.name = "file_operation"
        self.mock_tool3.description = "Perform file operations"
        self.mock_tool3.to_dict.return_value = {
            "name": "file_operation",
            "description": "Perform file operations",
        }
        
        self.registry.register_tools([self.mock_tool1, self.mock_tool2, self.mock_tool3])
        
        # Create mock state
        self.state = MagicMock(spec=ReActAgentState)
        self.state.get.return_value = [
            MagicMock(type="human", content="Search for information about AI")
        ]
    
    def test_all_tools_strategy(self):
        """Test the AllToolsStrategy."""
        strategy = AllToolsStrategy(self.registry)
        selected_tools = strategy.select_tools(self.state)
        
        self.assertEqual(len(selected_tools), 3)
        self.assertEqual(selected_tools[0]["name"], "web_search")
        self.assertEqual(selected_tools[1]["name"], "calculator")
        self.assertEqual(selected_tools[2]["name"], "file_operation")
    
    def test_task_based_strategy(self):
        """Test the TaskBasedToolStrategy."""
        task_tool_mapping = {
            "search": ["web_search"],
            "calculate": ["calculator"],
            "file": ["file_operation"],
        }
        
        strategy = TaskBasedToolStrategy(
            self.registry,
            task_tool_mapping,
            default_tools=["calculator"],
        )
        
        selected_tools = strategy.select_tools(self.state)
        
        # Should include web_search (from task) and calculator (default)
        self.assertEqual(len(selected_tools), 2)
        tool_names = [tool["name"] for tool in selected_tools]
        self.assertIn("web_search", tool_names)
        self.assertIn("calculator", tool_names)
    
    def test_dynamic_strategy(self):
        """Test the DynamicToolStrategy."""
        def selection_function(state, tools):
            # Simple function that always selects web_search
            return ["web_search"]
        
        strategy = DynamicToolStrategy(self.registry, selection_function)
        selected_tools = strategy.select_tools(self.state)
        
        self.assertEqual(len(selected_tools), 1)
        self.assertEqual(selected_tools[0]["name"], "web_search")


class TestWebSearchTool(unittest.TestCase):
    """Test the WebSearchTool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = WebSearchTool()
    
    def test_tool_metadata(self):
        """Test the tool metadata."""
        self.assertEqual(self.tool.name, "web_search")
        self.assertTrue("search" in self.tool.description.lower())
    
    def test_tool_execution(self):
        """Test executing the tool."""
        results = self.tool("test query")
        
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0)
        self.assertIn("title", results[0])
        self.assertIn("link", results[0])
        self.assertIn("snippet", results[0])
    
    def test_to_dict(self):
        """Test converting the tool to a dictionary."""
        tool_dict = self.tool.to_dict()
        
        self.assertEqual(tool_dict["name"], "web_search")
        self.assertTrue("description" in tool_dict)
        self.assertTrue("parameters" in tool_dict)
        self.assertTrue("query" in tool_dict["parameters"])


class TestCalculatorTool(unittest.TestCase):
    """Test the CalculatorTool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = CalculatorTool()
    
    def test_tool_metadata(self):
        """Test the tool metadata."""
        self.assertEqual(self.tool.name, "calculator")
        self.assertTrue("calculation" in self.tool.description.lower())
    
    def test_simple_calculation(self):
        """Test a simple calculation."""
        result = self.tool("2 + 2")
        
        self.assertEqual(result["expression"], "2 + 2")
        self.assertEqual(result["result"], 4)
    
    def test_complex_calculation(self):
        """Test a more complex calculation."""
        result = self.tool("math.sin(math.pi/2)")
        
        self.assertEqual(result["expression"], "math.sin(math.pi/2)")
        self.assertAlmostEqual(result["result"], 1.0)
    
    def test_invalid_expression(self):
        """Test an invalid expression."""
        result = self.tool("invalid expression")
        
        self.assertEqual(result["expression"], "invalid expression")
        self.assertTrue("error" in result)
    
    def test_to_dict(self):
        """Test converting the tool to a dictionary."""
        tool_dict = self.tool.to_dict()
        
        self.assertEqual(tool_dict["name"], "calculator")
        self.assertTrue("description" in tool_dict)
        self.assertTrue("parameters" in tool_dict)
        self.assertTrue("expression" in tool_dict["parameters"])


class TestFileOperationTool(unittest.TestCase):
    """Test the FileOperationTool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = "/tmp/citadel_test_files"
        os.makedirs(self.test_dir, exist_ok=True)
        self.tool = FileOperationTool(base_directory=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_tool_metadata(self):
        """Test the tool metadata."""
        self.assertEqual(self.tool.name, "file_operation")
        self.assertTrue("file" in self.tool.description.lower())
    
    def test_write_and_read_file(self):
        """Test writing and reading a file."""
        # Write a file
        write_result = self.tool(
            operation="write",
            path="test.txt",
            content="Hello, world!",
        )
        
        self.assertTrue(write_result["success"])
        
        # Read the file
        read_result = self.tool(
            operation="read",
            path="test.txt",
        )
        
        self.assertEqual(read_result["content"], "Hello, world!")
    
    def test_list_files(self):
        """Test listing files."""
        # Create some files
        self.tool(operation="write", path="file1.txt", content="Content 1")
        self.tool(operation="write", path="file2.txt", content="Content 2")
        
        # List files
        list_result = self.tool(operation="list")
        
        self.assertEqual(list_result["operation"], "list")
        self.assertTrue("files" in list_result)
        self.assertEqual(len(list_result["files"]), 2)
        
        file_names = [file["name"] for file in list_result["files"]]
        self.assertIn("file1.txt", file_names)
        self.assertIn("file2.txt", file_names)
    
    def test_file_exists(self):
        """Test checking if a file exists."""
        # Create a file
        self.tool(operation="write", path="exists_test.txt", content="Content")
        
        # Check if file exists
        exists_result = self.tool(operation="exists", path="exists_test.txt")
        
        self.assertEqual(exists_result["operation"], "exists")
        self.assertTrue(exists_result["exists"])
        self.assertFalse(exists_result["is_directory"])
        
        # Check if nonexistent file exists
        not_exists_result = self.tool(operation="exists", path="nonexistent.txt")
        
        self.assertEqual(not_exists_result["operation"], "exists")
        self.assertFalse(not_exists_result["exists"])
    
    def test_to_dict(self):
        """Test converting the tool to a dictionary."""
        tool_dict = self.tool.to_dict()
        
        self.assertEqual(tool_dict["name"], "file_operation")
        self.assertTrue("description" in tool_dict)
        self.assertTrue("parameters" in tool_dict)
        self.assertTrue("operation" in tool_dict["parameters"])
        self.assertTrue("path" in tool_dict["parameters"])
        self.assertTrue("content" in tool_dict["parameters"])


if __name__ == "__main__":
    unittest.main()
