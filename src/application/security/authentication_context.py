"""
Authentication context for the social scoring system.

This module defines the authentication context that carries
authenticated user information throughout the application layer.
"""

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ...domain.person.person import PersonId
    from ...domain.person.role import Role


class AuthenticationContext:
    """
    Authentication context containing authenticated user information.
    
    This context is passed through application services to provide
    authentication and authorization information in an infrastructure-agnostic way.
    """
    
    def __init__(
        self,
        current_user_id: "PersonId",
        email: str,
        roles: List["Role"],
        is_authenticated: bool = True
    ) -> None:
        """
        Initialize authentication context.
        
        Args:
            current_user_id: Unique identifier of the authenticated person
            email: Email address of the authenticated person
            roles: List of roles assigned to the user
            is_authenticated: Whether the person is authenticated (default: True)
        """
        self._current_user_id = current_user_id
        self._email = email
        self._roles = roles if roles else []
        self._is_authenticated = is_authenticated
    
    @property
    def current_user_id(self) -> "PersonId":
        """Get the authenticated person's ID."""
        return self._current_user_id
    
    @property 
    def person_id(self) -> "PersonId":
        """Get the authenticated person's ID (legacy compatibility)."""
        return self._current_user_id
    
    @property
    def email(self) -> str:
        """Get the authenticated person's email."""
        return self._email
    
    @property
    def roles(self) -> List["Role"]:
        """Get the list of roles assigned to the user."""
        return self._roles.copy()
    
    @property
    def is_authenticated(self) -> bool:
        """Check if the context represents an authenticated user."""
        return self._is_authenticated
    
    def can_act_as(self, person_id: "PersonId") -> bool:
        """
        Check if the authenticated user can act as another person.
        
        Args:
            person_id: The PersonId to check if actions can be performed as
            
        Returns:
            True if the user can act as the given PersonId
        """
        # Users can only act as themselves
        return self._current_user_id == person_id
    
    def has_role(self, role: "Role") -> bool:
        """
        Check if the authenticated user has a specific role.
        
        Args:
            role: The role to check for
            
        Returns:
            True if the user has the specified role
        """
        return role in self._roles
    
    def can_access_resource(self, resource_id: str, operation: str) -> bool:
        """
        Check if the authenticated user can access a resource for a specific operation.
        
        Args:
            resource_id: The identifier of the resource
            operation: The operation to be performed
            
        Returns:
            True if the user can access the resource for the operation
        """
        if not self._is_authenticated:
            return False
        
        # Basic access control - in a real implementation this would be more sophisticated
        # For now, check if any role has permission for the operation
        from ...domain.person.role import Role
        
        # LEADs have broader access
        if Role.LEAD in self._roles:
            return operation.lower() in {
                'create_activity', 'manage_activity', 'deactivate_activity',
                'submit_action', 'validate_proof', 'view_activities', 
                'view_leaderboard', 'view_profile'
            }
        
        # MEMBERs have limited access
        if Role.MEMBER in self._roles:
            return operation.lower() in {
                'submit_action', 'view_activities', 'view_leaderboard', 'view_profile'
            }
        
        return False
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another authentication context."""
        if not isinstance(other, AuthenticationContext):
            return False
        return (
            self._current_user_id == other._current_user_id and
            self._email == other._email and
            self._roles == other._roles and
            self._is_authenticated == other._is_authenticated
        )
    
    def __repr__(self) -> str:
        """Return string representation of the context."""
        return f"AuthenticationContext(current_user_id={self._current_user_id!r}, email='{self._email}', roles={self._roles!r}, is_authenticated={self._is_authenticated})"


def create_anonymous_context() -> AuthenticationContext:
    """
    Create an authentication context for anonymous users.
    
    Returns:
        Authentication context representing an unauthenticated user
    """
    from ...domain.person.person import PersonId
    return AuthenticationContext(
        current_user_id=PersonId("00000000-0000-0000-0000-000000000000"),
        email="",
        roles=[],
        is_authenticated=False
    )