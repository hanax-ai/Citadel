
"""
AG-UI Protocol - Transport Mechanisms

This module defines the transport mechanisms for the AG-UI protocol, including
Server-Sent Events (SSE) and WebSockets. These transport mechanisms enable
real-time communication between the backend agents and frontend components.

The transport layer abstracts the underlying communication protocols, providing
a consistent interface for sending and receiving AG-UI events regardless of the
transport mechanism used.
"""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Callable, Dict, List, Optional, Union, Any

import aiohttp
from aiohttp import web
import websockets

from .ag_ui import BaseEvent, EventType


class Transport(ABC):
    """
    Abstract base class for AG-UI transport mechanisms.
    
    This class defines the interface that all transport implementations must follow,
    providing methods for sending and receiving AG-UI events.
    """
    
    @abstractmethod
    async def send_event(self, event: BaseEvent) -> None:
        """
        Send an AG-UI event through the transport.
        
        Args:
            event (BaseEvent): The event to send
        """
        pass
    
    @abstractmethod
    async def receive_events(self) -> AsyncGenerator[BaseEvent, None]:
        """
        Receive AG-UI events from the transport.
        
        Yields:
            BaseEvent: The received events
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """
        Close the transport connection.
        """
        pass


class SSETransport(Transport):
    """
    Server-Sent Events (SSE) transport implementation for AG-UI.
    
    SSE provides a unidirectional communication channel from server to client,
    making it suitable for streaming events from agents to UI components.
    """
    
    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize the SSE transport.
        
        Args:
            url (str): The URL of the SSE endpoint
            headers (Optional[Dict[str, str]]): Optional HTTP headers for the connection
        """
        self.url = url
        self.headers = headers or {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.response: Optional[aiohttp.ClientResponse] = None
        self._closed = False
    
    async def connect(self) -> None:
        """
        Establish the SSE connection.
        """
        if self.session is None:
            self.session = aiohttp.ClientSession()
            self.response = await self.session.get(
                self.url,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=None)
            )
    
    async def send_event(self, event: BaseEvent) -> None:
        """
        Send an AG-UI event through the transport.
        
        Note: SSE is unidirectional (server to client), so this method raises an exception.
        Use a bidirectional transport like WebSockets for sending events from client to server.
        
        Args:
            event (BaseEvent): The event to send
            
        Raises:
            NotImplementedError: SSE does not support sending events from client to server
        """
        raise NotImplementedError("SSE transport does not support sending events from client to server")
    
    async def receive_events(self) -> AsyncGenerator[BaseEvent, None]:
        """
        Receive AG-UI events from the SSE stream.
        
        Yields:
            BaseEvent: The received events
        """
        if self.session is None or self.response is None:
            await self.connect()
            
        assert self.response is not None
        
        async for line in self.response.content:
            line = line.decode('utf-8').strip()
            
            if not line:
                continue
                
            if line.startswith('data: '):
                data = line[6:]  # Remove 'data: ' prefix
                try:
                    event_data = json.loads(data)
                    yield BaseEvent.from_dict(event_data)
                except json.JSONDecodeError:
                    # Log error but continue processing events
                    print(f"Error decoding SSE event: {data}")
    
    async def close(self) -> None:
        """
        Close the SSE connection.
        """
        if not self._closed and self.session is not None:
            if self.response is not None:
                self.response.close()
            await self.session.close()
            self._closed = True


