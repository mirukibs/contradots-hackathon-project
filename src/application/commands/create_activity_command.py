"""CreateActivityCommand - Command object for activity creation"""

from dataclasses import dataclass
from typing import TYPE_CHECKING
from src.domain.person.person import PersonId

if TYPE_CHECKING:
    from src.domain.shared.value_objects.activity_id import ActivityId


@dataclass(frozen=True)
class CreateActivityCommand:
    """
    Command for creating a new activity in the system.
    
    Attributes:
        name: Name of the activity
        description: Description of the activity
        points: Points awarded for completing the activity (must be positive)
        leadId: ID of the person who will lead this activity
        activityId: Optional pre-generated activity ID (e.g., from blockchain)
    """
    name: str
    description: str
    points: int
    leadId: PersonId
    activityId: 'ActivityId | None' = None
    
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
            import uuid
            uuid.UUID(str(self.leadId))
        except (ValueError, TypeError):
            raise ValueError("Lead ID must be a valid UUID")