"""ActionDto - Data transfer object for action information"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class ActionDto:
    """
    Data Transfer Object for action information.
    
    This DTO is used for read operations to return action data
    in a format optimized for action list displays and validation views.
    
    Attributes:
        actionId: Unique identifier of the action (as string)
        personName: Name of the person who submitted the action
        activityName: Name of the activity this action is for
        description: Description of the action taken
        status: Current status of the action (pending, validated, rejected)
        submittedAt: When the action was submitted (as ISO string)
        blockchainActionId: Blockchain action ID if available
    """
    actionId: str
    personName: str
    activityName: str
    description: str
    status: str
    submittedAt: str
    blockchainActionId: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the DTO to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the action
        """
        result = {
            'actionId': self.actionId,
            'personName': self.personName,
            'activityName': self.activityName,
            'description': self.description,
            'status': self.status,
            'submittedAt': self.submittedAt
        }
        if self.blockchainActionId is not None:
            result['blockchainActionId'] = self.blockchainActionId
        return result