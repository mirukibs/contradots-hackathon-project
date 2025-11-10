"""
DomainEvent base class for the Social Scoring System.
Abstract base class for all domain events in the system.
"""
import uuid
from datetime import datetime
from abc import ABC
from typing import Any


class DomainEvent(ABC):
    """Abstract base class for all domain events."""
    
    def __init__(
        self, 
        event_id: uuid.UUID,
        occurred_at: datetime,
        aggregate_id: uuid.UUID,
        aggregate_type: str
    ) -> None:
        self._event_id = event_id
        self._occurred_at = occurred_at
        self._aggregate_id = aggregate_id
        self._aggregate_type = aggregate_type
    
    @property
    def event_id(self) -> uuid.UUID:
        """Unique identifier for this event."""
        return self._event_id
    
    @property
    def occurred_at(self) -> datetime:
        """When this event occurred."""
        return self._occurred_at
    
    @property
    def aggregate_id(self) -> uuid.UUID:
        """ID of the aggregate that generated this event."""
        return self._aggregate_id
    
    @property
    def aggregate_type(self) -> str:
        """Type of the aggregate that generated this event."""
        return self._aggregate_type
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, DomainEvent):
            return False
        return self._event_id == other._event_id
    
    def __hash__(self) -> int:
        return hash(self._event_id)
    
    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(event_id={self._event_id!r}, "
                f"occurred_at={self._occurred_at!r}, aggregate_id={self._aggregate_id!r}, "
                f"aggregate_type={self._aggregate_type!r})")