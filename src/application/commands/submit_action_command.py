"""SubmitActionCommand - Command object for action submission"""

from dataclasses import dataclass
import re
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.shared.value_objects.activity_id import ActivityId


@dataclass(frozen=True)
class SubmitActionCommand:
    """
    Command for submitting an action for an activity.
    
    Attributes:
        personId: ID of the person submitting the action
        activityId: ID of the activity the action is for
        description: Description of the action taken
        proofHash: Hash of the proof document/image (must be valid hash format)
    """
    personId: PersonId
    activityId: ActivityId
    description: str
    proofHash: str
    
    def validate(self) -> None:
        """
        Validates the command fields according to business rules.
        
        Raises:
            ValueError: If any validation fails
        """
        if not self.personId:
            raise ValueError("Person ID is required")
        
        if not self.activityId:
            raise ValueError("Activity ID is required")
        
        if not self.description or not self.description.strip():
            raise ValueError("Description is required and cannot be empty")
        
        if not self.proofHash or not self.proofHash.strip():
            raise ValueError("Proof hash is required and cannot be empty")
        
        # Validate PersonId format (UUID)
        try:
            import uuid
            uuid.UUID(str(self.personId))
        except (ValueError, TypeError):
            raise ValueError("Person ID must be a valid UUID")
        
        # Validate ActivityId format (UUID)
        try:
            import uuid
            uuid.UUID(str(self.activityId))
        except (ValueError, TypeError):
            raise ValueError("Activity ID must be a valid UUID")
        
        # Validate proof hash format (should be hexadecimal string of standard lengths)
        # Standard hash lengths: MD5=32, SHA-1=40, SHA-256=64, SHA-512=128
        valid_lengths = {32, 40, 64, 128}
        if len(self.proofHash) not in valid_lengths:
            raise ValueError("Proof hash must be a valid hexadecimal string (32, 40, 64, or 128 characters)")
        
        # Check if it's valid hexadecimal
        hash_pattern = r'^[a-fA-F0-9]+$'
        if not re.match(hash_pattern, self.proofHash):
            raise ValueError("Proof hash must be a valid hexadecimal string (32, 40, 64, or 128 characters)")