"""
Action aggregate root implementation.
Implements the Action entity as specified in the domain model.
"""

from datetime import datetime, timezone
from typing import List, Optional

from ..shared.value_objects.action_id import ActionId
from ..shared.value_objects.person_id import PersonId
from ..shared.value_objects.activity_id import ActivityId
from ..shared.domain_events import DomainEvent, ActionSubmittedEvent, ProofValidatedEvent
from .action_status import ActionStatus


class Action:
    """
    Action aggregate root.
    
    Represents an action submitted by a person for an activity within the domain.
    Contains business logic for action submission and proof validation.
    """
    
    def __init__(
        self,
        action_id: ActionId,
        person_id: PersonId,
        activity_id: ActivityId,
        proof: str,
        status: ActionStatus = ActionStatus.SUBMITTED,
        submitted_at: Optional[datetime] = None,
        verified_at: Optional[datetime] = None,
        blockchain_action_id: Optional[int] = None
    ):
        """
        Initialize an Action aggregate.
        
        Args:
            action_id: Unique identifier for the action
            person_id: Identifier of the person who submitted the action
            activity_id: Identifier of the activity this action belongs to
            proof: Proof data provided by the person
            status: Current status of the action (default: SUBMITTED)
            submitted_at: Timestamp when action was submitted (default: now)
            verified_at: Timestamp when action was verified (default: None)
            blockchain_action_id: ID from blockchain contract (optional)
        """
        self._action_id = action_id
        self._person_id = person_id
        self._activity_id = activity_id
        self._proof = proof
        self._status = status
        self._submitted_at = submitted_at or datetime.now(timezone.utc)
        self._verified_at = verified_at
        self._blockchain_action_id = blockchain_action_id
        self._domain_events: List[DomainEvent] = []
    
    @property
    def action_id(self) -> ActionId:
        """Get the action's unique identifier."""
        return self._action_id
    
    @property
    def person_id(self) -> PersonId:
        """Get the identifier of the person who submitted this action."""
        return self._person_id
    
    @property
    def activity_id(self) -> ActivityId:
        """Get the identifier of the activity this action belongs to."""
        return self._activity_id
    
    @property
    def proof(self) -> str:
        """Get the proof data for this action."""
        return self._proof
    
    @property
    def status(self) -> ActionStatus:
        """Get the current status of the action."""
        return self._status
    
    @property
    def blockchain_action_id(self) -> Optional[int]:
        """Get the blockchain action ID if available."""
        return self._blockchain_action_id
    
    @property
    def submitted_at(self) -> datetime:
        """Get the timestamp when the action was submitted."""
        return self._submitted_at
    
    @property
    def verified_at(self) -> Optional[datetime]:
        """Get the timestamp when the action was verified."""
        return self._verified_at
    
    @property
    def domain_events(self) -> List[DomainEvent]:
        """Get the list of domain events raised by this aggregate."""
        return self._domain_events.copy()
    
    @classmethod
    def submit(
        cls,
        action_id: ActionId,
        person_id: PersonId,
        activity_id: ActivityId,
        proof: str
    ) -> "Action":
        """
        Create and submit a new action.
        
        Args:
            action_id: Unique identifier for the new action
            person_id: Identifier of the person submitting the action
            activity_id: Identifier of the activity
            proof: Proof data provided by the person
            
        Returns:
            New Action aggregate with SUBMITTED status
        """
        action = cls(
            action_id=action_id,
            person_id=person_id,
            activity_id=activity_id,
            proof=proof,
            status=ActionStatus.SUBMITTED
        )
        
        # Raise domain event for action submission
        event = ActionSubmittedEvent(
            action_id=action_id,
            person_id=person_id,
            activity_id=activity_id,
            description=f"Action submitted for activity {activity_id}",
            proof_hash=str(hash(proof))  # Simple hash of proof for event
        )
        action._domain_events.append(event)
        
        return action
    
    def validate_proof(self) -> None:
        """
        Validate the proof and mark the action as verified.
        
        This method handles the proof validation business logic and
        raises appropriate domain events.
        
        Raises:
            ValueError: If the action is not in SUBMITTED status
        """
        if self._status != ActionStatus.SUBMITTED:
            raise ValueError("Can only validate proof for actions in SUBMITTED status")
        
        # Update status and verification timestamp
        self._status = ActionStatus.VALIDATED
        self._verified_at = datetime.now(timezone.utc)
        
        # Raise domain event for proof validation
        event = ProofValidatedEvent(
            action_id=self._action_id,
            person_id=self._person_id,
            activity_id=self._activity_id,
            is_valid=True  # Successful validation
        )
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> None:
        """Clear all domain events from this aggregate."""
        self._domain_events.clear()
    
    def is_verified(self) -> bool:
        """Check if the action has been verified."""
        return self._status == ActionStatus.VALIDATED
    
    def __eq__(self, other: object) -> bool:
        """Compare actions based on their identity."""
        if not isinstance(other, Action):
            return False
        return self._action_id == other._action_id
    
    def __hash__(self) -> int:
        """Hash based on action identity."""
        return hash(self._action_id)
    
    def __repr__(self) -> str:
        """String representation of the action."""
        return (
            f"Action(action_id={self._action_id}, "
            f"person_id={self._person_id}, "
            f"activity_id={self._activity_id}, "
            f"status={self._status}, "
            f"submitted_at={self._submitted_at})"
        )