class WebSocketTransport(Transport):
    """
    WebSocket transport implementation for AG-UI.
    
    WebSockets provide a bidirectional communication channel between server and client,
    making them suitable for interactive agent-UI communication.
    """
    
    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize the WebSocket transport.
        
        Args:
            url (str): The URL of the WebSocket endpoint
            headers (Optional[Dict[str, str]]): Optional HTTP headers for the connection
        """
        self.url = url
        self.headers = headers or {}
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._closed = False
    
    async def connect(self) -> None:
        """
        Establish the WebSocket connection.
        """
        if self.websocket is None or self.websocket.closed:
            self.websocket = await websockets.connect(
                self.url,
                extra_headers=self.headers
            )
    
    async def send_event(self, event: BaseEvent) -> None:
        """
        Send an AG-UI event through the WebSocket.
        
        Args:
            event (BaseEvent): The event to send
        """
        if self.websocket is None or self.websocket.closed:
            await self.connect()
            
        assert self.websocket is not None
        
        await self.websocket.send(event.to_json())
    
    async def receive_events(self) -> AsyncGenerator[BaseEvent, None]:
        """
        Receive AG-UI events from the WebSocket.
        
        Yields:
            BaseEvent: The received events
        """
        if self.websocket is None or self.websocket.closed:
            await self.connect()
            
        assert self.websocket is not None
        
        while True:
            try:
                message = await self.websocket.recv()
                try:
                    event = BaseEvent.from_json(message)
                    yield event
                except json.JSONDecodeError:
                    # Log error but continue processing events
                    print(f"Error decoding WebSocket message: {message}")
            except websockets.exceptions.ConnectionClosed:
                break
    
    async def close(self) -> None:
        """
        Close the WebSocket connection.
        """
        if not self._closed and self.websocket is not None and not self.websocket.closed:
            await self.websocket.close()
            self._closed = True


class TransportFactory:
    """
    Factory class for creating AG-UI transport instances.
    
    This class provides methods for creating different types of transport instances
    based on the desired transport mechanism.
    """
    
    @staticmethod
    def create_sse_transport(url: str, headers: Optional[Dict[str, str]] = None) -> SSETransport:
        """
        Create an SSE transport instance.
        
        Args:
            url (str): The URL of the SSE endpoint
            headers (Optional[Dict[str, str]]): Optional HTTP headers for the connection
            
        Returns:
            SSETransport: The created SSE transport instance
        """
        return SSETransport(url, headers)
    
    @staticmethod
    def create_websocket_transport(url: str, headers: Optional[Dict[str, str]] = None) -> WebSocketTransport:
        """
        Create a WebSocket transport instance.
        
        Args:
            url (str): The URL of the WebSocket endpoint
            headers (Optional[Dict[str, str]]): Optional HTTP headers for the connection
            
        Returns:
            WebSocketTransport: The created WebSocket transport instance
        """
        return WebSocketTransport(url, headers)


class TransportServer:
    """
    Server-side implementation for AG-UI transports.
    
    This class provides methods for creating SSE and WebSocket endpoints
    that can send and receive AG-UI events.
    """
    
    @staticmethod
    async def create_sse_handler(events_queue: asyncio.Queue) -> web.StreamResponse:
        """
        Create an SSE handler for an aiohttp server.
        
        Args:
            events_queue (asyncio.Queue): Queue of events to send to clients
            
        Returns:
            web.StreamResponse: The SSE response object
        """
        response = web.StreamResponse(
            status=200,
            reason='OK',
            headers={
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',
            }
        )
        
        await response.prepare(web.Request)
        
        try:
            while True:
                event = await events_queue.get()
                message = f"data: {event.to_json()}\n\n"
                await response.write(message.encode('utf-8'))
                await response.drain()
                
                if event.type == EventType.RUN_FINISHED:
                    break
        except ConnectionResetError:
            # Client disconnected
            pass
        
        return response
    
    @staticmethod
    async def websocket_handler(websocket: websockets.WebSocketServerProtocol, 
                               event_callback: Callable[[BaseEvent], None]) -> None:
        """
        Handle WebSocket connections for AG-UI events.
        
        Args:
            websocket (websockets.WebSocketServerProtocol): The WebSocket connection
            event_callback (Callable[[BaseEvent], None]): Callback for received events
        """
        try:
            async for message in websocket:
                try:
                    event = BaseEvent.from_json(message)
                    event_callback(event)
                except json.JSONDecodeError:
                    # Log error but continue processing events
                    print(f"Error decoding WebSocket message: {message}")
        except websockets.exceptions.ConnectionClosed:
            pass
