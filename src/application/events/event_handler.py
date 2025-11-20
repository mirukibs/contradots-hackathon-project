"""EventHandler - Generic interface for handling domain events"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from src.domain.shared.events.domain_event import DomainEvent

T = TypeVar('T', bound=DomainEvent)


class EventHandler(ABC, Generic[T]):
    """
    Generic Event Handler interface for processing domain events.
    
    Event handlers bridge the domain and application layers by reacting
    to domain events and updating projections or triggering side effects.
    """
    
    @abstractmethod
    def handle(self, event: T) -> None:
        """
        Handle a specific domain event.
        
        Args:
            event: The domain event to handle
            
        Raises:
            ValueError: If the event cannot be processed
            RuntimeError: If there are errors during event processing
        """
        pass
    
    @abstractmethod
    def can_handle(self, event: DomainEvent) -> bool:
        """
        Check if this handler can process the given event.
        
        Args:
            event: The domain event to check
            
        Returns:
            True if this handler can process the event, False otherwise
        """
        pass