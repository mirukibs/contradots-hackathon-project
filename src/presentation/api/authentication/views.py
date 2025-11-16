"""
Clean authentication API views for the Social Scoring System.

This module provides Django REST Framework views for authentication endpoints,
integrating with the infrastructure layer authentication system.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from typing import Dict, Any, cast
import uuid

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
)
from ....infrastructure.auth.authentication_bridge import get_authentication_bridge
from ....infrastructure.auth.django_auth_integration import get_authentication_service
from ....application.commands.register_person_command import RegisterPersonCommand
from ....infrastructure.persistence.django_repositories import DjangoPersonRepository
from ....domain.shared.value_objects.person_id import PersonId
import uuid


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request: Request) -> Response:
    """Register a new user account."""
    print("REGISTER_USER VIEW CALLED")
    
    try:
        # Validate input data
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'VALIDATION_ERROR',
                'message': 'Invalid registration data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract required fields
        validated_data = cast(Dict[str, Any], serializer.validated_data)
        
        name: str = validated_data['name']
        email: str = validated_data['email']
        password: str = validated_data['password']
        
        print(f"Registration attempt: {name}, {email}")
        
        try:
            # Step 1: Use Application Layer to register person through proper domain flow
            register_command = RegisterPersonCommand(
                name=name,
                email=email,
                role='participant'  # Default role for registration
            )
            
            # Step 2: Create application service instance with minimal dependencies
            from ....infrastructure.persistence.django_repositories import DjangoPersonRepository
            
            # For registration, we can use a simplified flow without authorization
            person_repo = DjangoPersonRepository()
            
            # Check if person with this email already exists using repository
            try:
                existing_person = person_repo.find_by_email(email)
                return Response({
                    'error': 'REGISTRATION_FAILED',
                    'message': f'Person with email {email} already exists'
                }, status=status.HTTP_409_CONFLICT)
            except ValueError:
                # Person doesn't exist - good, we can proceed
                pass
            
            # Step 3: Validate the command
            register_command.validate()
            
            # Step 4: Create person using domain factory
            from ....domain.person.person import Person
            from ....domain.person.role import Role
            
            # Map command role to domain Role enum
            role_mapping = {
                'participant': Role.MEMBER,
                'lead': Role.LEAD
            }
            domain_role = role_mapping[register_command.role.lower()]
            
            # Create person domain object
            person = Person.create(
                name=register_command.name,
                email=register_command.email,
                role=domain_role
            )
            
            # Step 5: Create authentication user FIRST (this creates Django User)
            auth_bridge = get_authentication_bridge()
            auth_context = auth_bridge.register_user_and_create_context(
                str(person.person_id.value), email, password
            )
            
            if not auth_context:
                return Response({
                    'error': 'AUTH_REGISTRATION_FAILED',
                    'message': 'Authentication registration failed. Email may already be in use.'
                }, status=status.HTTP_409_CONFLICT)
            
            # Step 6: Save person (will link to existing Django User created by auth system)
            person_repo.save(person)
            
            print(f"User registered successfully: {person.person_id}")
            
            # Create response without token - user must login separately
            response_data = {
                'user_id': str(person.person_id.value),
                'name': name,
                'email': email,
                'message': 'User registered successfully. Please log in to get an access token.'
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            # Domain validation error
            error_msg = str(e)
            print(f"DOMAIN VALIDATION ERROR: {error_msg}")
            return Response({
                'error': 'VALIDATION_ERROR',
                'message': f'Registration validation failed: {error_msg}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        error_msg = str(e)
        print(f"REGISTRATION EXCEPTION: {error_msg}")
        print(f"Exception type: {type(e)}")
        return Response({
            'error': 'INTERNAL_ERROR',
            'message': f'Registration failed: {error_msg}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request: Request) -> Response:
    """Authenticate user credentials and return access token."""
    print("LOGIN_USER VIEW CALLED")
    
    try:
        # Validate input data
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'VALIDATION_ERROR',
                'message': 'Invalid login data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract credentials
        validated_data = cast(Dict[str, Any], serializer.validated_data)
        
        email: str = validated_data['email']
        password: str = validated_data['password']
        
        print(f"Login attempt: {email}")
        
        # Authenticate user
        auth_service = get_authentication_service()
        token = auth_service.authenticate_user(email, password)
        
        if not token:
            return Response({
                'error': 'AUTHENTICATION_FAILED',
                'message': 'Invalid email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        print(f"Login successful: {email}")
        
        # Get user context for response
        auth_bridge = get_authentication_bridge()
        auth_context = auth_bridge.create_context_from_token(token)
        
        if not auth_context:
            return Response({
                'error': 'CONTEXT_ERROR',
                'message': 'Unable to create user context'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Create response
        response_data = {
            'token': token,
            'user_id': str(auth_context.current_user_id),
            'email': str(auth_context.email),
            'is_authenticated': True,
            'message': 'Login successful'
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Login error: {e}")
        return Response({
            'error': 'INTERNAL_ERROR', 
            'message': f'Login failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_user(request: Request) -> Response:
    """Logout user by validating authentication token."""
    print("LOGOUT_USER VIEW CALLED")
    
    try:
        # Extract token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return Response({
                'error': 'MISSING_TOKEN',
                'message': 'Authorization header with Bearer token required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        print(f"Logout token: {token[:20]}...")
        
        # Validate token
        auth_service = get_authentication_service()
        token_info = auth_service.validate_token(token)
        
        if not token_info:
            return Response({
                'error': 'INVALID_TOKEN',
                'message': 'Invalid or expired token'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Return success (token validation is sufficient for logout)
        return Response({
            'message': 'Logout successful',
            'is_authenticated': False  
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Logout error: {e}")
        return Response({
            'error': 'INTERNAL_ERROR',
            'message': f'Logout failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def validate_token(request: Request) -> Response:
    """Validate authentication token and return user context."""
    print("VALIDATE_TOKEN VIEW CALLED")
    
    try:
        # Extract token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return Response({
                'error': 'MISSING_TOKEN',
                'message': 'Authorization header with Bearer token required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        print(f"Validating token: {token[:20]}...")
        
        # Validate token
        auth_service = get_authentication_service()
        token_info = auth_service.validate_token(token)
        
        if not token_info:
            return Response({
                'error': 'INVALID_TOKEN',
                'message': 'Invalid or expired token'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get user context
        auth_bridge = get_authentication_bridge()
        auth_context = auth_bridge.create_context_from_token(token)
        
        if not auth_context:
            return Response({
                'error': 'CONTEXT_ERROR', 
                'message': 'Unable to create user context'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Return validation info
        response_data = {
            'valid': True,
            'user_id': str(auth_context.current_user_id),
            'email': str(auth_context.email),
            'is_authenticated': True,
            'message': 'Token is valid'
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Token validation error: {e}")
        return Response({
            'error': 'INTERNAL_ERROR',
            'message': f'Token validation failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_current_user(request: Request) -> Response:
    """Get current user information from token."""
    print("GET_CURRENT_USER VIEW CALLED")
    
    try:
        # Extract token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return Response({
                'error': 'MISSING_TOKEN',
                'message': 'Authorization header with Bearer token required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        print(f"Getting user for token: {token[:20]}...")
        
        # Get user context from token
        auth_bridge = get_authentication_bridge()
        auth_context = auth_bridge.create_context_from_token(token)
        
        if not auth_context or not auth_context.is_authenticated:
            return Response({
                'error': 'INVALID_TOKEN',
                'message': 'Invalid or expired token'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Return user info
        response_data = {
            'user_id': str(auth_context.current_user_id),
            'email': str(auth_context.email),
            'is_authenticated': True,
            'message': 'User information retrieved successfully'
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Get current user error: {e}")
        return Response({
            'error': 'INTERNAL_ERROR',
            'message': f'Failed to get user information: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)