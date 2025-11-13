"""
Authentication commands for the social scoring system.

This module defines commands related to authentication operations
following CQRS principles and domain-driven design.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..security.authentication_context import AuthenticationContext


class AuthenticateUserCommand:
    """
    Command for user authentication (as specified in Application Layer design).
    
    This command represents the intent to authenticate a user
    using their credentials.
    """
    
    def __init__(self, email: str, password: str) -> None:
        """
        Initialize authenticate user command.
        
        Args:
            email: User's email address
            password: User's password (will be handled securely)
        """
        if not email or not email.strip():
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")
            
        self.email = email.strip().lower()
        self.password = password  # In real implementation, this would be handled securely
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another authenticate user command."""
        if not isinstance(other, AuthenticateUserCommand):
            return False
        return self.email == other.email
    
    def __repr__(self) -> str:
        """Return string representation (without password)."""
        return f"AuthenticateUserCommand(email='{self.email}')"


class LoginCommand:
    """
    Command for user authentication via email.
    
    This command represents the intent to authenticate a user
    using their email credentials.
    """
    
    def __init__(self, email: str, password: str) -> None:
        """
        Initialize login command.
        
        Args:
            email: User's email address
            password: User's password (will be handled securely)
        """
        if not email or not email.strip():
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")
            
        self.email = email.strip().lower()
        self.password = password  # In real implementation, this would be handled securely
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another login command."""
        if not isinstance(other, LoginCommand):
            return False
        return self.email == other.email
    
    def __repr__(self) -> str:
        """Return string representation (without password)."""
        return f"LoginCommand(email='{self.email}')"


class LogoutCommand:
    """
    Command for user logout.
    
    This command represents the intent to logout a user
    and invalidate their authentication context.
    """
    
    def __init__(self, context: "AuthenticationContext") -> None:
        """
        Initialize logout command.
        
        Args:
            context: Current authentication context to logout
        """
        self.context = context
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another logout command."""
        if not isinstance(other, LogoutCommand):
            return False
        return self.context == other.context
    
    def __repr__(self) -> str:
        """Return string representation."""
        return f"LogoutCommand(person_id={self.context.person_id!r})"