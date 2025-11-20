"""
Django implementation of AuthorizationService for the Social Scoring System.

This module provides concrete authorization service implementation using Django
that implements the authorization interface defined in the application layer.
"""

from typing import List, Optional

from ...application.security.authorization_service import AuthorizationService as BaseAuthorizationService
from ...application.security.authentication_context import AuthenticationContext
from ...application.security.authorization_exception import AuthorizationException
from ...domain.person.person_repository import PersonRepository
from ...domain.person.role import Role


class DjangoAuthorizationService(BaseAuthorizationService):
    """
    Django implementation of AuthorizationService.
    
    Provides authorization capabilities based on domain rules and permissions
    while being implementation-agnostic.
    """
    
    def __init__(self, person_repository: PersonRepository) -> None:
        """
        Initialize the authorization service.
        
        Args:
            person_repository: Repository for accessing person data
        """
        super().__init__(person_repository)
        
        # Define role-based permissions
        self._role_permissions = {
            Role.LEAD: {
                'view_profile',
                'view_leaderboard', 
                'create_activity',
                'validate_action',
                'validate_proof',  # Add this line for compatibility
                'view_all_actions',
                'manage_activities'
            },
            Role.MEMBER: {
                'view_profile',  # Only own profile
                'view_leaderboard',
                'submit_action'
            }
        }
    
    def validate_role_permission(self, context: AuthenticationContext, permission: str) -> None:
        """
        Validate that the current user has the required permission.
        
        Args:
            context: Authentication context
            permission: Required permission name
            
        Raises:
            AuthorizationException: If user doesn't have the permission
        """
        self.require_authentication(context)
        
        # Get user's roles and check if any role has the permission
        user_has_permission = False
        for role in context.roles:
            role_permissions = self._role_permissions.get(role, set())
            if permission in role_permissions:
                user_has_permission = True
                break
        
        if not user_has_permission:
            role_names = [role.value for role in context.roles]
            raise AuthorizationException(
                f"User with roles {role_names} does not have permission '{permission}'",
                user_id=None,  # No PersonId available in infrastructure layer
                operation=permission
            )
    
    def can_create_activity(self, context: AuthenticationContext) -> bool:
        """
        Check if user can create activities.
        
        Args:
            context: Authentication context
            
        Returns:
            True if user can create activities
        """
        if not context.is_authenticated:
            return False
        
        return any(
            'create_activity' in self._role_permissions.get(role, set())
            for role in context.roles
        )
    
    def can_validate_actions(self, context: AuthenticationContext) -> bool:
        """
        Check if user can validate actions.
        
        Args:
            context: Authentication context
            
        Returns:
            True if user can validate actions
        """
        if not context.is_authenticated:
            return False
        
        return any(
            'validate_action' in self._role_permissions.get(role, set())
            for role in context.roles
        )
    
    def can_view_all_actions(self, context: AuthenticationContext) -> bool:
        """
        Check if user can view all actions (not just their own).
        
        Args:
            context: Authentication context
            
        Returns:
            True if user can view all actions
        """
        if not context.is_authenticated:
            return False
        
        return any(
            'view_all_actions' in self._role_permissions.get(role, set())
            for role in context.roles
        )
    
    def can_manage_activities(self, context: AuthenticationContext) -> bool:
        """
        Check if user can manage activities (edit, deactivate).
        
        Args:
            context: Authentication context
            
        Returns:
            True if user can manage activities
        """
        if not context.is_authenticated:
            return False
        
        return any(
            'manage_activities' in self._role_permissions.get(role, set())
            for role in context.roles
        )


# Global authorization service instance
_authorization_service: Optional[DjangoAuthorizationService] = None


def get_authorization_service() -> DjangoAuthorizationService:
    """
    Get the global authorization service instance.
    
    Returns:
        The configured authorization service
    """
    global _authorization_service
    if _authorization_service is None:
        from ..persistence.django_repositories import DjangoPersonRepository
        person_repo = DjangoPersonRepository()
        _authorization_service = DjangoAuthorizationService(person_repo)
    return _authorization_service


def create_authorization_service(person_repository: PersonRepository) -> DjangoAuthorizationService:
    """
    Create a new authorization service instance.
    
    Args:
        person_repository: Repository for accessing person data
        
    Returns:
        New authorization service instance
    """
    return DjangoAuthorizationService(person_repository)