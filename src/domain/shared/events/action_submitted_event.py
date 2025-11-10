"""
ActionSubmittedEvent for the Social Scoring System.
Domain event published when an Action is submitted.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from .domain_event import DomainEvent
from ..value_objects.person_id import PersonId
from ..value_objects.activity_id import ActivityId
from ..value_objects.action_id import ActionId


class ActionSubmittedEvent(DomainEvent):
    """Domain event published when an Action is submitted."""
    
    def __init__(
        self,
        action_id: ActionId,
        person_id: PersonId,
        activity_id: ActivityId,
        description: str,
        proof_hash: str,
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
        self._description = description
        self._proof_hash = proof_hash
    
    @property
    def action_id(self) -> ActionId:
        """The ID of the action that was submitted."""
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
    def description(self) -> str:
        """Description of the action that was submitted."""
        return self._description
    
    @property
    def proof_hash(self) -> str:
        """Blockchain proof hash for the submitted action."""
        return self._proof_hash