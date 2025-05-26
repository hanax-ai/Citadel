
"""
AG-UI Protocol - Event Emitters and Consumers

This module defines the event emitters and consumers for the AG-UI protocol,
providing mechanisms for producing and consuming AG-UI events in an asynchronous manner.

The event system enables bidirectional communication between agents and UI components,
with support for event filtering, transformation, and buffering.
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Set, TypeVar, Generic, Union

from .ag_ui import BaseEvent, EventType
from .transport import Transport


T = TypeVar('T', bound=BaseEvent)


class EventEmitter(ABC):
    """
    Abstract base class for AG-UI event emitters.
    
    Event emitters are responsible for producing AG-UI events and sending them
    to consumers through a transport mechanism.
    """
    
    @abstractmethod
    async def emit(self, event: BaseEvent) -> None:
        """
        Emit an AG-UI event.
        
        Args:
            event (BaseEvent): The event to emit
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """
        Close the event emitter and release any resources.
        """
        pass


class EventConsumer(ABC, Generic[T]):
    """
    Abstract base class for AG-UI event consumers.
    
    Event consumers are responsible for receiving and processing AG-UI events
    from a transport mechanism.
    """
    
    @abstractmethod
    async def consume(self) -> AsyncGenerator[T, None]:
        """
        Consume AG-UI events.
        
        Yields:
            T: The consumed events
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """
        Close the event consumer and release any resources.
        """
        pass


class TransportEventEmitter(EventEmitter):
    """
    Event emitter implementation that uses a transport mechanism.
    
    This emitter sends events through a specified transport, such as SSE or WebSockets.
    """
    
    def __init__(self, transport: Transport):
        """
        Initialize the transport event emitter.
        
        Args:
            transport (Transport): The transport to use for sending events
        """
        self.transport = transport
    
    async def emit(self, event: BaseEvent) -> None:
        """
        Emit an AG-UI event through the transport.
        
        Args:
            event (BaseEvent): The event to emit
        """
        await self.transport.send_event(event)
    
    async def close(self) -> None:
        """
        Close the event emitter and the underlying transport.
        """
        await self.transport.close()


class TransportEventConsumer(EventConsumer[T]):
    """
    Event consumer implementation that uses a transport mechanism.
    
    This consumer receives events from a specified transport, such as SSE or WebSockets,
    with optional filtering by event type.
    """
    
    def __init__(self, transport: Transport, event_types: Optional[Set[EventType]] = None):
        """
        Initialize the transport event consumer.
        
        Args:
            transport (Transport): The transport to use for receiving events
            event_types (Optional[Set[EventType]]): Optional set of event types to filter by
        """
        self.transport = transport
        self.event_types = event_types
    
    async def consume(self) -> AsyncGenerator[T, None]:
        """
        Consume AG-UI events from the transport, optionally filtered by event type.
        
        Yields:
            T: The consumed events
        """
        async for event in self.transport.receive_events():
            if self.event_types is None or event.type in self.event_types:
                yield event  # type: ignore
    
    async def close(self) -> None:
        """
        Close the event consumer and the underlying transport.
        """
        await self.transport.close()


class QueueEventEmitter(EventEmitter):
    """
    Event emitter implementation that uses an asyncio queue.
    
    This emitter is useful for in-process communication between components,
    without the need for a network transport.
    """
    
    def __init__(self, queue: Optional[asyncio.Queue[BaseEvent]] = None):
        """
        Initialize the queue event emitter.
        
        Args:
            queue (Optional[asyncio.Queue[BaseEvent]]): Optional queue to use for events
        """
        self.queue = queue or asyncio.Queue()
    
    async def emit(self, event: BaseEvent) -> None:
        """
        Emit an AG-UI event to the queue.
        
        Args:
            event (BaseEvent): The event to emit
        """
        await self.queue.put(event)
    
    async def close(self) -> None:
        """
        Close the event emitter.
        
        For queue-based emitters, this is a no-op as there are no resources to release.
        """
        pass
    
    def get_queue(self) -> asyncio.Queue[BaseEvent]:
        """
        Get the underlying queue.
        
        Returns:
            asyncio.Queue[BaseEvent]: The queue used by this emitter
        """
        return self.queue


class QueueEventConsumer(EventConsumer[T]):
    """
    Event consumer implementation that uses an asyncio queue.
    
    This consumer is useful for in-process communication between components,
    without the need for a network transport.
    """
    
    def __init__(self, queue: asyncio.Queue[BaseEvent], event_types: Optional[Set[EventType]] = None):
        """
        Initialize the queue event consumer.
        
        Args:
            queue (asyncio.Queue[BaseEvent]): The queue to consume events from
            event_types (Optional[Set[EventType]]): Optional set of event types to filter by
        """
        self.queue = queue
        self.event_types = event_types
    
    async def consume(self) -> AsyncGenerator[T, None]:
        """
        Consume AG-UI events from the queue, optionally filtered by event type.
        
        Yields:
            T: The consumed events
        """
        while True:
            event = await self.queue.get()
            self.queue.task_done()
            
            if self.event_types is None or event.type in self.event_types:
                yield event  # type: ignore
    
    async def close(self) -> None:
        """
        Close the event consumer.
        
        For queue-based consumers, this is a no-op as there are no resources to release.
        """
        pass


class EventBus:
    """
    Central event bus for AG-UI events.
    
    The event bus provides a centralized mechanism for publishing and subscribing to
    AG-UI events, with support for multiple subscribers and event filtering.
    """
    
    def __init__(self):
        """
        Initialize the event bus.
        """
        self.subscribers: Dict[Optional[Set[EventType]], List[asyncio.Queue[BaseEvent]]] = {}
    
    async def publish(self, event: BaseEvent) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event (BaseEvent): The event to publish
        """
        for event_types, queues in self.subscribers.items():
            if event_types is None or event.type in event_types:
                for queue in queues:
                    await queue.put(event)
    
    def subscribe(self, event_types: Optional[Set[EventType]] = None) -> QueueEventConsumer[BaseEvent]:
        """
        Subscribe to events, optionally filtered by event type.
        
        Args:
            event_types (Optional[Set[EventType]]): Optional set of event types to filter by
            
        Returns:
            QueueEventConsumer[BaseEvent]: Event consumer for the subscription
        """
        queue: asyncio.Queue[BaseEvent] = asyncio.Queue()
        
        if event_types not in self.subscribers:
            self.subscribers[event_types] = []
            
        self.subscribers[event_types].append(queue)
        
        return QueueEventConsumer(queue, event_types)
    
    def unsubscribe(self, consumer: QueueEventConsumer[BaseEvent]) -> None:
        """
        Unsubscribe from events.
        
        Args:
            consumer (QueueEventConsumer[BaseEvent]): The consumer to unsubscribe
        """
        for event_types, queues in self.subscribers.items():
            if consumer.queue in queues:
                queues.remove(consumer.queue)
                
                if not queues:
                    del self.subscribers[event_types]
                    
                break


