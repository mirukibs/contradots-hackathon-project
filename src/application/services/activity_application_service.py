"""ActivityApplicationService - Application service for activity-related use cases"""

from typing import List

from src.application.commands.create_activity_command import CreateActivityCommand
from src.application.commands.deactivate_activity_command import DeactivateActivityCommand
from src.application.dtos.activity_dto import ActivityDto
from src.application.dtos.activity_details_dto import ActivityDetailsDto
from src.application.repositories.activity_query_repository import ActivityQueryRepository
from src.application.security.authentication_context import AuthenticationContext
from src.application.security.authorization_service import AuthorizationService
from src.domain.activity.activity_repository import ActivityRepository
from src.domain.person.person_repository import PersonRepository
from src.domain.activity.activity import Activity, ActivityId


class ActivityApplicationService:
    """
    Application service that orchestrates activity-related use cases.
    
    This service handles:
    - Activity creation (Lead only)
    - Activity queries
    - Activity management
    
    It coordinates between command/query repositories and enforces authorization.
    """
    
    def __init__(
        self,
        activity_repo: ActivityRepository,
        activity_query_repo: ActivityQueryRepository,
        person_repo: PersonRepository,
        authorization_service: AuthorizationService
    ) -> None:
        self._activity_repo = activity_repo
        self._activity_query_repo = activity_query_repo
        self._person_repo = person_repo
        self._authorization_service = authorization_service
    
    def create_activity(self, command: CreateActivityCommand, context: AuthenticationContext) -> ActivityId:
        """
        Create a new activity (Lead only).
        
        Args:
            command: The activity creation command
            context: Authentication context of the requesting user
            
        Returns:
            ActivityId: The ID of the newly created activity
            
        Raises:
            ValueError: If command validation fails
            AuthorizationException: If authorization fails
        """
        # Enforce authentication and authorization
        self._authorization_service.validate_role_permission(context, "create_activity")
        
        # Validate command
        command.validate()
        
        # Verify that the leadId matches the authenticated user
        if command.leadId != context.current_user_id:
            raise ValueError("Lead ID must match the authenticated user")
        
        # Create new activity using domain constructor
        from src.domain.shared.value_objects.activity_id import ActivityId as DomainActivityId
        activity_id = DomainActivityId.generate()
        
        # TODO: Add points support to Activity domain model
        # The command contains points but the domain Activity doesn't support points yet
        activity = Activity(
            activity_id=activity_id,
            title=command.name,
            description=command.description,
            creator_id=command.leadId
            # points=command.points  # TODO: Add points to Activity domain model
        )
        
        # Save the activity
        self._activity_repo.save(activity)
        
        return activity.activity_id
    
    def get_active_activities(self, context: AuthenticationContext) -> List[ActivityDto]:
        """
        Get all currently active activities.
        
        Args:
            context: Authentication context of the requesting user
            
        Returns:
            List[ActivityDto]: List of active activities
            
        Raises:
            AuthorizationException: If user is not authenticated
        """
        # Require authentication to view activities
        self._authorization_service.validate_role_permission(context, "view_activities")
        
        # Delegate to query repository for optimized read
        return self._activity_query_repo.get_active_activities()
    
    def get_activity_details(self, activity_id: ActivityId, context: AuthenticationContext) -> ActivityDetailsDto:
        """
        Get detailed information about a specific activity.
        
        Args:
            activity_id: The ID of the activity to retrieve
            context: Authentication context of the requesting user
            
        Returns:
            ActivityDetailsDto: The detailed activity data
            
        Raises:
            ValueError: If activity not found
            AuthorizationException: If user is not authenticated
        """
        # Require authentication to view activity details
        self._authorization_service.validate_role_permission(context, "view_activities")
        
        # Delegate to query repository for optimized read
        # The repository will raise ValueError if activity not found
        return self._activity_query_repo.get_activity_details(activity_id)
    
    def deactivate_activity(self, command: DeactivateActivityCommand, context: AuthenticationContext) -> None:
        """
        Deactivate an activity (Lead only).
        
        Args:
            command: The activity deactivation command
            context: Authentication context of the requesting user
            
        Raises:
            ValueError: If command validation fails
            AuthorizationException: If authorization fails
        """
        # Validate command
        command.validate()
        
        # Get the activity first to check management permissions
        activity = self._activity_repo.find_by_id(command.activityId)
        if not activity:
            raise ValueError(f"Activity not found: {command.activityId}")
        
        # Enforce activity management permissions
        self._authorization_service.enforce_activity_ownership(context, command.activityId)
        
        # Verify that the leadId matches the authenticated user
        if command.leadId != context.current_user_id:
            raise ValueError("Lead ID must match the authenticated user")
        
        # Verify the requesting lead is the activity creator  
        if activity.creator_id != command.leadId:
            raise ValueError("Only the activity creator can deactivate the activity")
        
        # TODO: Add is_active field and deactivate() method to Activity domain model
        # activity.deactivate()
        
        # Save the updated activity  
        self._activity_repo.save(activity)