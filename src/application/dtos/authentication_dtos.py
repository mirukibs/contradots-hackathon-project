"""
Authentication DTOs for the social scoring system.

This module defines data transfer objects for authentication results
and related information following clean architecture principles.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.shared.value_objects.person_id import PersonId


class AuthenticationResultDto:
    """
    Result of an authentication operation (as specified in Application Layer design).
    
    This DTO contains the result information from an authentication
    attempt, including success status and user details.
    """
    
    def __init__(
        self,
        success: bool,
        person_id: "PersonId | None" = None,
        email: str = "",
        error_message: str = ""
    ) -> None:
        """
        Initialize authentication result.
        
        Args:
            success: Whether the authentication was successful
            person_id: ID of the authenticated person (if successful)
            email: Email of the authenticated person (if successful)
            error_message: Error message (if unsuccessful)
        """
        self.success = success
        self.person_id = person_id
        self.email = email
        self.error_message = error_message
    
    @classmethod
    def successful(cls, person_id: "PersonId", email: str) -> "AuthenticationResultDto":
        """
        Create a successful authentication result.
        
        Args:
            person_id: ID of the authenticated person
            email: Email of the authenticated person
            
        Returns:
            AuthenticationResultDto indicating successful authentication
        """
        return cls(success=True, person_id=person_id, email=email)
    
    @classmethod
    def failed(cls, error_message: str) -> "AuthenticationResultDto":
        """
        Create a failed authentication result.
        
        Args:
            error_message: Reason for authentication failure
            
        Returns:
            AuthenticationResultDto indicating failed authentication
        """
        return cls(success=False, error_message=error_message)


class LoginResult:
    """
    Result of a login operation.
    
    This DTO contains the result information from an authentication
    attempt, including success status and user details.
    """
    
    def __init__(
        self,
        success: bool,
        person_id: "PersonId | None" = None,
        email: str = "",
        error_message: str = ""
    ) -> None:
        """
        Initialize login result.
        
        Args:
            success: Whether the login was successful
            person_id: ID of the authenticated person (if successful)
            email: Email of the authenticated person (if successful)
            error_message: Error message (if unsuccessful)
        """
        self.success = success
        self.person_id = person_id
        self.email = email
        self.error_message = error_message
    
    @classmethod
    def successful(cls, person_id: "PersonId", email: str) -> "LoginResult":
        """
        Create a successful login result.
        
        Args:
            person_id: ID of the authenticated person
            email: Email of the authenticated person
            
        Returns:
            LoginResult indicating successful authentication
        """
        return cls(success=True, person_id=person_id, email=email)
    
    @classmethod
    def failed(cls, error_message: str) -> "LoginResult":
        """
        Create a failed login result.
        
        Args:
            error_message: Reason for authentication failure
            
        Returns:
            LoginResult indicating failed authentication
        """
        return cls(success=False, error_message=error_message)
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another login result."""
        if not isinstance(other, LoginResult):
            return False
        return (
            self.success == other.success and
            self.person_id == other.person_id and
            self.email == other.email and
            self.error_message == other.error_message
        )
    
    def __repr__(self) -> str:
        """Return string representation."""
        if self.success:
            return f"LoginResult(success=True, person_id={self.person_id!r}, email='{self.email}')"
        return f"LoginResult(success=False, error='{self.error_message}')"


class UserInfo:
    """
    DTO containing user information.
    
    This DTO provides user details for authenticated operations
    without exposing domain objects directly.
    """
    
    def __init__(
        self,
        person_id: "PersonId",
        email: str,
        name: str,
        role: str
    ) -> None:
        """
        Initialize user information.
        
        Args:
            person_id: Unique identifier of the user
            email: Email address of the user
            name: Display name of the user
            role: Role of the user (MEMBER, LEAD)
        """
        self.person_id = person_id
        self.email = email
        self.name = name
        self.role = role
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another user info."""
        if not isinstance(other, UserInfo):
            return False
        return (
            self.person_id == other.person_id and
            self.email == other.email and
            self.name == other.name and
            self.role == other.role
        )
    
    def __repr__(self) -> str:
        """Return string representation."""
        return f"UserInfo(person_id={self.person_id!r}, email='{self.email}', name='{self.name}', role='{self.role}')"