"""
Repository interface for the Person aggregate.
Defines the contract for persisting and retrieving Person aggregates.
"""
from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

from ..shared.value_objects.person_id import PersonId

if TYPE_CHECKING:
    from .person import Person


class PersonRepository(ABC):
    """Abstract repository interface for Person aggregates."""
    
    @abstractmethod
    def find_by_id(self, person_id: PersonId) -> 'Person':
        """
        Find a Person by their unique identifier.
        
        Args:
            person_id: The PersonId to search for
            
        Returns:
            The Person with the given ID
            
        Raises:
            PersonNotFoundError: If no Person exists with the given ID
        """
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> 'Person':
        """
        Find a Person by their email address.
        
        Used for authentication - allows looking up users by their login email.
        
        Args:
            email: The email address to search for
            
        Returns:
            The Person with the given email
            
        Raises:
            PersonNotFoundError: If no Person exists with the given email
        """
        pass
    
    @abstractmethod
    def save(self, person: 'Person') -> None:
        """
        Save a Person aggregate to persistent storage.
        
        Args:
            person: The Person aggregate to save
        """
        pass
    
    @abstractmethod
    def find_all(self) -> List['Person']:
        """
        Find all Person aggregates.
        
        Returns:
            List of all Person aggregates
        """
        pass