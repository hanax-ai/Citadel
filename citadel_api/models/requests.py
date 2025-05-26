
"""
Request models for the Citadel API.

This module defines Pydantic models for API request schemas, ensuring proper validation
and documentation of the API contract.
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional, Union
from uuid import UUID
import re

class AgentConfig(BaseModel):
    """Configuration for an agent workflow."""
    model: str = Field(..., description="The language model to use for the agent")
    temperature: float = Field(0.7, description="Temperature for model generation")
    max_tokens: int = Field(1000, description="Maximum tokens for model generation")
    tools: List[Dict[str, Any]] = Field(default_factory=list, description="Tools available to the agent")
    memory: Optional[Dict[str, Any]] = Field(None, description="Memory configuration for the agent")
    system_prompt: Optional[str] = Field(None, description="System prompt for the agent")
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if v < 0 or v > 2:
            raise ValueError('Temperature must be between 0 and 2')
        return v

class StartAgentWorkflowRequest(BaseModel):
    """Request to start a new agent workflow."""
    config: AgentConfig = Field(..., description="Configuration for the agent workflow")
    input: Dict[str, Any] = Field(..., description="Initial input for the workflow")

class AgentActionRequest(BaseModel):
    """Request to submit an action to an agent workflow."""
    action_type: str = Field(..., description="Type of action to submit")
    action_data: Dict[str, Any] = Field(..., description="Data for the action")

class AgentFeedbackRequest(BaseModel):
    """Request to submit feedback to an agent workflow."""
    feedback_type: str = Field(..., description="Type of feedback to submit")
    feedback_data: Dict[str, Any] = Field(..., description="Data for the feedback")

class AgentSubscriptionRequest(BaseModel):
    """Request to subscribe to agent workflow events."""
    event_types: Optional[List[str]] = Field(None, description="Types of events to subscribe to")

class GraphNodeDefinition(BaseModel):
    """Definition of a node in a graph workflow."""
    id: str = Field(..., description="Unique identifier for the node")
    type: str = Field(..., description="Type of the node")
    config: Dict[str, Any] = Field(..., description="Configuration for the node")
    
    @validator('id')
    def validate_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Node ID must contain only alphanumeric characters, underscores, and hyphens')
        return v

class GraphEdgeDefinition(BaseModel):
    """Definition of an edge in a graph workflow."""
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    condition: Optional[Dict[str, Any]] = Field(None, description="Condition for the edge")

class CreateGraphRequest(BaseModel):
    """Request to create a new graph workflow definition."""
    name: str = Field(..., description="Name of the graph workflow")
    description: Optional[str] = Field(None, description="Description of the graph workflow")
    nodes: List[GraphNodeDefinition] = Field(..., description="Nodes in the graph")
    edges: List[GraphEdgeDefinition] = Field(..., description="Edges in the graph")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the graph")
    
    @validator('nodes')
    def validate_nodes(cls, v):
        if not v:
            raise ValueError('Graph must have at least one node')
        
        # Check for duplicate node IDs
        node_ids = [node.id for node in v]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError('Node IDs must be unique')
        
        return v
    
    @validator('edges')
    def validate_edges(cls, v, values):
        if 'nodes' not in values:
            return v
        
        node_ids = [node.id for node in values['nodes']]
        
        # Check that edge source and target nodes exist
        for edge in v:
            if edge.source not in node_ids:
                raise ValueError(f'Edge source node {edge.source} does not exist')
            if edge.target not in node_ids:
                raise ValueError(f'Edge target node {edge.target} does not exist')
        
        return v

class UpdateGraphRequest(BaseModel):
    """Request to update an existing graph workflow definition."""
    name: Optional[str] = Field(None, description="Updated name of the graph workflow")
    description: Optional[str] = Field(None, description="Updated description of the graph workflow")
    nodes: List[GraphNodeDefinition] = Field(..., description="Updated nodes in the graph")
    edges: List[GraphEdgeDefinition] = Field(..., description="Updated edges in the graph")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata for the graph")
    
    @validator('nodes')
    def validate_nodes(cls, v):
        if not v:
            raise ValueError('Graph must have at least one node')
        
        # Check for duplicate node IDs
        node_ids = [node.id for node in v]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError('Node IDs must be unique')
        
        return v
    
    @validator('edges')
    def validate_edges(cls, v, values):
        if 'nodes' not in values:
            return v
        
        node_ids = [node.id for node in values['nodes']]
        
        # Check that edge source and target nodes exist
        for edge in v:
            if edge.source not in node_ids:
                raise ValueError(f'Edge source node {edge.source} does not exist')
            if edge.target not in node_ids:
                raise ValueError(f'Edge target node {edge.target} does not exist')
        
        return v

class ExecuteGraphRequest(BaseModel):
    """Request to execute a graph workflow."""
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuration for the execution")
    input: Dict[str, Any] = Field(..., description="Initial input for the workflow")

class GraphSubscriptionRequest(BaseModel):
    """Request to subscribe to graph workflow events."""
    event_types: Optional[List[str]] = Field(None, description="Types of events to subscribe to")
