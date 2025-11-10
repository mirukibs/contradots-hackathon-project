"""EventStore - Interface for storing and retrieving domain events"""

from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from src.domain.shared.events.domain_event import DomainEvent


class EventStore(ABC):
    """
    Event Store interface for persisting and retrieving domain events.
    
    This interface provides the contract for event sourcing capabilities,
    allowing events to be stored and retrieved for replay and audit purposes.
    """
    
    @abstractmethod
    def append(self, aggregate_id: UUID, events: List[DomainEvent]) -> None:
        """
        Append events for a specific aggregate to the event store.
        
        Args:
            aggregate_id: The ID of the aggregate that generated the events
            events: List of domain events to store
            
        Raises:
            ValueError: If aggregate_id is invalid or events list is empty
            ConcurrencyError: If there are concurrency conflicts
        """
        pass
    
    @abstractmethod
    def get_events(self, aggregate_id: UUID) -> List[DomainEvent]:
        """
        Get all events for a specific aggregate in chronological order.
        
        Args:
            aggregate_id: The ID of the aggregate to get events for
            
        Returns:
            List of domain events for the aggregate, ordered by occurrence time
        """
        pass
    
    @abstractmethod
    def get_all_events(self) -> List[DomainEvent]:
        """
        Get all events in the event store in chronological order.
        
        Returns:
            List of all domain events, ordered by occurrence time
        """
        pass