"""
Action command handlers for the social scoring system.

This module defines command handlers for action operations
following CQRS principles and maintaining clean separation of concerns.
"""

from typing import TYPE_CHECKING
from ..commands.submit_action_command import SubmitActionCommand
from ..commands.validate_proof_command import ValidateProofCommand
from ..services.action_application_service import ActionApplicationService
from ..security.authentication_context import AuthenticationContext
from ..security.authorization_exception import AuthorizationException

if TYPE_CHECKING:
    from src.domain.action.action import ActionId


class SubmitActionCommandHandler:
    """
    Command handler for action submission operations.
    
    Processes action submission commands using the action application service
    while maintaining CQRS separation of concerns.
    """
    
    def __init__(self, action_service: ActionApplicationService) -> None:
        """
        Initialize action submission command handler.
        
        Args:
            action_service: Service for handling action operations
        """
        self._action_service = action_service
    
    def handle(self, command: SubmitActionCommand, context: AuthenticationContext) -> 'ActionId':
        """
        Handle submit action command.
        
        Args:
            command: Submit action command to process
            context: Authentication context of the requesting user
            
        Returns:
            ActionId of the submitted action
            
        Raises:
            ValueError: If command validation fails
            AuthorizationException: If user lacks permission
        """
        # Validate command
        command.validate()
        
        # Execute through application service
        return self._action_service.submit_action(command, context)


class ValidateProofCommandHandler:
    """
    Command handler for proof validation operations.
    
    Processes proof validation commands using the action application service
    while maintaining CQRS separation of concerns.
    """
    
    def __init__(self, action_service: ActionApplicationService) -> None:
        """
        Initialize proof validation command handler.
        
        Args:
            action_service: Service for handling action operations
        """
        self._action_service = action_service
    
    def handle(self, command: ValidateProofCommand, context: AuthenticationContext) -> None:
        """
        Handle validate proof command.
        
        Args:
            command: Validate proof command to process
            context: Authentication context of the requesting user
            
        Raises:
            ValueError: If command validation fails
            AuthorizationException: If user lacks permission
        """
        # Validate command
        command.validate()
        
        # Execute through application service
        self._action_service.simulate_proof_validation(command, context)