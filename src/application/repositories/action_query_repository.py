"""ActionQueryRepository - Query-side repository interface for action operations"""

from abc import ABC, abstractmethod
from typing import List
from src.domain.person.person import PersonId
from src.domain.activity.activity import ActivityId
from src.application.dtos.action_dto import ActionDto


class ActionQueryRepository(ABC):
    """
    Query-side repository interface for action operations.
    
    This interface defines read-only operations for action data,
    following the CQRS pattern for optimized read performance.
    """
    
    @abstractmethod
    def get_pending_validations(self) -> List[ActionDto]:
        """
        Get all actions that are pending validation.
        
        Returns:
            List of ActionDto objects for actions awaiting validation
        """
        pass
    
    @abstractmethod
    def get_person_actions(self, person_id: PersonId) -> List[ActionDto]:
        """
        Get all actions submitted by a specific person.
        
        Args:
            person_id: The ID of the person to get actions for
            
        Returns:
            List of ActionDto objects for the person's actions
        """
        pass
    
    @abstractmethod
    def get_activity_actions(self, activity_id: ActivityId) -> List[ActionDto]:
        """
        Get all actions submitted for a specific activity.
        
        Args:
            activity_id: The ID of the activity to get actions for
            
        Returns:
            List of ActionDto objects for the activity's actions
        """
        pass