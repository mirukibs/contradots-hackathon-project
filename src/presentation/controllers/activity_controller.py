"""
Activity HTTP Controller

Handles all activity-related HTTP endpoints including creation,
retrieval, and management.
"""

from typing import Any, Dict
from flask import Blueprint, request, g

from src.application.services.activity_application_service import ActivityApplicationService
from src.application.commands.create_activity_command import CreateActivityCommand
from src.application.commands.deactivate_activity_command import DeactivateActivityCommand
from src.application.security.authorization_exception import AuthorizationException
from src.domain.shared.value_objects.activity_id import ActivityId
from src.presentation.middleware.authentication import require_authentication, require_role
from src.presentation.serializers.base_serializers import ActivitySerializer, ErrorSerializer
from src.domain.person.role import Role


class ActivityController:
    """HTTP controller for activity-related operations."""
    
    def __init__(self, activity_service: ActivityApplicationService):
        self.activity_service = activity_service
        
        # Create Flask blueprint
        self.blueprint = Blueprint('activity', __name__, url_prefix='/api/v1/activity')
        self._register_routes()
    
    def _register_routes(self):
        """Register all activity-related routes."""
        self.blueprint.add_url_rule('/', 'create', 
                                  self.create_activity, methods=['POST'])
        self.blueprint.add_url_rule('/', 'list', 
                                  self.get_active_activities, methods=['GET'])
        self.blueprint.add_url_rule('/<activity_id>', 'details', 
                                  self.get_activity_details, methods=['GET'])
        self.blueprint.add_url_rule('/<activity_id>/deactivate', 'deactivate', 
                                  self.deactivate_activity, methods=['POST'])
    
    @require_role(Role.LEAD)
    def create_activity(self) -> tuple[Dict[str, Any], int]:
        """
        Create a new activity (LEAD only).
        
        POST /api/v1/activity/
        Headers: Authorization: Bearer <jwt_token>
        Body: {
            "name": "Beach Cleanup Drive",
            "description": "Community beach cleanup event",
            "points": 50
        }
        """
        try:
            # Parse and validate request data
            data = request.get_json()
            if not data:
                return ErrorSerializer.serialize_error("Request body is required"), 400
            
            auth_context = g.auth_context
            
            # Deserialize request
            activity_data = ActivitySerializer.deserialize_create_activity_request(data)
            
            # Create command
            command = CreateActivityCommand(
                name=activity_data['name'],
                description=activity_data['description'],
                points=activity_data['points'],
                leadId=auth_context.current_user_id
            )
            
            # Execute creation
            activity_id = self.activity_service.create_activity(command, auth_context)
            
            return {'activityId': str(activity_id)}, 201
            
        except AuthorizationException as e:
            return ErrorSerializer.serialize_authorization_error(), 403
        except ValueError as e:
            return ErrorSerializer.serialize_error(str(e), 'VALIDATION_ERROR'), 400
        except Exception as e:
            return ErrorSerializer.serialize_error(str(e), 'INTERNAL_ERROR'), 500
    
    @require_authentication
    def get_active_activities(self) -> tuple[Dict[str, Any], int]:
        """
        Get all active activities.
        
        GET /api/v1/activity/
        Headers: Authorization: Bearer <jwt_token>
        """
        try:
            auth_context = g.auth_context
            
            # Get active activities
            activities = self.activity_service.get_active_activities(auth_context)
            
            # Serialize response
            response_data = ActivitySerializer.serialize_activities(activities)
            
            return {'activities': response_data}, 200
            
        except AuthorizationException as e:
            return ErrorSerializer.serialize_authorization_error(), 403
        except Exception as e:
            return ErrorSerializer.serialize_error(str(e), 'INTERNAL_ERROR'), 500
    
    @require_authentication
    def get_activity_details(self, activity_id: str) -> tuple[Dict[str, Any], int]:
        """
        Get details of a specific activity.
        
        GET /api/v1/activity/<activity_id>
        Headers: Authorization: Bearer <jwt_token>
        """
        try:
            auth_context = g.auth_context
            
            # Parse activity ID
            target_activity_id = ActivityId(activity_id)
            
            # Get activity details
            details = self.activity_service.get_activity_details(target_activity_id, auth_context)
            
            # Serialize response
            response_data = ActivitySerializer.serialize_activity_details(details)
            
            return response_data, 200
            
        except AuthorizationException as e:
            return ErrorSerializer.serialize_authorization_error(), 403
        except ValueError as e:
            return ErrorSerializer.serialize_error("Invalid activity ID", 'VALIDATION_ERROR'), 400
        except Exception as e:
            return ErrorSerializer.serialize_error(str(e), 'INTERNAL_ERROR'), 500
    
    @require_authentication
    def deactivate_activity(self, activity_id: str) -> tuple[Dict[str, Any], int]:
        """
        Deactivate an activity (creator only).
        
        POST /api/v1/activity/<activity_id>/deactivate
        Headers: Authorization: Bearer <jwt_token>
        """
        try:
            auth_context = g.auth_context
            
            # Parse activity ID
            target_activity_id = ActivityId(activity_id)
            
            # Create command
            command = DeactivateActivityCommand(
                activityId=target_activity_id,
                leadId=auth_context.current_user_id
            )
            
            # Execute deactivation
            self.activity_service.deactivate_activity(command, auth_context)
            
            return {'message': 'Activity deactivated successfully'}, 200
            
        except AuthorizationException as e:
            return ErrorSerializer.serialize_authorization_error(), 403
        except ValueError as e:
            return ErrorSerializer.serialize_error(str(e), 'VALIDATION_ERROR'), 400
        except Exception as e:
            return ErrorSerializer.serialize_error(str(e), 'INTERNAL_ERROR'), 500


def create_activity_controller(activity_service: ActivityApplicationService) -> Blueprint:
    """
    Factory function to create activity controller blueprint.
    
    Args:
        activity_service: ActivityApplicationService instance
        
    Returns:
        Flask Blueprint for activity routes
    """
    controller = ActivityController(activity_service)
    return controller.blueprint