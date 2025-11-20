"""
Authorization exceptions for the social scoring system.

This module defines exceptions related to authorization failures
in an infrastructure-agnostic manner.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.person.person import PersonId


class AuthorizationException(Exception):
    """
    Exception raised when authorization fails.
    
    This exception represents authorization failures in the application
    layer without exposing infrastructure-specific details.
    """
    
    def __init__(
        self, 
        message: str, 
        user_id: Optional["PersonId"] = None,
        operation: Optional[str] = None,
        resource_id: Optional[str] = None,
        attempted_at: Optional[datetime] = None,
        required_permission: Optional[str] = None  # Legacy compatibility
    ) -> None:
        """
        Initialize authorization exception.
        
        Args:
            message: Human-readable error message
            user_id: ID of the user who attempted the operation
            operation: The operation that was attempted
            resource_id: ID of the resource that was accessed
            attempted_at: Timestamp when authorization was attempted (defaults to now)
            required_permission: Legacy compatibility parameter
        """
        super().__init__(message)
        self.message = message
        self.user_id = user_id
        self.operation = operation or required_permission
        self.resource_id = resource_id
        self.attempted_at = attempted_at or datetime.now()
        # Legacy compatibility
        self.required_permission = required_permission
    
    def __str__(self) -> str:
        """Return string representation of the exception."""
        parts = [self.message]
        if self.user_id:
            parts.append(f"user: {self.user_id}")
        if self.operation:
            parts.append(f"operation: {self.operation}")
        if self.resource_id:
            parts.append(f"resource: {self.resource_id}")
        parts.append(f"attempted at: {self.attempted_at}")
        
        return f"{' ('.join([parts[0]] + parts[1:])}" + ")" * (len(parts) - 1)