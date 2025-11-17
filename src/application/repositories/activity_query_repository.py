"""ActivityQueryRepository - Query-side repository interface for activity operations"""

from abc import ABC, abstractmethod
from typing import List
from src.application.dtos.activity_dto import ActivityDto
from src.application.dtos.activity_details_dto import ActivityDetailsDto


class ActivityQueryRepository(ABC):
    """
    Query-side repository interface for activity operations.
    
    This interface defines read-only operations for activity data,
    following the CQRS pattern for optimized read performance.
    Infrastructure layer implements this with primitive types only.
    """
    
    @abstractmethod
    def get_active_activities(self) -> List[ActivityDto]:
        """
        Get all currently active activities.
        
        Returns:
            List of ActivityDto objects for all active activities
        """
        pass
    
    @abstractmethod
    def get_activity_details(self, activity_id: str) -> ActivityDetailsDto:
        """
        Get detailed information for a specific activity including statistics.
        
        Args:
            activity_id: The ID of the activity to get details for (as string)
            
        Returns:
            ActivityDetailsDto with comprehensive activity information
            
        Raises:
            ValueError: If activity not found
        """
        pass