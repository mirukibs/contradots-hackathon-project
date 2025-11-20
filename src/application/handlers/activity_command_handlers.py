"""
Activity command handlers for the social scoring system.

This module defines command handlers for activity operations
following CQRS principles and maintaining clean separation of concerns.
"""

from typing import TYPE_CHECKING
from ..commands.create_activity_command import CreateActivityCommand
from ..commands.deactivate_activity_command import DeactivateActivityCommand
from ..services.activity_application_service import ActivityApplicationService
from ..security.authentication_context import AuthenticationContext
from ..security.authorization_exception import AuthorizationException

if TYPE_CHECKING:
    from src.domain.shared.value_objects.activity_id import ActivityId


class CreateActivityCommandHandler:
    """
    Command handler for activity creation operations.
    
    Processes activity creation commands using the activity application service
    while maintaining CQRS separation of concerns.
    """
    
    def __init__(self, activity_service: ActivityApplicationService) -> None:
        """
        Initialize activity creation command handler.
        
        Args:
            activity_service: Service for handling activity operations
        """
        self._activity_service = activity_service
    
    def handle(self, command: CreateActivityCommand, context: AuthenticationContext) -> 'ActivityId':
        """
        Handle create activity command.
        
        Args:
            command: Create activity command to process
            context: Authentication context of the requesting user
            
        Returns:
            ActivityId of the created activity
            
        Raises:
            ValueError: If command validation fails
            AuthorizationException: If user lacks permission
        """
        # Validate command
        command.validate()
        
        # Execute through application service
        return self._activity_service.create_activity(command, context)


class DeactivateActivityCommandHandler:
    """
    Command handler for activity deactivation operations.
    
    Processes activity deactivation commands using the activity application service
    while maintaining CQRS separation of concerns.
    """
    
    def __init__(self, activity_service: ActivityApplicationService) -> None:
        """
        Initialize activity deactivation command handler.
        
        Args:
            activity_service: Service for handling activity operations
        """
        self._activity_service = activity_service
    
    def handle(self, command: DeactivateActivityCommand, context: AuthenticationContext) -> None:
        """
        Handle deactivate activity command.
        
        Args:
            command: Deactivate activity command to process
            context: Authentication context of the requesting user
            
        Raises:
            ValueError: If command validation fails
            AuthorizationException: If user lacks permission
        """
        # Validate command
        command.validate()
        
        # Execute through application service
        self._activity_service.deactivate_activity(command, context)