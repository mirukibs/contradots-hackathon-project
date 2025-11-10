"""
Action aggregate status enumeration.
Implements the status values as specified in the domain model.
"""

from enum import Enum


class ActionStatus(str, Enum):
    """
    Status enumeration for Action entities.
    
    Represents the lifecycle states of an action within the domain:
    - SUBMITTED: Initial state when action is created and submitted
    - VALIDATED: State after proof validation is successful
    - REJECTED: State after proof validation fails
    """
    
    SUBMITTED = "submitted"
    VALIDATED = "validated"
    REJECTED = "rejected"
    
    def __str__(self) -> str:
        return self.value