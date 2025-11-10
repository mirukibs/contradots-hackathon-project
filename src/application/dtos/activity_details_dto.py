"""ActivityDetailsDto - Data transfer object for detailed activity information"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class ActivityDetailsDto:
    """
    Data Transfer Object for detailed activity information.
    
    This DTO is used for read operations to return comprehensive activity data
    including statistics and participation information.
    
    Attributes:
        activityId: Unique identifier of the activity (as string)
        name: Name of the activity
        description: Description of the activity
        points: Points awarded for completing the activity
        leadName: Name of the activity lead
        isActive: Whether the activity is currently active
        participantCount: Number of people who have participated
        totalActionsSubmitted: Total number of actions submitted for this activity
    """
    activityId: str
    name: str
    description: str
    points: int
    leadName: str
    isActive: bool
    participantCount: int
    totalActionsSubmitted: int
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the DTO to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the detailed activity information
        """
        return {
            'activityId': self.activityId,
            'name': self.name,
            'description': self.description,
            'points': self.points,
            'leadName': self.leadName,
            'isActive': self.isActive,
            'participantCount': self.participantCount,
            'totalActionsSubmitted': self.totalActionsSubmitted
        }