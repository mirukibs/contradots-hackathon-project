"""
Authentication exceptions for the social scoring system.

This module defines exceptions related to authentication failures
in an infrastructure-agnostic manner.
"""

from datetime import datetime
from typing import Optional


class AuthenticationException(Exception):
    """
    Exception raised when authentication fails.
    
    This exception represents authentication failures in the application
    layer without exposing infrastructure-specific details.
    """
    
    def __init__(self, message: str, email: str, attempted_at: Optional[datetime] = None) -> None:
        """
        Initialize authentication exception.
        
        Args:
            message: Human-readable error message
            email: Email address that was used in the failed authentication attempt
            attempted_at: Timestamp when authentication was attempted (defaults to now)
        """
        super().__init__(message)
        self.message = message
        self.email = email
        self.attempted_at = attempted_at or datetime.now()
    
    def __str__(self) -> str:
        """Return string representation of the exception."""
        return f"{self.message} (email: {self.email}, attempted at: {self.attempted_at})"