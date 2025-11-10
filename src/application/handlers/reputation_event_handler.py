"""ReputationEventHandler - Handles events to update domain reputation logic"""

from src.application.events.event_handler import EventHandler
from src.domain.shared.events.domain_event import DomainEvent
from src.domain.shared.events.action_submitted_event import ActionSubmittedEvent
from src.domain.shared.events.proof_validated_event import ProofValidatedEvent
from src.domain.person.person_repository import PersonRepository
from src.domain.activity.activity_repository import ActivityRepository
from src.domain.services.reputation_service import ReputationService


class ReputationEventHandler(EventHandler[DomainEvent]):
    """
    Event handler responsible for updating Person reputation scores
    based on action-related domain events.
    
    This handler bridges domain events with reputation calculation logic,
    ensuring Person.reputationScore is kept up-to-date when actions are
    submitted and validated.
    """
    
    def __init__(
        self,
        person_repo: PersonRepository,
        activity_repo: ActivityRepository,
        reputation_service: ReputationService
    ):
        self._person_repo = person_repo
        self._activity_repo = activity_repo
        self._reputation_service = reputation_service
    
    def handle(self, event: DomainEvent) -> None:
        """
        Handle domain events related to reputation updates.
        
        Args:
            event: The domain event to process
            
        Raises:
            ValueError: If event cannot be processed
            RuntimeError: If reputation update fails
        """
        if isinstance(event, ActionSubmittedEvent):
            self._handle_action_submitted(event)
        elif isinstance(event, ProofValidatedEvent):
            self._handle_proof_validated(event)
        else:
            raise ValueError(f"Unsupported event type: {type(event)}")
    
    def can_handle(self, event: DomainEvent) -> bool:
        """
        Check if this handler can process the given event.
        
        Args:
            event: The domain event to check
            
        Returns:
            True if this handler can process ActionSubmittedEvent or ProofValidatedEvent
        """
        return isinstance(event, (ActionSubmittedEvent, ProofValidatedEvent))
    
    def _handle_action_submitted(self, event: ActionSubmittedEvent) -> None:
        """
        Handle ActionSubmittedEvent - placeholder for future reputation logic.
        
        Args:
            event: The action submitted event
        """
        # Future: Could implement preliminary reputation updates
        # For now, reputation changes only happen on validation
        pass
    
    def _handle_proof_validated(self, event: ProofValidatedEvent) -> None:
        """
        Handle ProofValidatedEvent - update person reputation if proof is valid.
        
        Args:
            event: The proof validated event
            
        Raises:
            ValueError: If person or activity not found
            RuntimeError: If reputation update fails
        """
        if not event.is_valid:
            # No reputation change for invalid proofs
            return
        
        # Get the person and activity
        person = self._person_repo.find_by_id(event.person_id)
        if not person:
            raise ValueError(f"Person not found: {event.person_id}")
        
        activity = self._activity_repo.find_by_id(event.activity_id)
        if not activity:
            raise ValueError(f"Activity not found: {event.activity_id}")
        
        # Since this is a proof validation event and it's valid,
        # we know an action was just verified, so we can add reputation points
        current_reputation = person.reputation_score
        
        # Each verified action adds 10 points (as per domain service logic)
        role_modifier = 1.2 if str(person.role) == "lead" else 1.0
        points_to_add = int(10 * role_modifier)
        
        # Update person reputation
        person.update_reputation(current_reputation + points_to_add)
        
        # Save the updated person
        self._person_repo.save(person)