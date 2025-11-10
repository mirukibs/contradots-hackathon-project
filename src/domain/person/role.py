"""
Role enum for the Person aggregate.
Defines the roles a person can have in the social scoring system.
"""
from enum import Enum


class Role(Enum):
    """Enumeration of person roles in the system."""
    
    MEMBER = "MEMBER"
    LEAD = "LEAD"
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"Role.{self.name}"