"""
Command handler service for the social scoring system.

This module provides a centralized service for executing commands
through their appropriate handlers, implementing the Command pattern.
"""

from typing import TypeVar, Generic, Any
from ..commands.create_activity_command import CreateActivityCommand
from ..commands.deactivate_activity_command import DeactivateActivityCommand
from ..commands.submit_action_command import SubmitActionCommand
from ..commands.validate_proof_command import ValidateProofCommand
from ..commands.authentication_commands import LoginCommand, LogoutCommand
from ..handlers.activity_command_handlers import (
    CreateActivityCommandHandler,
    DeactivateActivityCommandHandler
)
from ..handlers.action_command_handlers import (
    SubmitActionCommandHandler,
    ValidateProofCommandHandler
)
from ..handlers.authentication_command_handlers import (
    LoginCommandHandler,
    LogoutCommandHandler
)
from ..services.activity_application_service import ActivityApplicationService
from ..services.action_application_service import ActionApplicationService
from ..services.authentication_service import AuthenticationService
from ..security.authentication_context import AuthenticationContext

TCommand = TypeVar('TCommand')
TResult = TypeVar('TResult')


class CommandHandlerService:
    """
    Centralized service for executing commands through their handlers.
    
    This service acts as a command dispatcher, routing commands to their
    appropriate handlers and providing a clean API for command execution.
    """
    
    def __init__(
        self,
        activity_service: ActivityApplicationService,
        action_service: ActionApplicationService,
        authentication_service: AuthenticationService
    ) -> None:
        """
        Initialize the command handler service.
        
        Args:
            activity_service: Service for activity operations
            action_service: Service for action operations
            authentication_service: Service for authentication operations
        """
        # Initialize command handlers
        self._create_activity_handler = CreateActivityCommandHandler(activity_service)
        self._deactivate_activity_handler = DeactivateActivityCommandHandler(activity_service)
        self._submit_action_handler = SubmitActionCommandHandler(action_service)
        self._validate_proof_handler = ValidateProofCommandHandler(action_service)
        self._login_handler = LoginCommandHandler(authentication_service)
        self._logout_handler = LogoutCommandHandler(authentication_service)
    
    def handle_create_activity(
        self, 
        command: CreateActivityCommand, 
        context: AuthenticationContext
    ) -> Any:
        """
        Handle activity creation command.
        
        Args:
            command: The command to execute
            context: Authentication context
            
        Returns:
            ActivityId of the created activity
        """
        return self._create_activity_handler.handle(command, context)
    
    def handle_deactivate_activity(
        self, 
        command: DeactivateActivityCommand, 
        context: AuthenticationContext
    ) -> None:
        """
        Handle activity deactivation command.
        
        Args:
            command: The command to execute
            context: Authentication context
        """
        self._deactivate_activity_handler.handle(command, context)
    
    def handle_submit_action(
        self, 
        command: SubmitActionCommand, 
        context: AuthenticationContext
    ) -> Any:
        """
        Handle action submission command.
        
        Args:
            command: The command to execute
            context: Authentication context
            
        Returns:
            ActionId of the submitted action
        """
        return self._submit_action_handler.handle(command, context)
    
    def handle_validate_proof(
        self, 
        command: ValidateProofCommand, 
        context: AuthenticationContext
    ) -> None:
        """
        Handle proof validation command.
        
        Args:
            command: The command to execute
            context: Authentication context
        """
        self._validate_proof_handler.handle(command, context)
    
    def handle_login(self, command: LoginCommand) -> Any:
        """
        Handle login command.
        
        Args:
            command: The command to execute
            
        Returns:
            LoginResult indicating success or failure
        """
        return self._login_handler.handle(command)
    
    def handle_logout(self, command: LogoutCommand) -> bool:
        """
        Handle logout command.
        
        Args:
            command: The command to execute
            
        Returns:
            True if logout was successful
        """
        return self._logout_handler.handle(command)