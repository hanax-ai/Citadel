
"""
Test script for UI events in LangGraph.
"""

import asyncio
from citadel_langgraph.state.ui_state import (
    UIState, UIAgentState, create_ui_state, create_ui_agent_state, emit_state_update
)
from citadel_langgraph.events.emitter import (
    start_run, end_run, emit_node_start, emit_node_end,
    emit_tool_call_start, emit_tool_call_args, emit_tool_call_end,
    emit_message_start, emit_message_content, emit_message_end
)
from citadel_frontend.protocol.events import EventManager, QueueEventConsumer
from citadel_frontend.protocol.ag_ui import EventType
from langchain_core.messages import HumanMessage, AIMessage

async def main():
    # Create a state
    print("Creating UI state...")
    state = create_ui_agent_state(
        system_message="You are a helpful assistant.",
        tools=[{"name": "search", "description": "Search the web"}],
        metadata={"test": True}
    )
    print(f"State created: {state}")
    
    # Start a run
    print("Starting run...")
    run_id = start_run()
    print(f"Run started with ID: {run_id}")
    
    # Set up an event consumer to monitor events
    event_manager = EventManager()
    consumer = event_manager.create_consumer()
    
    # Start consuming events in the background
    async def print_events():
        async for event in consumer.consume():
            print(f"Received event: {event.type.value}, payload: {event.payload}")
    
    task = asyncio.create_task(print_events())
    
    # Emit some events
    print("Emitting node start event...")
    emit_node_start("test_node", state)
    
    # Add a message
    print("Adding a human message...")
    state["messages"] = [HumanMessage(content="Hello, how are you?")]
    emit_state_update(state)
    
    # Emit a tool call
    print("Emitting tool call events...")
    tool_call_id = emit_tool_call_start("search")
    emit_tool_call_args(tool_call_id, {"query": "test query"})
    emit_tool_call_end(tool_call_id, {"result": "test result"})
    
    # Emit a message
    print("Emitting message events...")
    message_id = emit_message_start(sender="agent")
    emit_message_content(message_id, "Hello, I'm doing well. How can I help you today?")
    emit_message_end(message_id)
    
    # Add an AI message
    print("Adding an AI message...")
    state["messages"].append(AIMessage(content="I'm here to help!"))
    emit_state_update(state)
    
    # Emit node end event
    print("Emitting node end event...")
    emit_node_end("test_node", state)
    
    # End the run
    print("Ending run...")
    end_run()
    
    # Wait for events to be processed
    await asyncio.sleep(1)
    
    # Cancel the event consumer task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    
    print("Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
