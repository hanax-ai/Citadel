
"""
Response models for the Citadel API.

This module defines Pydantic models for API response schemas, ensuring proper validation
and documentation of the API contract.
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from uuid import UUID
import time

class WorkflowResponse(BaseModel):
    """Generic response for workflow operations."""
    workflow_id: UUID = Field(..., description="Unique identifier for the workflow")
    status: str = Field(..., description="Status of the workflow")
    message: str = Field(..., description="Response message")

class AgentStatusResponse(BaseModel):
    """Response with the current status of an agent workflow."""
    workflow_id: UUID = Field(..., description="Unique identifier for the workflow")
    status: str = Field(..., description="Status of the workflow")
    config: Dict[str, Any] = Field(..., description="Configuration of the workflow")
    result: Optional[Dict[str, Any]] = Field(None, description="Result of the workflow if completed")
    error: Optional[str] = Field(None, description="Error message if workflow failed")

class AgentEventResponse(BaseModel):
    """Response with an event from an agent workflow."""
    workflow_id: UUID = Field(..., description="Unique identifier for the workflow")
    event_type: str = Field(..., description="Type of the event")
    timestamp: Optional[int] = Field(default_factory=lambda: int(time.time() * 1000), description="Timestamp of the event")
    data: Dict[str, Any] = Field(..., description="Event data")

class GraphDefinitionResponse(BaseModel):
    """Response with information about a graph workflow definition."""
    graph_id: UUID = Field(..., description="Unique identifier for the graph definition")
    name: str = Field(..., description="Name of the graph workflow")
    description: Optional[str] = Field(None, description="Description of the graph workflow")
    node_count: int = Field(..., description="Number of nodes in the graph")
    edge_count: int = Field(..., description="Number of edges in the graph")
    created_at: int = Field(..., description="Timestamp when the graph was created")
    updated_at: Optional[int] = Field(None, description="Timestamp when the graph was last updated")

class GraphStatusResponse(BaseModel):
    """Response with the current status of a graph execution."""
    execution_id: UUID = Field(..., description="Unique identifier for the execution")
    graph_id: UUID = Field(..., description="Unique identifier for the graph definition")
    graph_name: str = Field(..., description="Name of the graph workflow")
    status: str = Field(..., description="Status of the execution")
    config: Dict[str, Any] = Field(..., description="Configuration of the execution")
    result: Optional[Dict[str, Any]] = Field(None, description="Result of the execution if completed")
    error: Optional[str] = Field(None, description="Error message if execution failed")

class GraphEventResponse(BaseModel):
    """Response with an event from a graph execution."""
    workflow_id: UUID = Field(..., description="Unique identifier for the execution")
    event_type: str = Field(..., description="Type of the event")
    timestamp: Optional[int] = Field(default_factory=lambda: int(time.time() * 1000), description="Timestamp of the event")
    data: Dict[str, Any] = Field(..., description="Event data")

class NodeStatusResponse(BaseModel):
    """Response with the status of a node in a graph execution."""
    node_id: str = Field(..., description="Identifier of the node")
    status: str = Field(..., description="Status of the node")
    started_at: Optional[int] = Field(None, description="Timestamp when the node started execution")
    completed_at: Optional[int] = Field(None, description="Timestamp when the node completed execution")
    input: Optional[Dict[str, Any]] = Field(None, description="Input to the node")
    output: Optional[Dict[str, Any]] = Field(None, description="Output from the node")
    error: Optional[str] = Field(None, description="Error message if node execution failed")
