"""
ActionId value object for the Social Scoring System Domain.
Represents an Action's identity as an immutable, validated UUID.
"""
import uuid
from typing import Any, Union


class ActionId:
    """Value object representing an Action's identity."""
    
    def __init__(self, value: Union[uuid.UUID, str]) -> None:
        if isinstance(value, str):
            try:
                self._value = uuid.UUID(value)
            except ValueError as e:
                raise ValueError(f"ActionId value must be a valid UUID string: {e}")
        else:
            self._value = value
        self.validate()
    
    @property
    def value(self) -> uuid.UUID:
        """The UUID value of this ActionId."""
        return self._value
    
    def validate(self) -> None:
        """Validates that this ActionId has a valid UUID value."""
        # Value objects must be valid by construction
        pass
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ActionId):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)
    
    def __str__(self) -> str:
        return str(self._value)
    
    def __repr__(self) -> str:
        return f"ActionId(value={self._value!r})"

    @classmethod
    def generate(cls) -> "ActionId":
        """Generate a new ActionId with a random UUID."""
        return cls(uuid.uuid4())