class EventProcessor:
    """
    Processor for transforming and filtering AG-UI events.
    
    The event processor provides a way to transform and filter events between
    an event consumer and an event emitter, enabling complex event processing pipelines.
    """
    
    def __init__(self, 
                consumer: EventConsumer[BaseEvent], 
                emitter: EventEmitter,
                transform_fn: Optional[Callable[[BaseEvent], Optional[BaseEvent]]] = None):
        """
        Initialize the event processor.
        
        Args:
            consumer (EventConsumer[BaseEvent]): The event consumer to process events from
            emitter (EventEmitter): The event emitter to send processed events to
            transform_fn (Optional[Callable[[BaseEvent], Optional[BaseEvent]]]): Optional function
                to transform events. If it returns None, the event is filtered out.
        """
        self.consumer = consumer
        self.emitter = emitter
        self.transform_fn = transform_fn
        self.task: Optional[asyncio.Task] = None
    
    async def process_events(self) -> None:
        """
        Process events from the consumer and send them to the emitter.
        """
        async for event in self.consumer.consume():
            if self.transform_fn:
                transformed_event = self.transform_fn(event)
                if transformed_event:
                    await self.emitter.emit(transformed_event)
            else:
                await self.emitter.emit(event)
    
    def start(self) -> None:
        """
        Start processing events in the background.
        """
        if self.task is None or self.task.done():
            self.task = asyncio.create_task(self.process_events())
    
    async def stop(self) -> None:
        """
        Stop processing events and close the consumer and emitter.
        """
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            
        await self.consumer.close()
        await self.emitter.close()


class EventManager:
    """
    Manager for coordinating AG-UI events across multiple components.
    
    The event manager provides a centralized mechanism for creating and managing
    event emitters, consumers, and processors, with support for event routing and
    lifecycle management.
    """
    
    def __init__(self):
        """
        Initialize the event manager.
        """
        self.event_bus = EventBus()
        self.processors: List[EventProcessor] = []
        self.run_id = str(uuid.uuid4())
    
    async def start_run(self) -> None:
        """
        Start a new agent run with a unique ID.
        """
        self.run_id = str(uuid.uuid4())
        await self.event_bus.publish(BaseEvent(
            type=EventType.RUN_STARTED,
            payload={"runId": self.run_id}
        ))
    
    async def end_run(self) -> None:
        """
        End the current agent run.
        """
        await self.event_bus.publish(BaseEvent(
            type=EventType.RUN_FINISHED,
            payload={"runId": self.run_id}
        ))
    
    def create_emitter(self) -> EventEmitter:
        """
        Create an event emitter that publishes to the event bus.
        
        Returns:
            EventEmitter: The created event emitter
        """
        queue_emitter = QueueEventEmitter()
        
        processor = EventProcessor(
            QueueEventConsumer(queue_emitter.get_queue()),
            TransportEventEmitter(self.event_bus)
        )
        
        processor.start()
        self.processors.append(processor)
        
        return queue_emitter
    
    def create_consumer(self, event_types: Optional[Set[EventType]] = None) -> EventConsumer[BaseEvent]:
        """
        Create an event consumer that subscribes to the event bus.
        
        Args:
            event_types (Optional[Set[EventType]]): Optional set of event types to filter by
            
        Returns:
            EventConsumer[BaseEvent]: The created event consumer
        """
        return self.event_bus.subscribe(event_types)
    
    async def close(self) -> None:
        """
        Close the event manager and all associated processors.
        """
        for processor in self.processors:
            await processor.stop()
            
        self.processors.clear()
