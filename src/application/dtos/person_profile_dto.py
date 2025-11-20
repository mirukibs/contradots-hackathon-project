"""PersonProfileDto - Data transfer object for person profile information"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class PersonProfileDto:
    """
    Data Transfer Object for person profile information.
    
    This DTO is used for read operations to return person profile data
    in a format optimized for the application layer consumers.
    
    Attributes:
        personId: Unique identifier of the person (as string)
        name: Full name of the person
        email: Email address of the person
        role: Role in the system (participant or lead)
        reputationScore: Current reputation score of the person
    """
    personId: str
    name: str
    email: str
    role: str
    reputationScore: int
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the DTO to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the person profile
        """
        return {
            'personId': self.personId,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'reputationScore': self.reputationScore
        }