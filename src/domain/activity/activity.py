"""
Activity aggregate root implementation.
Implements the Activity entity as specified in the domain model.
"""

from datetime import datetime, timezone
from typing import List, Optional

from ..shared.value_objects.activity_id import ActivityId
from ..shared.value_objects.person_id import PersonId
from ..shared.domain_events import DomainEvent


class Activity:
    """
    Activity aggregate root.
    
    Represents an activity that can be created by administrators and contains
    actions submitted by persons within the domain.
    """
    
    def __init__(
        self,
        activity_id: ActivityId,
        title: str,
        description: str,
        creator_id: PersonId,
        points: int,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize an Activity aggregate.
        
        Args:
            activity_id: Unique identifier for the activity
            title: Title of the activity
            description: Detailed description of the activity
            creator_id: Identifier of the person who created the activity
            points: Points value for the activity
            created_at: Timestamp when activity was created (default: now)
        """
        self._activity_id = activity_id
        self._title = title
        self._description = description
        self._creator_id = creator_id
        self._points = points
        self._created_at = created_at or datetime.now(timezone.utc)
        self._domain_events: List[DomainEvent] = []
    @property
    def points(self) -> int:
        """Get the activity's points value."""
        return self._points
    
    @property
    def activity_id(self) -> ActivityId:
        """Get the activity's unique identifier."""
        return self._activity_id
    
    @property
    def title(self) -> str:
        """Get the activity's title."""
        return self._title
    
    @property
    def description(self) -> str:
        """Get the activity's description."""
        return self._description
    
    @property
    def creator_id(self) -> PersonId:
        """Get the identifier of the person who created this activity."""
        return self._creator_id
    
    @property
    def created_at(self) -> datetime:
        """Get the timestamp when the activity was created."""
        return self._created_at
    
    @property
    def domain_events(self) -> List[DomainEvent]:
        """Get the list of domain events raised by this aggregate."""
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """Clear all domain events from this aggregate."""
        self._domain_events.clear()
    
    def update_title(self, new_title: str) -> None:
        """
        Update the activity's title.
        
        Args:
            new_title: The new title for the activity
            
        Raises:
            ValueError: If the new title is empty or only whitespace
        """
        if not new_title or not new_title.strip():
            raise ValueError("Activity title cannot be empty")
        
        self._title = new_title.strip()
    
    def update_description(self, new_description: str) -> None:
        """
        Update the activity's description.
        
        Args:
            new_description: The new description for the activity
            
        Raises:
            ValueError: If the new description is empty or only whitespace
        """
        if not new_description or not new_description.strip():
            raise ValueError("Activity description cannot be empty")
        
        self._description = new_description.strip()
    
    def __eq__(self, other: object) -> bool:
        """Compare activities based on their identity."""
        if not isinstance(other, Activity):
            return False
        return self._activity_id == other._activity_id
    
    def __hash__(self) -> int:
        """Hash based on activity identity."""
        return hash(self._activity_id)
    
    def __repr__(self) -> str:
        """String representation of the activity."""
        return (
            f"Activity(activity_id={self._activity_id}, "
            f"title='{self._title}', "
            f"creator_id={self._creator_id}, "
            f"created_at={self._created_at})"
        )