"""
ProofValidatedEvent for the Social Scoring System.
Domain event published when an Action's proof is validated.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from .domain_event import DomainEvent
from ..value_objects.person_id import PersonId
from ..value_objects.activity_id import ActivityId
from ..value_objects.action_id import ActionId


class ProofValidatedEvent(DomainEvent):
    """Domain event published when an Action's proof is validated."""
    
    def __init__(
        self,
        action_id: ActionId,
        person_id: PersonId,
        activity_id: ActivityId,
        is_valid: bool,
        event_id: Optional[uuid.UUID] = None,
        occurred_at: Optional[datetime] = None
    ) -> None:
        # Generate defaults if not provided
        if event_id is None:
            event_id = uuid.uuid4()
        if occurred_at is None:
            occurred_at = datetime.now(timezone.utc)
        
        # Initialize base class
        super().__init__(
            event_id=event_id,
            occurred_at=occurred_at,
            aggregate_id=action_id.value,
            aggregate_type="Action"
        )
        
        # Store event-specific properties
        self._action_id = action_id
        self._person_id = person_id
        self._activity_id = activity_id
        self._is_valid = is_valid
    
    @property
    def action_id(self) -> ActionId:
        """The ID of the action whose proof was validated."""
        return self._action_id
    
    @property
    def person_id(self) -> PersonId:
        """The ID of the person who submitted the action."""
        return self._person_id
    
    @property
    def activity_id(self) -> ActivityId:
        """The ID of the activity this action relates to."""
        return self._activity_id
    
    @property
    def is_valid(self) -> bool:
        """Whether the proof validation was successful."""
        return self._is_valid