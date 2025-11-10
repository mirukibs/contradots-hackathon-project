"""
PersonId value object for the Social Scoring System Domain.
Represents a Person's identity as an immutable, validated UUID.
"""
import uuid
from typing import Any, Union


class PersonId:
    """Value object representing a Person's identity."""
    
    def __init__(self, value: Union[uuid.UUID, str]) -> None:
        if isinstance(value, str):
            try:
                self._value = uuid.UUID(value)
            except ValueError as e:
                raise ValueError(f"PersonId value must be a valid UUID string: {e}")
        else:
            self._value = value
        self.validate()
    
    @property
    def value(self) -> uuid.UUID:
        """The UUID value of this PersonId."""
        return self._value
    
    def validate(self) -> None:
        """Validates that this PersonId has a valid UUID value."""
        # Value objects must be valid by construction
        pass
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PersonId):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)
    
    def __str__(self) -> str:
        return str(self._value)
    
    def __repr__(self) -> str:
        return f"PersonId(value={self._value!r})"

    @classmethod
    def generate(cls) -> "PersonId":
        """Generate a new PersonId with a random UUID."""
        return cls(uuid.uuid4())