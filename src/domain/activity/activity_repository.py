"""
Activity repository interface for persistence layer abstraction.
Defines the contract for Activity aggregate persistence operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING

from ..shared.value_objects.activity_id import ActivityId
from ..shared.value_objects.person_id import PersonId

if TYPE_CHECKING:
    from .activity import Activity


class ActivityRepository(ABC):
    """
    Abstract repository interface for Activity aggregate persistence.
    
    Defines the contract that infrastructure layer implementations must follow
    to provide persistence capabilities for Activity aggregates.
    """
    
    @abstractmethod
    def save(self, activity: "Activity") -> None:
        """
        Persist an Activity aggregate.
        
        Args:
            activity: The Activity aggregate to save
        """
        pass
    
    @abstractmethod
    def find_by_id(self, activity_id: ActivityId) -> Optional["Activity"]:
        """
        Find an Activity by its unique identifier.
        
        Args:
            activity_id: The unique identifier of the activity
            
        Returns:
            The Activity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def find_by_creator_id(self, creator_id: PersonId) -> List["Activity"]:
        """
        Find all Activities created by a specific Person.
        
        Args:
            creator_id: The unique identifier of the creator
            
        Returns:
            List of Activities created by the person
        """
        pass
    
    @abstractmethod
    def find_all_active(self) -> List["Activity"]:
        """
        Find all currently active activities.
        
        Returns:
            List of all active activities
        """
        pass
    
    @abstractmethod
    def reactivate_activity(self, activity_id: ActivityId) -> None:
        """
        Reactivate a deactivated activity.
        
        Args:
            activity_id: The unique identifier of the activity to reactivate
        """
        pass