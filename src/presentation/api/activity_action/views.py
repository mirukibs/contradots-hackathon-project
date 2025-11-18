"""
Activity and Action API views for the Social Scoring System.

This module provides Django REST Framework views for activity and action endpoints,
integrating with the application layer services.
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from typing import Dict, Any, cast, List
from uuid import UUID

from .serializers import (
    CreateActivitySerializer,
    ActivityResponseSerializer,
    ActivityDetailsResponseSerializer,
    DeactivateActivitySerializer,
    SubmitActionSerializer,
    ActionResponseSerializer,
    ValidateProofSerializer,
)

from ....application.commands.create_activity_command import CreateActivityCommand
from ....application.commands.deactivate_activity_command import DeactivateActivityCommand
from ....application.commands.submit_action_command import SubmitActionCommand
from ....application.commands.validate_proof_command import ValidateProofCommand
from ....application.services.activity_application_service import ActivityApplicationService
from ....application.services.action_application_service import ActionApplicationService
from ....application.security.authentication_context import AuthenticationContext
from ....application.security.authorization_service import AuthorizationService
from ....application.security.authorization_exception import AuthorizationException
from ....infrastructure.persistence.django_repositories import (
    DjangoActivityRepository,
    DjangoActionRepository,
    DjangoPersonRepository,
)
from ....application.repositories.activity_query_repository import ActivityQueryRepository
from ....application.repositories.action_query_repository import ActionQueryRepository
from ....application.dtos.activity_dto import ActivityDto
from ....application.dtos.activity_details_dto import ActivityDetailsDto
from ....application.dtos.action_dto import ActionDto as ActionDtoType
from ....application.events.event_store import EventStore
from ....application.events.event_publisher import EventPublisher
from ....domain.shared.value_objects.person_id import PersonId
from ....domain.shared.value_objects.activity_id import ActivityId
from ....domain.shared.value_objects.action_id import ActionId
from ....domain.shared.events.domain_event import DomainEvent
from ....domain.person.role import Role
from ....infrastructure.activity_action_contract.contract_client import ActivityActionTrackerClient
from ....infrastructure.activity_action_contract.uuid_int_converter import (
    int_to_uuid,
    safe_int_to_uuid,
    uuid_to_int
)
import uuid as uuid_lib
import os
import json
import asyncio

logger = logging.getLogger(__name__)


# Import our properly implemented infrastructure components
from ....infrastructure.persistence.django_query_repositories import (
    DjangoActivityQueryRepository,
    DjangoActionQueryRepository,
    DjangoLeaderboardQueryRepository
)
from ....infrastructure.events.event_publisher import (
    DjangoSignalEventBridge,
    InMemoryEventPublisher
)
from ....infrastructure.security.django_authorization_service import (
    DjangoAuthorizationService,
    get_authorization_service
)


# ==================== Helper Functions ====================

def _get_contract_client() -> ActivityActionTrackerClient:
    """
    Get an instance of the ActivityActionTracker contract client.
    
    Returns:
        ActivityActionTrackerClient instance
    """
    # Get configuration from environment variables
    web3_provider = os.getenv('WEB3_PROVIDER', 'https://testnet-passet-hub-eth-rpc.polkadot.io')
    contract_address = os.getenv('CONTRACT_ADDRESS', '0x7e50f3D523176C696AEe69A1245b12EBAE0a17dd')
    private_key = os.getenv('PRIVATE_KEY', '004df3d1cdd120476b39cf7f726b29179f9e1ae5aaf756ce82e2f62bdda82983')
    
    # Load ABI from file or environment
    # views.py is at: src/presentation/api/activity_action/views.py
    # abi.json is at: abi.json (project root)
    # Need to go up 5 levels: activity_action -> api -> presentation -> src -> project_root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    abi_path = os.path.join(base_dir, 'abi.json')
    try:
        with open(abi_path, 'r') as f:
            contract_abi = json.load(f)
    except FileNotFoundError:
        # Fallback to environment variable if file not found
        contract_abi = json.loads(os.getenv('CONTRACT_ABI', '[]'))
    
    return ActivityActionTrackerClient(
        web3_provider=web3_provider,
        contract_address=contract_address,
        contract_abi=contract_abi,
        private_key=private_key if private_key else None
    )


def _uuid_to_int(id_obj) -> int:
    """
    Convert any ID object (PersonId, ActivityId, ActionId) with UUID value to integer for blockchain storage.
    
    Args:
        id_obj: Any ID value object with a .value property containing a UUID
        
    Returns:
        Integer representation of the UUID
    """
    if hasattr(id_obj, 'value'):
        uuid_val = id_obj.value
        return uuid_to_int(uuid_val)
    raise ValueError(f"Cannot convert {type(id_obj)} to integer")


def _int_to_person_id(value: int) -> PersonId:
    """
    Convert integer to PersonId (UUID).
    
    Args:
        value: Integer value from blockchain
        
    Returns:
        PersonId value object
    """
    uuid_obj = int_to_uuid(value)
    return PersonId(uuid_obj)


def _enrich_action_with_blockchain_data(action_dict: Dict[str, Any], contract_client: ActivityActionTrackerClient) -> Dict[str, Any]:
    """
    Enrich action data with blockchain information.
    
    Args:
        action_dict: Action data dictionary
        contract_client: Contract client instance
        
    Returns:
        Enriched action dictionary
    """
    try:
        action_id_int = uuid_to_int(action_dict.get('actionId', ''))
        blockchain_action = contract_client.get_action(action_id_int)
        
        action_dict['blockchain'] = {
            'personId': str(int_to_uuid(blockchain_action.person_id)),
            'activityId': str(int_to_uuid(blockchain_action.activity_id)),
            'description': contract_client._bytes32_to_string(blockchain_action.description),
            'proofHash': contract_client._bytes32_to_string(blockchain_action.proof_hash),
            'status': blockchain_action.status.name
        }
    except Exception as e:
        action_dict['blockchain_warning'] = f'Blockchain data unavailable: {str(e)}'
    
    return action_dict


def _enrich_activity_with_blockchain_data(activity_dict: Dict[str, Any], contract_client: ActivityActionTrackerClient) -> Dict[str, Any]:
    """
    Enrich activity data with blockchain information.
    
    Args:
        activity_dict: Activity data dictionary
        contract_client: Contract client instance
        
    Returns:
        Enriched activity dictionary
    """
    try:
        activity_id_int = uuid_to_int(activity_dict.get('activityId', ''))
        blockchain_activity = contract_client.get_activity(activity_id_int)
        
        activity_dict['blockchain'] = {
            'name': contract_client._bytes32_to_string(blockchain_activity.name),
            'description': contract_client._bytes32_to_string(blockchain_activity.description),
            'points': blockchain_activity.points,
            'isActive': blockchain_activity.is_active,
            'leadId': str(int_to_uuid(blockchain_activity.lead_id))
        }
    except Exception as e:
        activity_dict['blockchain_warning'] = f'Blockchain data unavailable: {str(e)}'
    
    return activity_dict


def _get_auth_context(request: Request) -> AuthenticationContext:
    """
    Extract authentication context from the request.
    
    Args:
        request: Django REST framework request
        
    Returns:
        AuthenticationContext with current user information
        
    Raises:
        AuthorizationException: If user is not authenticated
    """
    if not request.user or not request.user.is_authenticated:
        raise AuthorizationException("Authentication required")
    
    # Get person_id from user's PersonProfile
    try:
        from ....infrastructure.django_app.models import PersonProfile
        person_profile = PersonProfile.objects.get(user=request.user)
        person_id_str = str(person_profile.person_id)
    except PersonProfile.DoesNotExist:
        raise AuthorizationException("User profile not found")
    except Exception as e:
        raise AuthorizationException(f"Invalid user authentication state: {str(e)}")
    
    # Create domain PersonId for repository calls
    from ....domain.shared.value_objects.person_id import PersonId
    person_id_obj = PersonId(person_id_str)
    
    # Get the person's role using the repository through string ID
    from ....infrastructure.persistence.django_repositories import DjangoPersonRepository
    person_repo = DjangoPersonRepository()
    try:
        person = person_repo.find_by_id(person_id_obj)
        roles = [person.role]
    except Exception:
        # If person not found in repository, default to MEMBER
        from ....domain.person.role import Role
        roles = [Role.MEMBER]
    
    # Get email from user
    email = request.user.email if hasattr(request.user, 'email') else ""
    
    return AuthenticationContext(
        current_user_id=person_id_obj,
        email=email,
        roles=roles
    )


def _get_activity_service() -> ActivityApplicationService:
    """Create and return an instance of ActivityApplicationService."""
    # Use our properly implemented infrastructure components
    activity_repo = DjangoActivityRepository()
    activity_query_repo = DjangoActivityQueryRepository()
    person_repo = DjangoPersonRepository()
    authorization_service = get_authorization_service()
    
    return ActivityApplicationService(
        activity_repo=activity_repo,
        activity_query_repo=activity_query_repo,
        person_repo=person_repo,
        authorization_service=authorization_service
    )


# Import command handlers
from ....application.handlers.command_handler_service import CommandHandlerService


class SimpleEventPublisher(EventPublisher):
    """Simple implementation of EventPublisher for API layer."""
    
    def __init__(self):
        self._handlers = []
    
    def publish(self, event: DomainEvent) -> None:
        """Publish a single domain event."""
        # For now, just log the event - can be enhanced later
        logger.info(f"Publishing event: {type(event).__name__}")
    
    def publish_all(self, events: List[DomainEvent]) -> None:
        """Publish multiple domain events."""
        for event in events:
            self.publish(event)
    
    @property
    def event_store(self):
        """Simple event store - not implemented."""
        return None
    
    @property
    def handlers(self):
        """Get registered handlers."""
        return self._handlers


def _get_command_handler_service() -> CommandHandlerService:
    """Create and return an instance of CommandHandlerService."""
    # Create application services
    activity_service = _get_activity_service()
    action_service = _get_action_service()
    
    # For now, create a simple authentication service (can be enhanced later)
    from ....application.services.authentication_service import AuthenticationService
    from ....infrastructure.persistence.django_repositories import DjangoPersonRepository
    
    person_repo = DjangoPersonRepository()
    auth_service = AuthenticationService(person_repo)
    
    return CommandHandlerService(
        activity_service=activity_service,
        action_service=action_service,
        authentication_service=auth_service
    )


def _get_action_service() -> ActionApplicationService:
    """Create and return an instance of ActionApplicationService."""
    # Use our properly implemented infrastructure components
    action_repo = DjangoActionRepository()
    action_query_repo = DjangoActionQueryRepository()
    activity_repo = DjangoActivityRepository()
    person_repo = DjangoPersonRepository()
    # Use simple event publisher implementation
    event_publisher = SimpleEventPublisher()
    authorization_service = get_authorization_service()
    
    return ActionApplicationService(
        action_repo=action_repo,
        action_query_repo=action_query_repo,
        activity_repo=activity_repo,
        person_repo=person_repo,
        event_publisher=event_publisher,
        authorization_service=authorization_service
    )


# ==================== Activity Endpoints ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_activity(request: Request) -> Response:
    """
    Create a new activity (Lead only).
    
    Request Body:
        - name: str (3-200 characters)
        - description: str (10-1000 characters)
        - points: int (1-1000)
    
    Returns:
        201: Activity created successfully
        400: Invalid request data
        401: Authentication required
        403: Insufficient permissions (not a lead)
    """
    try:
        # Get authentication context
        auth_context = _get_auth_context(request)
        
        # Validate input data
        serializer = CreateActivitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'VALIDATION_ERROR',
                'message': 'Invalid activity data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract validated data
        validated_data = cast(Dict[str, Any], serializer.validated_data)
        
        # First, create activity on blockchain to get the blockchain_activity_id
        try:
            contract_client = _get_contract_client()
            lead_id_int = _uuid_to_int(auth_context.current_user_id)
            
            # Create activity on blockchain
            blockchain_activity_id, tx_receipt = asyncio.run(contract_client.create_activity(
                name=validated_data['name'],
                description=validated_data['description'],
                lead_id=lead_id_int,
                points=validated_data['points']
            ))
            
            # Convert blockchain_activity_id (int) to UUID for use as database activity_id
            activity_uuid = int_to_uuid(blockchain_activity_id)
            activity_id_obj = ActivityId(activity_uuid)
            
            # Create command with the blockchain-generated activity ID
            command = CreateActivityCommand(
                name=validated_data['name'],
                description=validated_data['description'],
                points=validated_data['points'],
                leadId=auth_context.current_user_id,
                activityId=activity_id_obj
            )
            
            # Execute through command handler service
            command_service = _get_command_handler_service()
            activity_id = command_service.handle_create_activity(command, auth_context)
            
            return Response({
                'message': 'Activity created successfully',
                'activityId': str(activity_id.value),
                'blockchainActivityId': blockchain_activity_id,
                'transactionHash': tx_receipt.get('transactionHash', '').hex() if tx_receipt.get('transactionHash') else None
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # If blockchain creation fails, we don't create in DB
            return Response({
                'error': 'BLOCKCHAIN_ERROR',
                'message': f'Failed to create activity on blockchain: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except AuthorizationException as e:
        return Response({
            'error': 'AUTHORIZATION_ERROR',
            'message': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
        return Response({
            'error': 'VALIDATION_ERROR',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'INTERNAL_ERROR',
            'message': f'An unexpected error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_activities(request: Request) -> Response:
    """
    Get all currently active activities.
    
    Returns:
        200: List of active activities
        401: Authentication required
    """
    try:
        # Get authentication context
        auth_context = _get_auth_context(request)
        
        # Get activities through application service
        activity_service = _get_activity_service()
        activities = activity_service.get_active_activities(auth_context)
        
        # Serialize response
        activities_data = [activity.to_dict() for activity in activities]
        
        # Enrich with blockchain data
        try:
            contract_client = _get_contract_client()
            activities_data = [
                _enrich_activity_with_blockchain_data(activity_dict, contract_client)
                for activity_dict in activities_data
            ]
        except Exception as blockchain_error:
            # Continue without blockchain enrichment
            pass
        
        return Response({
            'activities': activities_data
        }, status=status.HTTP_200_OK)
        
    except AuthorizationException as e:
        return Response({
            'error': 'AUTHORIZATION_ERROR',
            'message': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({
            'error': 'INTERNAL_ERROR',
            'message': f'An unexpected error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_activity_details(request: Request, activity_id: str) -> Response:
    """
    Get detailed information about a specific activity.
    
    Args:
        activity_id: UUID of the activity
    
    Returns:
        200: Activity details
        401: Authentication required
        404: Activity not found
    """
    try:
        # Get authentication context
        auth_context = _get_auth_context(request)
        
        # Convert activity_id to ActivityId
        activity_id_obj = ActivityId(activity_id)
        
        # Get activity details through application service
        activity_service = _get_activity_service()
        activity_details = activity_service.get_activity_details(activity_id_obj, auth_context)
        
        # Enrich with blockchain data
        try:
            contract_client = _get_contract_client()
            activity_id_int = _uuid_to_int(activity_id_obj)
            
            blockchain_activity = contract_client.get_activity(activity_id_int)
            
            # Add blockchain data to response
            activity_dict = activity_details.to_dict()
            activity_dict['blockchain'] = {
                'name': contract_client._bytes32_to_string(blockchain_activity.name),
                'description': contract_client._bytes32_to_string(blockchain_activity.description),
                'points': blockchain_activity.points,
                'isActive': blockchain_activity.is_active,
                'leadId': str(int_to_uuid(blockchain_activity.lead_id))
            }
            
            return Response(activity_dict, status=status.HTTP_200_OK)
            
        except Exception as blockchain_error:
            # Return DB data if blockchain query fails
            activity_dict = activity_details.to_dict()
            activity_dict['warning'] = f'Blockchain data unavailable: {str(blockchain_error)}'
            return Response(activity_dict, status=status.HTTP_200_OK)
        
    except AuthorizationException as e:
        return Response({
            'error': 'AUTHORIZATION_ERROR',
            'message': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
        return Response({
            'error': 'NOT_FOUND',
            'message': str(e)
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': 'INTERNAL_ERROR',
            'message': f'An unexpected error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deactivate_activity(request: Request) -> Response:
    """
    Deactivate an activity (Lead only).
    
    Request Body:
        - activityId: str (UUID)
    
    Returns:
        200: Activity deactivated successfully
        400: Invalid request data
        401: Authentication required
        403: Insufficient permissions
        404: Activity not found
    """
    try:
        # Get authentication context
        auth_context = _get_auth_context(request)
        
        # Validate input data
        serializer = DeactivateActivitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'VALIDATION_ERROR',
                'message': 'Invalid request data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract validated data
        validated_data = cast(Dict[str, Any], serializer.validated_data)
        activity_id = ActivityId(validated_data['activityId'])
        
        # Create command
        command = DeactivateActivityCommand(
            activityId=activity_id,
            leadId=auth_context.current_user_id
        )
        
        # Execute through command handler service
        command_service = _get_command_handler_service()
        command_service.handle_deactivate_activity(command, auth_context)
        
        # Deactivate activity on blockchain
        try:
            contract_client = _get_contract_client()
            activity_id_int = _uuid_to_int(activity_id)
            
            tx_receipt = asyncio.run(contract_client.deactivate_activity(activity_id_int))
            
            return Response({
                'message': 'Activity deactivated successfully',
                'transactionHash': tx_receipt.get('transactionHash', '').hex() if tx_receipt.get('transactionHash') else None
            }, status=status.HTTP_200_OK)
        except Exception as blockchain_error:
            # Activity deactivated in DB but blockchain failed
            return Response({
                'message': 'Activity deactivated successfully (blockchain update pending)',
                'warning': f'Blockchain update failed: {str(blockchain_error)}'
            }, status=status.HTTP_200_OK)
        
    except AuthorizationException as e:
        return Response({
            'error': 'AUTHORIZATION_ERROR',
            'message': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
        return Response({
            'error': 'VALIDATION_ERROR',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'INTERNAL_ERROR',
            'message': f'An unexpected error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reactivate_activity(request: Request) -> Response:
    """
    Reactivate a deactivated activity (Lead only).
    
    Request Body:
        - activityId: str (UUID)
    
    Returns:
        200: Activity reactivated successfully
        400: Invalid request data
        401: Authentication required
        403: Insufficient permissions
        404: Activity not found
    """
    try:
        # Get authentication context
        auth_context = _get_auth_context(request)
        
        # Validate input data
        serializer = DeactivateActivitySerializer(data=request.data)  # Reuse same serializer
        if not serializer.is_valid():
            return Response({
                'error': 'VALIDATION_ERROR',
                'message': 'Invalid request data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract validated data
        validated_data = cast(Dict[str, Any], serializer.validated_data)
        activity_id = ActivityId(validated_data['activityId'])
        
        # Use the application service for proper domain logic and permission checks
        activity_service = _get_activity_service()
        try:
            activity_service.reactivate_activity(activity_id, auth_context)
        except Exception as e:
            return Response({
                'error': 'REACTIVATION_ERROR',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'success': True,
            'message': 'Activity reactivated successfully'
        }, status=status.HTTP_200_OK)
        
    except AuthorizationException as e:
        return Response({
            'error': 'AUTHORIZATION_ERROR',
            'message': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
        return Response({
            'error': 'VALIDATION_ERROR',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'INTERNAL_ERROR',
            'message': f'An unexpected error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== Action Endpoints ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_action(request: Request) -> Response:
    import logging
    logging.warning(f"RAW REQUEST BODY: {request.body}")
    try:
        import json as _json
        body_json = _json.loads(request.body)
        logging.warning(f"proofHash in body: {body_json.get('proofHash')}, length: {len(body_json.get('proofHash', ''))}")
    except Exception as e:
        logging.warning(f"Could not parse request body as JSON: {e}")
    """
    Submit a new action for an activity.
    
    Request Body:
        - activityId: str (UUID)
        - description: str (10-500 characters)
        - proofHash: str (32-128 hex characters)
    
    Returns:
        201: Action submitted successfully
        400: Invalid request data
        401: Authentication required
        404: Activity not found
    """
    try:
        # Get authentication context
        auth_context = _get_auth_context(request)
        
        # Validate input data
        serializer = SubmitActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'VALIDATION_ERROR',
                'message': 'Invalid action data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract validated data
        validated_data = cast(Dict[str, Any], serializer.validated_data)
        
        # Create command
        command = SubmitActionCommand(
            personId=auth_context.current_user_id,
            activityId=ActivityId(validated_data['activityId']),
            description=validated_data['description'],
            proofHash=validated_data['proofHash']
        )
        
        # Execute through command handler service
        command_service = _get_command_handler_service()
        action_id = command_service.handle_submit_action(command, auth_context)
        
        # Submit action to blockchain
        try:
            contract_client = _get_contract_client()
            person_id_int = _uuid_to_int(auth_context.current_user_id)
            activity_id_int = _uuid_to_int(ActivityId(validated_data['activityId']))
            
            blockchain_action_id, tx_receipt = asyncio.run(contract_client.submit_action(
                person_id=person_id_int,
                activity_id=activity_id_int,
                description=validated_data['description'],
                proof_hash=validated_data['proofHash']
            ))
            
            return Response({
                'message': 'Action submitted successfully',
                'actionId': str(action_id),
                'blockchainActionId': blockchain_action_id,
                'transactionHash': tx_receipt.get('transactionHash', '').hex() if tx_receipt.get('transactionHash') else None
            }, status=status.HTTP_201_CREATED)
        except Exception as blockchain_error:
            # Action submitted to DB but blockchain failed
            return Response({
                'message': 'Action submitted successfully (blockchain storage pending)',
                'actionId': str(action_id),
                'warning': f'Blockchain storage failed: {str(blockchain_error)}'
            }, status=status.HTTP_201_CREATED)
        
    except AuthorizationException as e:
        return Response({
            'error': 'AUTHORIZATION_ERROR',
            'message': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
        return Response({
            'error': 'VALIDATION_ERROR',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'INTERNAL_ERROR',
            'message': f'An unexpected error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_validations(request: Request) -> Response:
    """
    Get all actions pending validation (Lead only).
    
    Returns:
        200: List of pending actions
        401: Authentication required
        403: Insufficient permissions (not a lead)
    """
    try:
        # Get authentication context
        auth_context = _get_auth_context(request)
        
        # Get pending actions through application service
        action_service = _get_action_service()
        actions = action_service.get_pending_validations(auth_context)
        
        # Serialize response
        actions_data = [action.to_dict() for action in actions]
        
        # Enrich with blockchain data
        try:
            contract_client = _get_contract_client()
            actions_data = [
                _enrich_action_with_blockchain_data(action_dict, contract_client)
                for action_dict in actions_data
            ]
        except Exception as blockchain_error:
            # Continue without blockchain enrichment
            pass
        
        return Response({
            'actions': actions_data
        }, status=status.HTTP_200_OK)
        
    except AuthorizationException as e:
        return Response({
            'error': 'AUTHORIZATION_ERROR',
            'message': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({
            'error': 'INTERNAL_ERROR',
            'message': f'An unexpected error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_actions(request: Request) -> Response:
    """
    Get all actions submitted by the current user.
    
    Returns:
        200: List of user's actions
        401: Authentication required
    """
    try:
        # Get authentication context
        auth_context = _get_auth_context(request)
        
        # Get user's actions through application service
        action_service = _get_action_service()
        actions = action_service.get_person_actions(auth_context.current_user_id, auth_context)
        
        # Serialize response
        actions_data = [action.to_dict() for action in actions]
        
        # Enrich with blockchain data
        try:
            contract_client = _get_contract_client()
            actions_data = [
                _enrich_action_with_blockchain_data(action_dict, contract_client)
                for action_dict in actions_data
            ]
        except Exception as blockchain_error:
            # Continue without blockchain enrichment
            pass
        
        return Response({
            'actions': actions_data
        }, status=status.HTTP_200_OK)
        
    except AuthorizationException as e:
        return Response({
            'error': 'AUTHORIZATION_ERROR',
            'message': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({
            'error': 'INTERNAL_ERROR',
            'message': f'An unexpected error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_proof(request: Request) -> Response:
    """
    Validate or reject an action's proof (Lead only).
    
    Request Body:
        - actionId: str (UUID)
        - isValid: bool
        - validatorComment: str (optional)
    
    Returns:
        200: Proof validated successfully
        400: Invalid request data
        401: Authentication required
        403: Insufficient permissions (not a lead)
        404: Action not found
    """
    try:
        # Get authentication context
        auth_context = _get_auth_context(request)
        
        # Validate input data
        serializer = ValidateProofSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'VALIDATION_ERROR',
                'message': 'Invalid validation data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract validated data
        validated_data = cast(Dict[str, Any], serializer.validated_data)
        
        # Create command
        command = ValidateProofCommand(
            actionId=ActionId(validated_data['actionId']),
            isValid=validated_data['isValid']
        )
        
        # Execute through command handler service
        command_service = _get_command_handler_service()
        command_service.handle_validate_proof(command, auth_context)
        
        # Validate proof on blockchain
        try:
            contract_client = _get_contract_client()
            action_id_int = _uuid_to_int(ActionId(validated_data['actionId']))
            
            tx_receipt = asyncio.run(contract_client.validate_proof(
                action_id=action_id_int,
                is_valid=validated_data['isValid']
            ))
            
            result_message = 'Proof validated successfully' if validated_data['isValid'] else 'Proof rejected'
            
            return Response({
                'message': result_message,
                'transactionHash': tx_receipt.get('transactionHash', '').hex() if tx_receipt.get('transactionHash') else None
            }, status=status.HTTP_200_OK)
        except Exception as blockchain_error:
            # Validation done in DB but blockchain failed
            result_message = 'Proof validated successfully' if validated_data['isValid'] else 'Proof rejected'
            return Response({
                'message': f'{result_message} (blockchain update pending)',
                'warning': f'Blockchain update failed: {str(blockchain_error)}'
            }, status=status.HTTP_200_OK)
        
    except AuthorizationException as e:
        return Response({
            'error': 'AUTHORIZATION_ERROR',
            'message': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
        return Response({
            'error': 'VALIDATION_ERROR',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'INTERNAL_ERROR',
            'message': f'An unexpected error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
