"""ActionApplicationService - Application service for action-related use cases"""

from typing import List

from src.application.commands.submit_action_command import SubmitActionCommand
from src.application.commands.validate_proof_command import ValidateProofCommand
from src.application.dtos.action_dto import ActionDto
from src.application.repositories.action_query_repository import ActionQueryRepository
from src.application.events.event_publisher import EventPublisher
from src.application.security.authentication_context import AuthenticationContext
from src.application.security.authorization_service import AuthorizationService
from src.domain.action.action_repository import ActionRepository
from src.domain.activity.activity_repository import ActivityRepository
from src.domain.action.action import Action, ActionId
from src.domain.person.person import PersonId
from src.domain.shared.events.proof_validated_event import ProofValidatedEvent


class ActionApplicationService:
    """
    Application service that orchestrates action-related use cases.
    
    This service handles:
    - Action submission
    - Proof validation
    - Event publishing
    
    It coordinates between repositories, enforces authorization, and publishes domain events.
    """
    
    def __init__(
        self,
        action_repo: ActionRepository,
        action_query_repo: ActionQueryRepository,
        activity_repo: ActivityRepository,
        event_publisher: EventPublisher,
        authorization_service: AuthorizationService
    ) -> None:
        self._action_repo = action_repo
        self._action_query_repo = action_query_repo
        self._activity_repo = activity_repo
        self._event_publisher = event_publisher
        self._authorization_service = authorization_service
    
    def submit_action(self, command: SubmitActionCommand, context: AuthenticationContext) -> ActionId:
        """
        Submit a new action for validation.
        
        Args:
            command: The action submission command
            context: Authentication context of the requesting user
            
        Returns:
            ActionId: The ID of the newly submitted action
            
        Raises:
            ValueError: If command validation fails or references don't exist
            AuthorizationException: If authorization fails
        """
        # Enforce authentication and authorization
        self._authorization_service.validate_role_permission(context, "submit_action")
        
        # Validate command
        command.validate()
        
        # Verify that the personId matches the authenticated user
        if command.personId != context.current_user_id:
            raise ValueError("Person ID must match the authenticated user")
        
        # Verify the activity exists and is active
        activity = self._activity_repo.find_by_id(command.activityId)
        if not activity:
            raise ValueError(f"Activity not found: {command.activityId}")
        
        # Create new action using domain factory method
        from src.domain.shared.value_objects.action_id import ActionId as DomainActionId
        action_id = DomainActionId.generate()
        
        # Use domain factory method which handles event creation
        action = Action.submit(
            action_id=action_id,
            person_id=command.personId,
            activity_id=command.activityId,
            proof=f"{command.description} [Hash: {command.proofHash}]"  # Combine description and hash
        )
        
        # Save the action
        self._action_repo.save(action)
        
        # Publish domain events raised by the action
        for event in action.domain_events:
            self._event_publisher.publish(event)
        action.clear_domain_events()
        
        return action.action_id
    
    def get_pending_validations(self, context: AuthenticationContext) -> List[ActionDto]:
        """
        Get all actions pending validation (Lead only access).
        
        Args:
            context: Authentication context of the requesting user
            
        Returns:
            List[ActionDto]: List of actions awaiting validation
            
        Raises:
            AuthorizationException: If user does not have validate_proof permission
        """
        # Only LEADs can validate proofs
        self._authorization_service.validate_role_permission(context, "validate_proof")
        
        # Delegate to query repository for optimized read
        return self._action_query_repo.get_pending_validations()
    
    def get_person_actions(self, person_id: PersonId, context: AuthenticationContext) -> List[ActionDto]:
        """
        Get all actions submitted by a specific person.
        
        Args:
            person_id: The ID of the person whose actions to retrieve
            context: Authentication context of the requesting user
            
        Returns:
            List[ActionDto]: List of actions by the person
            
        Raises:
            AuthorizationException: If user is not authenticated or trying to access other's actions
        """
        # Users can only view their own actions (unless they're a LEAD)
        self._authorization_service.require_authentication(context)
        
        # Check if user is trying to access their own actions or has validation permissions
        if person_id != context.current_user_id:
            # Allow LEADs to view any user's actions for validation purposes
            self._authorization_service.validate_role_permission(context, "validate_proof")
        
        # Delegate to query repository for optimized read
        return self._action_query_repo.get_person_actions(person_id)
    
    def simulate_proof_validation(self, command: ValidateProofCommand, context: AuthenticationContext) -> None:
        """
        Simulate proof validation (for demo purposes).
        
        Args:
            command: The proof validation command
            context: Authentication context of the requesting user
            
        Raises:
            ValueError: If command validation fails or action not found
            AuthorizationException: If user does not have validate_proof permission
        """
        # Only LEADs can validate proofs
        self._authorization_service.validate_role_permission(context, "validate_proof")
        
        # Validate command
        command.validate()
        
        # Get the action
        action = self._action_repo.find_by_id(command.actionId)
        if not action:
            raise ValueError(f"Action not found: {command.actionId}")
        
        # In a real implementation, this would update the action's validation status
        # For now, we'll just publish the validation event
        
        # Publish ProofValidatedEvent
        event = ProofValidatedEvent(
            action_id=action.action_id,
            person_id=action.person_id,
            activity_id=action.activity_id,
            is_valid=command.isValid
        )
        self._event_publisher.publish(event)