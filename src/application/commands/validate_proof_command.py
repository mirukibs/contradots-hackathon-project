"""ValidateProofCommand - Command object for proof validation"""

from dataclasses import dataclass
from src.domain.shared.value_objects.action_id import ActionId


@dataclass(frozen=True)
class ValidateProofCommand:
    """
    Command for validating a proof submission.
    
    Attributes:
        actionId: ID of the action whose proof is being validated
        isValid: Whether the proof is valid or not
    """
    actionId: ActionId
    isValid: bool
    
    def validate(self) -> None:
        """
        Validates the command fields according to business rules.
        
        Raises:
            ValueError: If any validation fails
        """
        if not self.actionId:
            raise ValueError("Action ID is required")
        
        # isValid is guaranteed to be bool by dataclass type hint
        
        # Validate ActionId format (UUID)
        try:
            import uuid
            uuid.UUID(str(self.actionId))
        except (ValueError, TypeError):
            raise ValueError("Action ID must be a valid UUID")