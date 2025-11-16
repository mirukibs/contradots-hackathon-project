"""
Authentication command handlers for the social scoring system.

This module defines command handlers for authentication operations
following CQRS principles and maintaining clean separation of concerns.
"""

from typing import TYPE_CHECKING
from ..commands.authentication_commands import LoginCommand, LogoutCommand
from ..dtos.authentication_dtos import LoginResult
from ..services.authentication_service import AuthenticationService

if TYPE_CHECKING:
    pass


class LoginCommandHandler:
    """
    Command handler for login operations.
    
    Processes login commands using the authentication service
    while maintaining CQRS separation of concerns.
    """
    
    def __init__(self, authentication_service: AuthenticationService) -> None:
        """
        Initialize login command handler.
        
        Args:
            authentication_service: Service for handling authentication logic
        """
        self._authentication_service = authentication_service
    
    def handle(self, command: LoginCommand) -> LoginResult:
        """
        Handle login command.
        
        Args:
            command: Login command to process
            
        Returns:
            LoginResult indicating success or failure
        """
        return self._authentication_service.handle_login(command)


class LogoutCommandHandler:
    """
    Command handler for logout operations.
    
    Processes logout commands using the authentication service
    while maintaining CQRS separation of concerns.
    """
    
    def __init__(self, authentication_service: AuthenticationService) -> None:
        """
        Initialize logout command handler.
        
        Args:
            authentication_service: Service for handling authentication logic
        """
        self._authentication_service = authentication_service
    
    def handle(self, command: LogoutCommand) -> bool:
        """
        Handle logout command.
        
        Args:
            command: Logout command to process
            
        Returns:
            True if logout was successful
        """
        return self._authentication_service.handle_logout(command)