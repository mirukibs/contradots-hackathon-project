"""
Request and response serializers for the presentation layer.

Handles conversion between HTTP data and application DTOs.
"""

from typing import Dict, Any, List, Optional
from dataclasses import asdict

from src.application.dtos.person_profile_dto import PersonProfileDto
from src.application.dtos.authentication_dtos import AuthenticationResultDto, LoginResult, UserInfo
from src.application.dtos.leaderboard_dto import LeaderboardDto
from src.application.dtos.activity_dto import ActivityDto
from src.application.dtos.activity_details_dto import ActivityDetailsDto
from src.application.dtos.action_dto import ActionDto


class BaseSerializer:
    """Base serializer with common functionality."""
    
    @staticmethod
    def to_dict(dto_object: Any) -> Dict[str, Any]:
        """Convert DTO to dictionary for JSON response."""
        if hasattr(dto_object, '__dict__'):
            return {key: value for key, value in dto_object.__dict__.items()}
        return asdict(dto_object) if hasattr(dto_object, '__dataclass_fields__') else {}


class PersonSerializer(BaseSerializer):
    """Serializer for Person-related requests and responses."""
    
    @staticmethod
    def serialize_profile(profile: PersonProfileDto) -> Dict[str, Any]:
        """Serialize person profile for HTTP response."""
        return {
            'personId': profile.personId,
            'name': profile.name,
            'email': profile.email,
            'role': profile.role,
            'reputationScore': profile.reputationScore
        }
    
    @staticmethod
    def serialize_authentication_result(result: AuthenticationResultDto) -> Dict[str, Any]:
        """Serialize authentication result for HTTP response."""
        return {
            'accessToken': result.accessToken,
            'refreshToken': result.refreshToken,
            'personId': result.personId,
            'email': result.email,
            'roles': result.roles,
            'expiresAt': result.expiresAt.isoformat() if result.expiresAt else None
        }
    
    @staticmethod
    def serialize_leaderboard(leaderboard: List[LeaderboardDto]) -> List[Dict[str, Any]]:
        """Serialize leaderboard for HTTP response."""
        return [
            {
                'personId': entry.personId,
                'name': entry.name,
                'reputationScore': entry.reputationScore,
                'rank': entry.rank
            }
            for entry in leaderboard
        ]
    
    @staticmethod
    def deserialize_register_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize registration request data."""
        return {
            'name': data.get('name', '').strip(),
            'email': data.get('email', '').strip().lower(),
            'role': data.get('role', 'MEMBER').upper()
        }
    
    @staticmethod
    def deserialize_auth_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize authentication request data."""
        return {
            'email': data.get('email', '').strip().lower(),
            'password': data.get('password', '')
        }


class ActivitySerializer(BaseSerializer):
    """Serializer for Activity-related requests and responses."""
    
    @staticmethod
    def serialize_activity(activity: ActivityDto) -> Dict[str, Any]:
        """Serialize activity for HTTP response."""
        return {
            'activityId': activity.activityId,
            'name': activity.name,
            'description': activity.description,
            'points': activity.points,
            'leadName': activity.leadName,
            'isActive': activity.isActive
        }
    
    @staticmethod
    def serialize_activity_details(details: ActivityDetailsDto) -> Dict[str, Any]:
        """Serialize activity details for HTTP response."""
        return {
            'activityId': details.activityId,
            'name': details.name,
            'description': details.description,
            'points': details.points,
            'leadName': details.leadName,
            'isActive': details.isActive,
            'participantCount': details.participantCount,
            'totalActionsSubmitted': details.totalActionsSubmitted
        }
    
    @staticmethod
    def serialize_activities(activities: List[ActivityDto]) -> List[Dict[str, Any]]:
        """Serialize list of activities for HTTP response."""
        return [
            ActivitySerializer.serialize_activity(activity)
            for activity in activities
        ]
    
    @staticmethod
    def deserialize_create_activity_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize create activity request data."""
        return {
            'name': data.get('name', '').strip(),
            'description': data.get('description', '').strip(),
            'points': int(data.get('points', 0))
        }


class ActionSerializer(BaseSerializer):
    """Serializer for Action-related requests and responses."""
    
    @staticmethod
    def serialize_action(action: ActionDto) -> Dict[str, Any]:
        """Serialize action for HTTP response."""
        return {
            'actionId': action.actionId,
            'personName': action.personName,
            'activityName': action.activityName,
            'description': action.description,
            'status': action.status,
            'submittedAt': action.submittedAt
        }
    
    @staticmethod
    def serialize_actions(actions: List[ActionDto]) -> List[Dict[str, Any]]:
        """Serialize list of actions for HTTP response."""
        return [
            ActionSerializer.serialize_action(action)
            for action in actions
        ]
    
    @staticmethod
    def deserialize_submit_action_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize submit action request data."""
        return {
            'activityId': data.get('activityId', '').strip(),
            'description': data.get('description', '').strip(),
            'proofHash': data.get('proofHash', '').strip()
        }
    
    @staticmethod
    def deserialize_validate_proof_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize validate proof request data."""
        return {
            'actionId': data.get('actionId', '').strip(),
            'isValid': bool(data.get('isValid', False))
        }


class ErrorSerializer:
    """Serializer for error responses."""
    
    @staticmethod
    def serialize_error(error_message: str, error_code: str = 'GENERIC_ERROR') -> Dict[str, Any]:
        """Serialize error for HTTP response."""
        return {
            'error': {
                'message': error_message,
                'code': error_code
            }
        }
    
    @staticmethod
    def serialize_validation_errors(errors: Dict[str, List[str]]) -> Dict[str, Any]:
        """Serialize validation errors for HTTP response."""
        return {
            'error': {
                'message': 'Validation failed',
                'code': 'VALIDATION_ERROR',
                'details': errors
            }
        }
    
    @staticmethod
    def serialize_authentication_error() -> Dict[str, Any]:
        """Serialize authentication error for HTTP response."""
        return {
            'error': {
                'message': 'Authentication required',
                'code': 'AUTHENTICATION_ERROR'
            }
        }
    
    @staticmethod
    def serialize_authorization_error() -> Dict[str, Any]:
        """Serialize authorization error for HTTP response."""
        return {
            'error': {
                'message': 'Insufficient permissions',
                'code': 'AUTHORIZATION_ERROR'
            }
        }