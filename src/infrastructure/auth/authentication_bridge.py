"""
Authentication bridge between infrastructure and application layers.

This module provides the bridge that converts infrastructure authentication
results into application layer AuthenticationContext objects.
"""

from typing import Optional

from .django_auth_integration import get_authentication_service
from ...application.security.authentication_context import AuthenticationContext, create_anonymous_context
from ...domain.shared.value_objects.person_id import PersonId
from ...domain.person.role import Role


class AuthenticationBridge:
    """
    Bridge between infrastructure authentication and application context.
    
    Converts low-level authentication tokens into high-level AuthenticationContext
    objects that the application layer can use.
    """
    
    def __init__(self) -> None:
        """Initialize authentication bridge."""
        self._auth_service = get_authentication_service()  # Use global singleton
    
    def create_context_from_token(self, token: str) -> Optional[AuthenticationContext]:
        """
        Create AuthenticationContext from an authentication token.
        
        Args:
            token: Authentication token from infrastructure
            
        Returns:
            AuthenticationContext if token is valid, None otherwise
        """
        user_info = self._auth_service.validate_token(token)
        
        if not user_info:
            return None
        
        try:
            # Extract user information from token validation
            user_id_str = user_info['user_id']
            email = user_info['email']
            
            # Convert string user ID to PersonId with UUID conversion
            # If the user_id is not a valid UUID, create a deterministic UUID from it
            try:
                person_id = PersonId(user_id_str)
            except ValueError:
                # Create a deterministic UUID from the string user ID
                import uuid
                import hashlib
                
                # Create a deterministic UUID based on the string user ID
                namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # Standard namespace
                deterministic_uuid = uuid.uuid5(namespace, user_id_str)
                person_id = PersonId(deterministic_uuid)
            
            # Get user role from infrastructure (simplified for MVP)
            # In a full implementation, this would query the PersonRepository
            # For now, default to MEMBER role
            roles = [Role.MEMBER]
            
            return AuthenticationContext(
                current_user_id=person_id,
                email=email,
                roles=roles,
                is_authenticated=True
            )
            
        except (KeyError, ValueError) as e:
            # Invalid token format or user data
            return None
    
    def create_context_from_credentials(self, email: str, password: str) -> Optional[AuthenticationContext]:
        """
        Create AuthenticationContext from email and password credentials.
        
        Args:
            email: User email address
            password: Plain text password
            
        Returns:
            AuthenticationContext if credentials are valid, None otherwise
        """
        token = self._auth_service.authenticate_user(email, password)
        
        if not token:
            return None
        
        return self.create_context_from_token(token)
    
    def register_user_and_create_context(
        self, 
        user_id: str, 
        email: str, 
        password: str
    ) -> Optional[AuthenticationContext]:
        """
        Register a new user and create authentication context.
        
        Args:
            user_id: Unique user identifier
            email: User email address
            password: Plain text password
            
        Returns:
            AuthenticationContext if registration successful, None otherwise
        """
        if self._auth_service.register_user(user_id, email, password):
            # Create token for the newly registered user
            token = self._auth_service.authenticate_user(email, password)
            if token:
                return self.create_context_from_token(token)
        
        return None
    
    def create_anonymous_context(self) -> AuthenticationContext:
        """
        Create anonymous authentication context for unauthenticated users.
        
        Returns:
            Anonymous AuthenticationContext
        """
        return create_anonymous_context()


# Global authentication bridge instance for dependency injection
_authentication_bridge: Optional[AuthenticationBridge] = None


def get_authentication_bridge() -> AuthenticationBridge:
    """
    Get the global authentication bridge instance.
    
    Returns:
        AuthenticationBridge singleton instance
    """
    global _authentication_bridge
    if _authentication_bridge is None:
        _authentication_bridge = AuthenticationBridge()
    return _authentication_bridge


def create_authentication_context_from_token(token: str) -> Optional[AuthenticationContext]:
    """
    Convenience function to create AuthenticationContext from token.
    
    Args:
        token: Authentication token
        
    Returns:
        AuthenticationContext if valid, None otherwise
    """
    bridge = get_authentication_bridge()
    return bridge.create_context_from_token(token)


def authenticate_and_create_context(email: str, password: str) -> Optional[AuthenticationContext]:
    """
    Convenience function to authenticate and create AuthenticationContext.
    
    Args:
        email: User email
        password: User password
        
    Returns:
        AuthenticationContext if authenticated, None otherwise
    """
    bridge = get_authentication_bridge()
    return bridge.create_context_from_credentials(email, password)