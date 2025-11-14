"""
Person HTTP Controller

Handles all person-related HTTP endpoints including authentication,
registration, profiles, and leaderboard.
"""

from typing import Any, Dict
from flask import Blueprint, request, jsonify, g

from src.application.services.person_application_service import PersonApplicationService
from src.application.commands.register_person_command import RegisterPersonCommand
from src.application.commands.authentication_commands import AuthenticateUserCommand
from src.application.security.authentication_exception import AuthenticationException
from src.application.security.authorization_exception import AuthorizationException
from src.domain.shared.value_objects.person_id import PersonId
from src.presentation.middleware.authentication import (
    AuthenticationMiddleware, 
    require_authentication, 
    optional_authentication
)
from src.presentation.serializers.base_serializers import (
    PersonSerializer, 
    ErrorSerializer
)


class PersonController:
    """HTTP controller for person-related operations."""
    
    def __init__(self, person_service: PersonApplicationService):
        self.person_service = person_service
        self.auth_middleware = AuthenticationMiddleware()
        
        # Create Flask blueprint
        self.blueprint = Blueprint('person', __name__, url_prefix='/api/v1/person')
        self._register_routes()
    
    def _register_routes(self):
        """Register all person-related routes."""
        self.blueprint.add_url_rule('/register', 'register', 
                                  self.register_person, methods=['POST'])
        self.blueprint.add_url_rule('/authenticate', 'authenticate', 
                                  self.authenticate_user, methods=['POST'])
        self.blueprint.add_url_rule('/profile', 'current_profile', 
                                  self.get_current_user_profile, methods=['GET'])
        self.blueprint.add_url_rule('/profile/<person_id>', 'profile', 
                                  self.get_person_profile, methods=['GET'])
        self.blueprint.add_url_rule('/leaderboard', 'leaderboard', 
                                  self.get_leaderboard, methods=['GET'])
    
    def register_person(self) -> tuple[Dict[str, Any], int]:
        """
        Register a new person.
        
        POST /api/v1/person/register
        Body: {
            "name": "John Doe",
            "email": "john@example.com", 
            "role": "MEMBER"  // Optional, defaults to MEMBER
        }
        """
        try:
            # Parse and validate request data
            data = request.get_json()
            if not data:
                return ErrorSerializer.serialize_error("Request body is required"), 400
            
            # Deserialize request
            person_data = PersonSerializer.deserialize_register_request(data)
            
            # Create command
            command = RegisterPersonCommand(
                name=person_data['name'],
                email=person_data['email'],
                role=person_data['role']
            )
            
            # Execute registration
            person_id = self.person_service.register_person(command)
            
            return {'personId': str(person_id)}, 201
            
        except ValueError as e:
            return ErrorSerializer.serialize_error(str(e), 'VALIDATION_ERROR'), 400
        except Exception as e:
            return ErrorSerializer.serialize_error(str(e), 'INTERNAL_ERROR'), 500
    
    def authenticate_user(self) -> tuple[Dict[str, Any], int]:
        """
        Authenticate a user and return JWT token.
        
        POST /api/v1/person/authenticate
        Body: {
            "email": "john@example.com",
            "password": "password123"
        }
        """
        try:
            # Parse and validate request data
            data = request.get_json()
            if not data:
                return ErrorSerializer.serialize_error("Request body is required"), 400
            
            # Deserialize request
            auth_data = PersonSerializer.deserialize_auth_request(data)
            
            # Create command
            command = AuthenticateUserCommand(
                email=auth_data['email'],
                password=auth_data['password']
            )
            
            # Execute authentication
            result = self.person_service.authenticate_user(command)
            
            # Serialize response
            response_data = PersonSerializer.serialize_authentication_result(result)
            
            return response_data, 200
            
        except AuthenticationException as e:
            return ErrorSerializer.serialize_authentication_error(), 401
        except ValueError as e:
            return ErrorSerializer.serialize_error(str(e), 'VALIDATION_ERROR'), 400
        except Exception as e:
            return ErrorSerializer.serialize_error(str(e), 'INTERNAL_ERROR'), 500
    
    @require_authentication
    def get_current_user_profile(self) -> tuple[Dict[str, Any], int]:
        """
        Get current authenticated user's profile.
        
        GET /api/v1/person/profile
        Headers: Authorization: Bearer <jwt_token>
        """
        try:
            auth_context = g.auth_context
            
            # Get current user profile
            profile = self.person_service.getCurrentUserProfile(auth_context)
            
            # Serialize response
            response_data = PersonSerializer.serialize_profile(profile)
            
            return response_data, 200
            
        except AuthorizationException as e:
            return ErrorSerializer.serialize_authorization_error(), 403
        except Exception as e:
            return ErrorSerializer.serialize_error(str(e), 'INTERNAL_ERROR'), 500
    
    @require_authentication
    def get_person_profile(self, person_id: str) -> tuple[Dict[str, Any], int]:
        """
        Get profile of a specific person.
        
        GET /api/v1/person/profile/<person_id>
        Headers: Authorization: Bearer <jwt_token>
        """
        try:
            auth_context = g.auth_context
            
            # Parse person ID
            target_person_id = PersonId(person_id)
            
            # Get person profile
            profile = self.person_service.getPersonProfile(target_person_id, auth_context)
            
            # Serialize response
            response_data = PersonSerializer.serialize_profile(profile)
            
            return response_data, 200
            
        except AuthorizationException as e:
            return ErrorSerializer.serialize_authorization_error(), 403
        except ValueError as e:
            return ErrorSerializer.serialize_error("Invalid person ID", 'VALIDATION_ERROR'), 400
        except Exception as e:
            return ErrorSerializer.serialize_error(str(e), 'INTERNAL_ERROR'), 500
    
    @optional_authentication
    def get_leaderboard(self) -> tuple[Dict[str, Any], int]:
        """
        Get leaderboard (public endpoint, but authentication provides personalized data).
        
        GET /api/v1/person/leaderboard
        Headers: Authorization: Bearer <jwt_token> (optional)
        """
        try:
            auth_context = g.auth_context
            
            # Get leaderboard
            leaderboard = self.person_service.getLeaderboard(auth_context)
            
            # Serialize response
            response_data = PersonSerializer.serialize_leaderboard(leaderboard)
            
            return {'leaderboard': response_data}, 200
            
        except Exception as e:
            return ErrorSerializer.serialize_error(str(e), 'INTERNAL_ERROR'), 500


def create_person_controller(person_service: PersonApplicationService) -> Blueprint:
    """
    Factory function to create person controller blueprint.
    
    Args:
        person_service: PersonApplicationService instance
        
    Returns:
        Flask Blueprint for person routes
    """
    controller = PersonController(person_service)
    return controller.blueprint