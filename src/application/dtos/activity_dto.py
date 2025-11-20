"""ActivityDto - Data transfer object for activity information"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class ActivityDto:
    """
    Data Transfer Object for activity information.
    
    This DTO is used for read operations to return activity data
    in a format optimized for activity list displays.
    
    Attributes:
        activityId: Unique identifier of the activity (as string)
        name: Name of the activity
        description: Description of the activity
        points: Points awarded for completing the activity
        leadName: Name of the activity lead
        isActive: Whether the activity is currently active
    """
    activityId: str
    name: str
    description: str
    points: int
    leadName: str
    isActive: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the DTO to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the activity
        """
        return {
            'activityId': self.activityId,
            'name': self.name,
            'description': self.description,
            'points': self.points,
            'leadName': self.leadName,
            'isActive': self.isActive
        }