"""DeactivateActivityCommand - Command object for activity deactivation"""

from dataclasses import dataclass
from src.domain.shared.value_objects.activity_id import ActivityId
from src.domain.shared.value_objects.person_id import PersonId


@dataclass(frozen=True)
class DeactivateActivityCommand:
    """
    Command for deactivating an activity.
    
    Attributes:
        activityId: ID of the activity to deactivate
        leadId: ID of the lead requesting deactivation (must match activity lead)
    """
    activityId: ActivityId
    leadId: PersonId
    
    def validate(self) -> None:
        """
        Validates the command fields according to business rules.
        
        Raises:
            ValueError: If any validation fails
        """
        if not self.activityId:
            raise ValueError("Activity ID is required")
        
        if not self.leadId:
            raise ValueError("Lead ID is required")
        
        # Validate ActivityId format (UUID)
        try:
            import uuid
            uuid.UUID(str(self.activityId))
        except (ValueError, TypeError):
            raise ValueError("Activity ID must be a valid UUID")
        
        # Validate PersonId format (UUID)
        try:
            import uuid
            uuid.UUID(str(self.leadId))
        except (ValueError, TypeError):
            raise ValueError("Lead ID must be a valid UUID")