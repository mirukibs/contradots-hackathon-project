"""
Authorization service for the social scoring system.

This module defines the authorization service that handles
permission checking in an infrastructure-agnostic manner.
"""

from typing import TYPE_CHECKING
from .authentication_context import AuthenticationContext
from .authorization_exception import AuthorizationException

if TYPE_CHECKING:
    from ...domain.person.person_repository import PersonRepository
    from ...domain.activity.activity import ActivityId
    from ...domain.person.person import PersonId


class AuthorizationService:
    """
    Service responsible for authorization decisions.
    
    This service provides infrastructure-agnostic authorization
    capabilities based on domain rules and permissions.
    """
    
    def __init__(self, person_repository: "PersonRepository") -> None:
        """
        Initialize authorization service.
        
        Args:
            person_repository: Repository for accessing person data
        """
        self._person_repository = person_repository
    
    def validate_user_can_act_as(self, auth_context: AuthenticationContext, target_person_id: "PersonId") -> None:
        """
        Validate that the authenticated user can act as another person.
        
        Args:
            auth_context: Authentication context
            target_person_id: The PersonId to check if actions can be performed as
            
        Raises:
            AuthorizationException: If the user cannot act as the target person
        """
        if not auth_context.is_authenticated:
            raise AuthorizationException("Authentication required")
        
        if not auth_context.can_act_as(target_person_id):
            raise AuthorizationException(
                f"User {auth_context.current_user_id} cannot act as {target_person_id}"
            )
    
    def validate_role_permission(self, auth_context: AuthenticationContext, operation: str) -> None:
        """
        Validate that the authenticated user has role permission for an operation.
        
        Args:
            auth_context: Authentication context
            operation: The operation to validate permission for
            
        Raises:
            AuthorizationException: If the user does not have permission
        """
        if not auth_context.is_authenticated:
            raise AuthorizationException("Authentication required")
        
        try:
            person = self._person_repository.find_by_id(auth_context.current_user_id)
        except Exception:
            raise AuthorizationException("Person not found")
        
        if not person.has_permission_for(operation):
            raise AuthorizationException(
                f"Permission denied",
                required_permission=operation
            )
    
    def enforce_resource_access(self, auth_context: AuthenticationContext, resource_id: str) -> None:
        """
        Enforce that the authenticated user can access a specific resource.
        
        Args:
            auth_context: Authentication context
            resource_id: The identifier of the resource to access
            
        Raises:
            AuthorizationException: If access is denied
        """
        if not auth_context.is_authenticated:
            raise AuthorizationException("Authentication required")
        
        # Basic resource access validation
        # In a real implementation, this would check specific resource ownership/permissions
        try:
            # Verify person exists
            self._person_repository.find_by_id(auth_context.current_user_id)
        except Exception:
            raise AuthorizationException("Person not found")
        
        # For now, authenticated users can access basic resources
        # More sophisticated logic would check resource-specific permissions
    
    def enforce_activity_ownership(self, auth_context: AuthenticationContext, activity_id: "ActivityId") -> None:
        """
        Enforce that the authenticated user can manage a specific activity.
        
        Args:
            auth_context: Authentication context
            activity_id: ID of the activity to manage
            
        Raises:
            AuthorizationException: If activity management permission is not granted
        """
        if not auth_context.is_authenticated:
            raise AuthorizationException("Authentication required")
        
        try:
            person = self._person_repository.find_by_id(auth_context.current_user_id)
        except Exception:
            raise AuthorizationException("Person not found")
        
        if not person.can_manage_activity(activity_id):
            raise AuthorizationException("Activity management permission denied")
    
    # Legacy compatibility methods
    def require_authentication(self, context: AuthenticationContext) -> None:
        """Legacy compatibility method."""
        if not context.is_authenticated:
            raise AuthorizationException("Authentication required")
    
    def require_permission(self, context: AuthenticationContext, permission: str, activity_id: "ActivityId | None" = None) -> None:
        """Legacy compatibility method."""
        self.validate_role_permission(context, permission)
    
    def require_activity_management_permission(self, context: AuthenticationContext, activity_id: "ActivityId") -> None:
        """Legacy compatibility method."""
        self.enforce_activity_ownership(context, activity_id)
    
    def require_action_submission_permission(self, context: AuthenticationContext) -> None:
        """Legacy compatibility method."""
        self.validate_role_permission(context, "submit_action")