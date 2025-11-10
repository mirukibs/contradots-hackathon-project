"""
Action repository interface for persistence layer abstraction.
Defines the contract for Action aggregate persistence operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING

from ..shared.value_objects.action_id import ActionId
from ..shared.value_objects.person_id import PersonId
from ..shared.value_objects.activity_id import ActivityId

if TYPE_CHECKING:
    from .action import Action


class ActionRepository(ABC):
    """
    Abstract repository interface for Action aggregate persistence.
    
    Defines the contract that infrastructure layer implementations must follow
    to provide persistence capabilities for Action aggregates.
    """
    
    @abstractmethod
    def save(self, action: "Action") -> None:
        """
        Persist an Action aggregate.
        
        Args:
            action: The Action aggregate to save
        """
        pass
    
    @abstractmethod
    def find_by_id(self, action_id: ActionId) -> Optional["Action"]:
        """
        Find an Action by its unique identifier.
        
        Args:
            action_id: The unique identifier of the action
            
        Returns:
            The Action if found, None otherwise
        """
        pass
    
    @abstractmethod
    def find_by_person_id(self, person_id: PersonId) -> List["Action"]:
        """
        Find all Actions submitted by a specific Person.
        
        Args:
            person_id: The unique identifier of the person
            
        Returns:
            List of Actions submitted by the person
        """
        pass
    
    @abstractmethod
    def find_by_activity_id(self, activity_id: ActivityId) -> List["Action"]:
        """
        Find all Actions associated with a specific Activity.
        
        Args:
            activity_id: The unique identifier of the activity
            
        Returns:
            List of Actions associated with the activity
        """
        pass
    
    @abstractmethod
    def find_verified_by_person_id(self, person_id: PersonId) -> List["Action"]:
        """
        Find all verified Actions by a specific Person.
        
        Args:
            person_id: The unique identifier of the person
            
        Returns:
            List of verified Actions by the person
        """
        pass