"""CreateActivityCommand - Command object for activity creation"""

from dataclasses import dataclass
from src.domain.person.person import PersonId


@dataclass(frozen=True)
class CreateActivityCommand:
    """
    Command for creating a new activity in the system.
    
    Attributes:
        name: Name of the activity
        description: Description of the activity
        points: Points awarded for completing the activity (must be positive)
        leadId: ID of the person who will lead this activity
    """
    name: str
    description: str
    points: int
    leadId: PersonId
    
    def validate(self) -> None:
        """
        Validates the command fields according to business rules.
        
        Raises:
            ValueError: If any validation fails
        """
        if not self.name or not self.name.strip():
            raise ValueError("Name is required and cannot be empty")
        
        if not self.description or not self.description.strip():
            raise ValueError("Description is required and cannot be empty")
        
        if self.points <= 0:
            raise ValueError("Points must be positive")
        
        if not self.leadId:
            raise ValueError("Lead ID is required")
        
        # Validate PersonId format (UUID)
        try:
            # PersonId should be a valid UUID string
            import uuid
            uuid.UUID(str(self.leadId))
        except (ValueError, TypeError):
            raise ValueError("Lead ID must be a valid UUID")