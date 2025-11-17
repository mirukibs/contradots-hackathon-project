"""
Activity and Action API views for the Social Scoring System.

This module provides Django REST Framework views for activity and action endpoints,
integrating with the application layer services.
"""

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


# ==================== Mock Implementations ====================
# These are temporary mock implementations until proper infrastructure is created

class MockActivityQueryRepository(ActivityQueryRepository):
    """Mock implementation of ActivityQueryRepository for API layer."""
    
    def get_active_activities(self) -> List[ActivityDto]:
        # TODO: Implement proper query logic
        return []
    
    def get_activity_details(self, activity_id: ActivityId) -> ActivityDetailsDto:
        # TODO: Implement proper query logic
        raise ValueError(f"Activity not found: {activity_id}")


class MockActionQueryRepository(ActionQueryRepository):
    """Mock implementation of ActionQueryRepository for API layer."""
    
    def get_pending_validations(self) -> List[ActionDtoType]:
        # TODO: Implement proper query logic
        return []
    
    def get_person_actions(self, person_id: PersonId) -> List[ActionDtoType]:
        # TODO: Implement proper query logic
        return []
    
    def get_activity_actions(self, activity_id: ActivityId) -> List[ActionDtoType]:
        # TODO: Implement proper query logic
        return []


class MockEventStore(EventStore):
    """Mock implementation of EventStore for API layer."""
    
    def append(self, aggregate_id: UUID, events: List[DomainEvent]) -> None:
        # TODO: Implement proper event storage
        pass
    
    def get_events(self, aggregate_id: UUID) -> List[DomainEvent]:
        return []
    
    def get_all_events(self) -> List[DomainEvent]:
        return []


class MockEventPublisher(EventPublisher):
    """Mock implementation of EventPublisher for API layer."""
    
    def __init__(self, event_store: EventStore):
        self._event_store = event_store
        self._handlers: List = []
    
    def publish(self, event: DomainEvent) -> None:
        # TODO: Implement proper event publishing
        pass
    
    def publish_all(self, events: List[DomainEvent]) -> None:
        for event in events:
            self.publish(event)
    
    @property
    def event_store(self) -> EventStore:
        return self._event_store
    
    @property
    def handlers(self) -> List:
        """Get the list of registered event handlers."""
        return self._handlers


# ==================== Helper Functions ====================

def _get_contract_client() -> ActivityActionTrackerClient:
    """
    Get an instance of the ActivityActionTracker contract client.
    
    Returns:
        ActivityActionTrackerClient instance
    """
    # Get configuration from environment variables
    web3_provider = os.getenv('WEB3_PROVIDER', 'http://localhost:8545')
    contract_address = os.getenv('CONTRACT_ADDRESS', '')
    private_key = os.getenv('PRIVATE_KEY', '')
    
    # Load ABI from file or environment
    abi_path = os.getenv('CONTRACT_ABI_PATH', 'contract_abi.json')
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
    
    # Get person_id from user
    try:
        person_id = PersonId(request.user.username)  # Assuming username stores person_id
    except Exception:
        raise AuthorizationException("Invalid user authentication state")
    
    # Determine roles from user permissions or groups
    roles = []
    if request.user.is_staff or request.user.groups.filter(name='lead').exists():
        roles.append(Role.LEAD)
    else:
        roles.append(Role.MEMBER)
    
    # Get email from user
    email = request.user.email if hasattr(request.user, 'email') else ""
    
    return AuthenticationContext(
        current_user_id=person_id,
        email=email,
        roles=roles
    )


def _get_activity_service() -> ActivityApplicationService:
    """Create and return an instance of ActivityApplicationService."""
    activity_repo = DjangoActivityRepository()
    activity_query_repo = MockActivityQueryRepository()
    person_repo = DjangoPersonRepository()
    authorization_service = AuthorizationService(person_repo)
    
    return ActivityApplicationService(
        activity_repo=activity_repo,
        activity_query_repo=activity_query_repo,
        person_repo=person_repo,
        authorization_service=authorization_service
    )


def _get_action_service() -> ActionApplicationService:
    """Create and return an instance of ActionApplicationService."""
    action_repo = DjangoActionRepository()
    action_query_repo = MockActionQueryRepository()
    activity_repo = DjangoActivityRepository()
    event_store = MockEventStore()
    event_publisher = MockEventPublisher(event_store)
    authorization_service = AuthorizationService(DjangoPersonRepository())
    
    return ActionApplicationService(
        action_repo=action_repo,
        action_query_repo=action_query_repo,
        activity_repo=activity_repo,
        event_publisher=event_publisher,
        authorization_service=authorization_service
    )


# ==================== Activity Endpoints ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def create_activity(request: Request) -> Response:
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
        
        # Create command
        command = CreateActivityCommand(
            name=validated_data['name'],
            description=validated_data['description'],
            points=validated_data['points'],
            leadId=auth_context.current_user_id
        )
        
        # Execute through application service
        activity_service = _get_activity_service()
        activity_id = activity_service.create_activity(command, auth_context)
        
        # Store activity on blockchain
        try:
            contract_client = _get_contract_client()
            lead_id_int = _uuid_to_int(auth_context.current_user_id)
            activity_id_int = _uuid_to_int(ActivityId(str(activity_id)))
            
            # Create activity on blockchain
            blockchain_activity_id, tx_receipt = await contract_client.create_activity(
                name=validated_data['name'],
                description=validated_data['description'],
                lead_id=lead_id_int,
                points=validated_data['points']
            )
            
            return Response({
                'message': 'Activity created successfully',
                'activityId': str(activity_id),
                'blockchainActivityId': blockchain_activity_id,
                'transactionHash': tx_receipt.get('transactionHash', '').hex() if tx_receipt.get('transactionHash') else None
            }, status=status.HTTP_201_CREATED)
        except Exception as blockchain_error:
            # Activity created in DB but blockchain failed - log and return with warning
            return Response({
                'message': 'Activity created successfully (blockchain storage pending)',
                'activityId': str(activity_id),
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
async def deactivate_activity(request: Request) -> Response:
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
        
        # Execute through application service
        activity_service = _get_activity_service()
        activity_service.deactivate_activity(command, auth_context)
        
        # Deactivate activity on blockchain
        try:
            contract_client = _get_contract_client()
            activity_id_int = _uuid_to_int(activity_id)
            
            tx_receipt = await contract_client.deactivate_activity(activity_id_int)
            
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


# ==================== Action Endpoints ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def submit_action(request: Request) -> Response:
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
        
        # Execute through application service
        action_service = _get_action_service()
        action_id = action_service.submit_action(command, auth_context)
        
        # Submit action to blockchain
        try:
            contract_client = _get_contract_client()
            person_id_int = _uuid_to_int(auth_context.current_user_id)
            activity_id_int = _uuid_to_int(ActivityId(validated_data['activityId']))
            
            blockchain_action_id, tx_receipt = await contract_client.submit_action(
                person_id=person_id_int,
                activity_id=activity_id_int,
                description=validated_data['description'],
                proof_hash=validated_data['proofHash']
            )
            
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
async def validate_proof(request: Request) -> Response:
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
        
        # Execute through application service
        action_service = _get_action_service()
        action_service.simulate_proof_validation(command, auth_context)
        
        # Validate proof on blockchain
        try:
            contract_client = _get_contract_client()
            action_id_int = _uuid_to_int(ActionId(validated_data['actionId']))
            
            tx_receipt = await contract_client.validate_proof(
                action_id=action_id_int,
                is_valid=validated_data['isValid']
            )
            
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
