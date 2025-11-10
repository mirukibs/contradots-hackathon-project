"""
Person aggregate root for the Social Scoring System.
Represents a person in the community with role-based permissions and reputation.
"""
from typing import List, Any, Optional

from ..shared.value_objects.person_id import PersonId
from ..shared.domain_events import DomainEvent
from .role import Role


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