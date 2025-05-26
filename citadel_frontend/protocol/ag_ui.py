
"""
AG-UI Protocol - Event Types and Base Event Class

This module defines the standardized event types and base event class for the AG-UI protocol,
which serves as the communication layer between AI backend agents and frontend applications
in Project Citadel.

The AG-UI protocol provides a lightweight, event-driven architecture for agent-UI communication
with standardized event types for message streaming, tool calls, state updates, and lifecycle signals.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict, Union
import json
from dataclasses import dataclass, asdict, field


class EventType(Enum):
    """
    Enumeration of standardized AG-UI event types for agent-UI communication.
    
    These event types cover the full spectrum of interactions between agents and UI components,
    including conversation messages, tool execution, state management, and lifecycle events.
    """
    # Run lifecycle events
    RUN_STARTED = "RUN_STARTED"
    RUN_FINISHED = "RUN_FINISHED"
    
    # Text message events
    TEXT_MESSAGE_START = "TEXT_MESSAGE_START"
    TEXT_MESSAGE_CONTENT = "TEXT_MESSAGE_CONTENT"
    TEXT_MESSAGE_END = "TEXT_MESSAGE_END"
    
    # Tool execution events
    TOOL_CALL_START = "TOOL_CALL_START"
    TOOL_CALL_ARGS = "TOOL_CALL_ARGS"
    TOOL_CALL_END = "TOOL_CALL_END"
    
    # State management events
    STATE_SNAPSHOT = "STATE_SNAPSHOT"
    STATE_DELTA = "STATE_DELTA"
    MESSAGES_SNAPSHOT = "MESSAGES_SNAPSHOT"
    
    # Error and status events
    ERROR = "ERROR"
    STATUS_UPDATE = "STATUS_UPDATE"
    
    # Additional events for enhanced functionality
    THINKING_START = "THINKING_START"
    THINKING_END = "THINKING_END"
    AGENT_CHANGE = "AGENT_CHANGE"


class JSONPatch(TypedDict):
    """
    JSON Patch operation as defined in RFC 6902.
    
    Used for incremental state updates in STATE_DELTA events.
    """
    op: str  # "add", "remove", "replace", "move", "copy", or "test"
    path: str  # JSON Pointer (RFC 6901) to the target location
    value: Optional[Any]  # The value to add, replace, or test
    from_: Optional[str]  # Source location for "move" and "copy" operations


@dataclass
class BaseEvent:
    """
    Base class for all AG-UI protocol events.
    
    All events in the AG-UI protocol inherit from this class, providing a consistent
    structure for event handling and serialization/deserialization.
    """
    type: EventType
    payload: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the event
        """
        result = asdict(self)
        result["type"] = self.type.value
        return result
    
    def to_json(self) -> str:
        """
        Convert the event to a JSON string.
        
        Returns:
            str: JSON string representation of the event
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEvent':
        """
        Create an event from a dictionary representation.
        
        Args:
            data (Dict[str, Any]): Dictionary representation of the event
            
        Returns:
            BaseEvent: Instantiated event object
        """
        event_type = EventType(data["type"])
        payload = data.get("payload", {})
        return cls(type=event_type, payload=payload)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BaseEvent':
        """
        Create an event from a JSON string.
        
        Args:
            json_str (str): JSON string representation of the event
            
        Returns:
            BaseEvent: Instantiated event object
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


# Specialized event classes for specific event types

@dataclass
class RunStartedEvent(BaseEvent):
    """Event indicating the start of an agent execution."""
    def __init__(self, run_id: str):
        super().__init__(
            type=EventType.RUN_STARTED,
            payload={"runId": run_id}
        )


@dataclass
class RunFinishedEvent(BaseEvent):
    """Event indicating the completion of an agent execution."""
    def __init__(self, run_id: str):
        super().__init__(
            type=EventType.RUN_FINISHED,
            payload={"runId": run_id}
        )


@dataclass
class TextMessageStartEvent(BaseEvent):
    """Event indicating the start of a new message in the conversation."""
    def __init__(self, message_id: str, sender: str):
        super().__init__(
            type=EventType.TEXT_MESSAGE_START,
            payload={"messageId": message_id, "sender": sender}
        )


@dataclass
class TextMessageContentEvent(BaseEvent):
    """Event containing streamed content for the current message."""
    def __init__(self, message_id: str, content: str):
        super().__init__(
            type=EventType.TEXT_MESSAGE_CONTENT,
            payload={"messageId": message_id, "content": content}
        )


@dataclass
class TextMessageEndEvent(BaseEvent):
    """Event indicating the completion of the current message."""
    def __init__(self, message_id: str):
        super().__init__(
            type=EventType.TEXT_MESSAGE_END,
            payload={"messageId": message_id}
        )


@dataclass
class ToolCallStartEvent(BaseEvent):
    """Event indicating the start of a tool execution."""
    def __init__(self, tool_call_id: str, tool: str):
        super().__init__(
            type=EventType.TOOL_CALL_START,
            payload={"toolCallId": tool_call_id, "tool": tool}
        )


@dataclass
class ToolCallArgsEvent(BaseEvent):
    """Event providing arguments for the tool call."""
    def __init__(self, tool_call_id: str, args: Dict[str, Any]):
        super().__init__(
            type=EventType.TOOL_CALL_ARGS,
            payload={"toolCallId": tool_call_id, "args": args}
        )


@dataclass
class ToolCallEndEvent(BaseEvent):
    """Event indicating the completion of the tool execution with results."""
    def __init__(self, tool_call_id: str, result: Dict[str, Any]):
        super().__init__(
            type=EventType.TOOL_CALL_END,
            payload={"toolCallId": tool_call_id, "result": result}
        )


@dataclass
class StateSnapshotEvent(BaseEvent):
    """Event providing a complete state snapshot."""
    def __init__(self, state: Dict[str, Any]):
        super().__init__(
            type=EventType.STATE_SNAPSHOT,
            payload={"state": state}
        )


@dataclass
class StateDeltaEvent(BaseEvent):
    """Event providing incremental state updates using JSON Patch."""
    def __init__(self, patch: List[JSONPatch]):
        super().__init__(
            type=EventType.STATE_DELTA,
            payload={"patch": patch}
        )


@dataclass
class ErrorEvent(BaseEvent):
    """Event indicating an error occurred during agent execution."""
    def __init__(self, error_code: str, message: str, details: Optional[Dict[str, Any]] = None):
        payload = {"errorCode": error_code, "message": message}
        if details:
            payload["details"] = details
        super().__init__(
            type=EventType.ERROR,
            payload=payload
        )
