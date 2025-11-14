"""
Action HTTP Controller

Handles all action-related HTTP endpoints including submission,
validation, and querying.
"""

from typing import Any, Dict
from flask import Blueprint, request, g

from src.application.services.action_application_service import ActionApplicationService
from src.application.commands.submit_action_command import SubmitActionCommand
from src.application.commands.validate_proof_command import ValidateProofCommand
from src.application.security.authorization_exception import AuthorizationException
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.shared.value_objects.activity_id import ActivityId
from src.domain.shared.value_objects.action_id import ActionId
from src.presentation.middleware.authentication import require_authentication, require_role
from src.presentation.serializers.base_serializers import ActionSerializer, ErrorSerializer
from src.domain.person.role import Role


class ActionController:
    """HTTP controller for action-related operations."""
    
    def __init__(self, action_service: ActionApplicationService):
        self.action_service = action_service
        
        # Create Flask blueprint
        self.blueprint = Blueprint('action', __name__, url_prefix='/api/v1/action')
        self._register_routes()
    
    def _register_routes(self):
        """Register all action-related routes."""
        self.blueprint.add_url_rule('/', 'submit', 
                                  self.submit_action, methods=['POST'])
        self.blueprint.add_url_rule('/pending', 'pending_validations', 
                                  self.get_pending_validations, methods=['GET'])
        self.blueprint.add_url_rule('/my-actions', 'my_actions', 
                                  self.get_my_actions, methods=['GET'])
        self.blueprint.add_url_rule('/person/<person_id>', 'person_actions', 
                                  self.get_person_actions, methods=['GET'])
        self.blueprint.add_url_rule('/<action_id>/validate', 'validate', 
                                  self.validate_proof, methods=['POST'])
    
    @require_authentication
    def submit_action(self) -> tuple[Dict[str, Any], int]:
        """
        Submit a new action for verification.
        
        POST /api/v1/action/
        Headers: Authorization: Bearer <jwt_token>
        Body: {
            "activityId": "uuid",
            "description": "Cleaned 5kg of trash from beach",
            "proofHash": "blockchain_hash_here"
        }
        """
        try:
            # Parse and validate request data
            data = request.get_json()
            if not data:
                return ErrorSerializer.serialize_error("Request body is required"), 400
            
            auth_context = g.auth_context
            
            # Deserialize request
            action_data = ActionSerializer.deserialize_submit_action_request(data)
            
            # Create command
            command = SubmitActionCommand(
                personId=auth_context.current_user_id,
                activityId=ActivityId(action_data['activityId']),
                description=action_data['description'],
                proofHash=action_data['proofHash']
            )
            
            # Execute submission
            action_id = self.action_service.submit_action(command, auth_context)
            
            return {'actionId': str(action_id)}, 201
            
        except AuthorizationException as e:
            return ErrorSerializer.serialize_authorization_error(), 403
        except ValueError as e:
            return ErrorSerializer.serialize_error(str(e), 'VALIDATION_ERROR'), 400
        except Exception as e:
            return ErrorSerializer.serialize_error(str(e), 'INTERNAL_ERROR'), 500
    
    @require_role(Role.LEAD)
    def get_pending_validations(self) -> tuple[Dict[str, Any], int]:
        """
        Get all pending proof validations (LEAD only).
        
        GET /api/v1/action/pending
        Headers: Authorization: Bearer <jwt_token>
        """
        try:
            auth_context = g.auth_context
            
            # Get pending validations
            actions = self.action_service.get_pending_validations(auth_context)
            
            # Serialize response
            response_data = ActionSerializer.serialize_actions(actions)
            
            return {'actions': response_data}, 200
            
        except AuthorizationException as e:
            return ErrorSerializer.serialize_authorization_error(), 403
        except Exception as e:
            return ErrorSerializer.serialize_error(str(e), 'INTERNAL_ERROR'), 500
    
    @require_authentication
    def get_my_actions(self) -> tuple[Dict[str, Any], int]:
        """
        Get current user's actions.
        
        GET /api/v1/action/my-actions
        Headers: Authorization: Bearer <jwt_token>
        """
        try:
            auth_context = g.auth_context
            
            # Get user's actions
            actions = self.action_service.get_my_actions(auth_context)
            
            # Serialize response
            response_data = ActionSerializer.serialize_actions(actions)
            
            return {'actions': response_data}, 200
            
        except AuthorizationException as e:
            return ErrorSerializer.serialize_authorization_error(), 403
        except Exception as e:
            return ErrorSerializer.serialize_error(str(e), 'INTERNAL_ERROR'), 500
    
    @require_authentication
    def get_person_actions(self, person_id: str) -> tuple[Dict[str, Any], int]:
        """
        Get actions for a specific person.
        
        GET /api/v1/action/person/<person_id>
        Headers: Authorization: Bearer <jwt_token>
        """
        try:
            auth_context = g.auth_context
            
            # Parse person ID
            target_person_id = PersonId(person_id)
            
            # Get person's actions
            actions = self.action_service.get_person_actions(target_person_id, auth_context)
            
            # Serialize response
            response_data = ActionSerializer.serialize_actions(actions)
            
            return {'actions': response_data}, 200
            
        except AuthorizationException as e:
            return ErrorSerializer.serialize_authorization_error(), 403
        except ValueError as e:
            return ErrorSerializer.serialize_error("Invalid person ID", 'VALIDATION_ERROR'), 400
        except Exception as e:
            return ErrorSerializer.serialize_error(str(e), 'INTERNAL_ERROR'), 500
    
    @require_role(Role.LEAD)
    def validate_proof(self, action_id: str) -> tuple[Dict[str, Any], int]:
        """
        Validate proof for an action (LEAD only).
        
        POST /api/v1/action/<action_id>/validate
        Headers: Authorization: Bearer <jwt_token>
        Body: {
            "isValid": true
        }
        """
        try:
            # Parse and validate request data
            data = request.get_json()
            if not data:
                return ErrorSerializer.serialize_error("Request body is required"), 400
            
            auth_context = g.auth_context
            
            # Deserialize request
            validation_data = ActionSerializer.deserialize_validate_proof_request(data)
            
            # Parse action ID
            target_action_id = ActionId(action_id)
            
            # Create command
            command = ValidateProofCommand(
                actionId=target_action_id,
                isValid=validation_data['isValid']
            )
            
            # Execute validation
            self.action_service.simulate_proof_validation(command, auth_context)
            
            return {'message': 'Proof validation completed'}, 200
            
        except AuthorizationException as e:
            return ErrorSerializer.serialize_authorization_error(), 403
        except ValueError as e:
            return ErrorSerializer.serialize_error(str(e), 'VALIDATION_ERROR'), 400
        except Exception as e:
            return ErrorSerializer.serialize_error(str(e), 'INTERNAL_ERROR'), 500


def create_action_controller(action_service: ActionApplicationService) -> Blueprint:
    """
    Factory function to create action controller blueprint.
    
    Args:
        action_service: ActionApplicationService instance
        
    Returns:
        Flask Blueprint for action routes
    """
    controller = ActionController(action_service)
    return controller.blueprint