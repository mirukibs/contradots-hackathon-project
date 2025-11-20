"""EventPublisher - Interface for publishing domain events to handlers"""

from abc import ABC, abstractmethod
from typing import List
from src.domain.shared.events.domain_event import DomainEvent
from src.application.events.event_store import EventStore
from src.application.events.event_handler import EventHandler


class EventPublisher(ABC):
    """
    Event Publisher interface for distributing domain events to handlers.
    
    The EventPublisher coordinates the distribution of domain events
    to registered event handlers and persists events to the event store.
    """
    
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """
        Publish a single domain event to all registered handlers.
        
        Args:
            event: The domain event to publish
            
        Raises:
            ValueError: If event is invalid
            RuntimeError: If publishing fails
        """
        pass
    
    @abstractmethod
    def publish_all(self, events: List[DomainEvent]) -> None:
        """
        Publish multiple domain events to all registered handlers.
        
        Args:
            events: List of domain events to publish
            
        Raises:
            ValueError: If events list is invalid
            RuntimeError: If publishing fails
        """
        pass
    
    @property
    @abstractmethod
    def event_store(self) -> EventStore:
        """Get the event store used by this publisher."""
        pass
    
    @property
    @abstractmethod
    def handlers(self) -> List[EventHandler[DomainEvent]]:
        """Get the list of registered event handlers."""
        pass