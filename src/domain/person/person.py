"""
Person aggregate root for the Social Scoring System.
Represents a person in the community with role-based permissions and reputation.
"""
from typing import List, Any, Optional, TYPE_CHECKING

from ..shared.value_objects.person_id import PersonId
from ..shared.domain_events import DomainEvent
from .role import Role

if TYPE_CHECKING:
    from ..shared.value_objects.activity_id import ActivityId


class Person:
    """
    Person aggregate root.
    
    Business Rules:
    • MEMBER can participate in activities
    • LEAD can create and manage activities  
    • Reputation updated via events only
    """
    
    def __init__(
        self,
        person_id: PersonId,
        name: str,
        email: str,
        role: Role,
        reputation_score: int = 0
    ) -> None:
        # Validate inputs
        if not name or not name.strip():
            raise ValueError("Person name cannot be empty")
        if not email or not email.strip():
            raise ValueError("Person email cannot be empty")
        if "@" not in email:  # Basic email validation
            raise ValueError("Person email must be a valid email address")
        if reputation_score < 0:
            raise ValueError("Person reputation score cannot be negative")
        
        # Initialize aggregate root properties
        self._person_id = person_id
        self._name = name.strip()
        self._email = email.strip()
        self._role = role
        self._reputation_score = reputation_score
        
        # Event management for aggregate root pattern
        self._uncommitted_events: List[DomainEvent] = []
    
    @property
    def person_id(self) -> PersonId:
        """The unique identifier for this person."""
        return self._person_id
    
    @property
    def name(self) -> str:
        """The name of this person."""
        return self._name
    
    @property
    def email(self) -> str:
        """The email address of this person."""
        return self._email
    
    @property
    def role(self) -> Role:
        """The role of this person in the system."""
        return self._role
    
    @property
    def reputation_score(self) -> int:
        """The current reputation score of this person."""
        return self._reputation_score
    
    def register(self) -> None:
        """
        Register this person in the system.
        This is a domain operation that could generate events.
        """
        # For now, registration is just creation
        # In a more complex system, this might generate a PersonRegisteredEvent
        pass
    
    def update_reputation(self, points: int) -> None:
        """
        Update the person's reputation score.
        
        Business Rule: Reputation updated via events only
        This method should only be called by event handlers.
        
        Args:
            points: The number of points to add (can be negative)
        """
        self._reputation_score += points
        # Ensure reputation doesn't go negative
        if self._reputation_score < 0:
            self._reputation_score = 0
    
    def can_create_activities(self) -> bool:
        """
        Check if this person can create activities.
        
        Business Rule: Only LEAD role can create activities.
        
        Returns:
            True if person can create activities, False otherwise
        """
        return self._role == Role.LEAD
    
    def can_authenticate_with_email(self, email: str) -> bool:
        """
        Check if this person can be authenticated with the given email.
        
        Domain authentication validation - checks if the provided email
        matches this person's registered email.
        
        Args:
            email: The email address to validate for authentication
            
        Returns:
            True if this person can authenticate with the given email
        """
        if not email or not email.strip():
            return False
        return self._email.lower() == email.strip().lower()
    
    def has_permission_for(self, operation: str) -> bool:
        """
        Check if this person has permission for a specific operation.
        
        Role-based authorization at the domain level.
        
        Args:
            operation: The operation to check permission for
            
        Returns:
            True if person has permission for the operation
        """
        if not operation:
            return False
            
        operation = operation.lower()
        
        # Lead permissions include all member permissions
        if self._role == Role.LEAD:
            return operation in {
                'create_activity', 'manage_activity', 'deactivate_activity',
                'submit_action', 'validate_proof', 'view_activities', 
                'view_leaderboard', 'view_profile'
            }
        
        # Member permissions
        if self._role == Role.MEMBER:
            return operation in {
                'submit_action', 'view_activities', 'view_leaderboard', 'view_profile'
            }
        
        return False
    
    def can_manage_activity(self, activity_id: 'ActivityId | None') -> bool:
        """
        Check if this person can manage a specific activity.
        
        Business rule: Only LEADs can manage activities, and typically
        only the LEAD who created the activity.
        
        Args:
            activity_id: The activity to check management permissions for
            
        Returns:
            True if person can manage the activity
        """
        # Cannot manage a None activity
        if activity_id is None:
            return False
            
        # For now, any LEAD can manage any activity
        # In a more sophisticated system, this would check ownership
        return self._role == Role.LEAD
    
    def can_submit_action_as(self, person_id: PersonId) -> bool:
        """
        Check if this person can submit actions on behalf of another person.
        
        Business rule: People can only submit actions for themselves.
        
        Args:
            person_id: The PersonId to check if actions can be submitted for
            
        Returns:
            True if person can submit actions for the given PersonId
        """
        return self._person_id == person_id
    
    def get_uncommitted_events(self) -> List[DomainEvent]:
        """
        Get all uncommitted domain events for this aggregate.
        
        Returns:
            List of uncommitted domain events
        """
        return self._uncommitted_events.copy()
    
    def mark_events_as_committed(self) -> None:
        """
        Mark all uncommitted events as committed.
        This should be called after events have been published.
        """
        self._uncommitted_events.clear()
    
    def _add_event(self, event: DomainEvent) -> None:
        """
        Add a domain event to the uncommitted events list.
        
        Args:
            event: The domain event to add
        """
        self._uncommitted_events.append(event)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Person):
            return False
        return self._person_id == other._person_id
    
    def __hash__(self) -> int:
        return hash(self._person_id)
    
    def __repr__(self) -> str:
        return (f"Person(person_id={self._person_id!r}, name={self._name!r}, "
                f"email={self._email!r}, role={self._role!r}, "
                f"reputation_score={self._reputation_score})")
    
    @classmethod
    def create(
        cls,
        name: str,
        email: str,
        role: Role,
        person_id: Optional[PersonId] = None
    ) -> 'Person':
        """
        Factory method to create a new Person.
        
        Args:
            name: The person's name
            email: The person's email
            role: The person's role
            person_id: Optional specific ID, generates new one if not provided
            
        Returns:
            A new Person instance
        """
        if person_id is None:
            person_id = PersonId.generate()
        
        person = cls(
            person_id=person_id,
            name=name,
            email=email,
            role=role,
            reputation_score=0
        )
        
        # Call register method as part of creation
        person.register()
        
        return person