"""
Authentication service for the social scoring system.

This module defines the application service for handling authentication
operations in an infrastructure-agnostic manner following CQRS and DDD principles.
"""

from typing import TYPE_CHECKING
from ..commands.authentication_commands import LoginCommand, LogoutCommand
from ..dtos.authentication_dtos import LoginResult, UserInfo
from ..security.authentication_context import AuthenticationContext
from ..security.authentication_exception import AuthenticationException

if TYPE_CHECKING:
    from ...domain.person.person_repository import PersonRepository


class AuthenticationService:
    """
    Application service for authentication operations.
    
    This service orchestrates authentication workflows while remaining
    infrastructure-agnostic and following domain-driven design principles.
    """
    
    def __init__(self, person_repository: "PersonRepository") -> None:
        """
        Initialize authentication service.
        
        Args:
            person_repository: Repository for accessing person data
        """
        self._person_repository = person_repository
    
    def handle_login(self, command: LoginCommand) -> LoginResult:
        """
        Handle user login command.
        
        Args:
            command: Login command with user credentials
            
        Returns:
            LoginResult indicating success or failure
        """
        try:
            # Find person by email
            person = self._person_repository.find_by_email(command.email)
            
            # Verify authentication credentials
            if not person.can_authenticate_with_email(command.email):
                return LoginResult.failed("Invalid email credentials")
            
            # In a real implementation, password verification would happen here
            # For now, we assume password is valid if email is found
            
            return LoginResult.successful(person.person_id, person.email)
            
        except Exception as e:
            return LoginResult.failed(f"Authentication failed: {str(e)}")
    
    def handle_logout(self, command: LogoutCommand) -> bool:
        """
        Handle user logout command.
        
        Args:
            command: Logout command with authentication context
            
        Returns:
            True if logout was successful
        """
        try:
            # In a real implementation, this would invalidate tokens/sessions
            # For now, we simply return success for authenticated users
            return command.context.is_authenticated
        except Exception:
            return False
    
    def create_authentication_context(self, login_result: LoginResult) -> AuthenticationContext:
        """
        Create authentication context from login result.
        
        Args:
            login_result: Result of successful login
            
        Returns:
            Authentication context for the logged-in user
            
        Raises:
            AuthenticationException: If login result is not successful
        """
        if not login_result.success:
            raise AuthenticationException("Cannot create context from failed login", "")
        
        if login_result.person_id is None:
            raise AuthenticationException("Person ID missing from login result", "")
        
        # Get person to retrieve their roles
        try:
            person = self._person_repository.find_by_id(login_result.person_id)
            roles = [person.role]  # Person has a single role
        except Exception:
            raise AuthenticationException("Failed to get person roles", login_result.email)
        
        return AuthenticationContext(
            current_user_id=login_result.person_id,
            email=login_result.email,
            roles=roles,
            is_authenticated=True
        )
    
    def get_user_info(self, context: AuthenticationContext) -> UserInfo:
        """
        Get user information from authentication context.
        
        Args:
            context: Current authentication context
            
        Returns:
            User information DTO
            
        Raises:
            AuthenticationException: If user is not authenticated or not found
        """
        if not context.is_authenticated:
            raise AuthenticationException("User is not authenticated", "")
        
        try:
            person = self._person_repository.find_by_id(context.current_user_id)
            return UserInfo(
                person_id=person.person_id,
                email=person.email,
                name=person.name,
                role=person.role.value
            )
        except Exception as e:
            raise AuthenticationException(f"Failed to get user info: {str(e)}", context.email)
    
    def validate_authentication(self, context: AuthenticationContext) -> bool:
        """
        Validate that an authentication context is still valid.
        
        Args:
            context: Authentication context to validate
            
        Returns:
            True if context is valid and user still exists
        """
        if not context.is_authenticated:
            return False
        
        try:
            person = self._person_repository.find_by_id(context.current_user_id)
            return person.can_authenticate_with_email(context.email)
        except Exception:
            return False