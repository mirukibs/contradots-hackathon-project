"""
Authentication API module for the Social Scoring System.

This module provides REST API endpoints for user authentication,
including registration, login, logout, and token validation.
"""

from .views import (
    register_user,
    login_user,
    logout_user,
    validate_token,
    get_current_user
)

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    AuthenticationResponseSerializer,
    TokenValidationSerializer,
    UserContextSerializer,
    LogoutSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer
)

__all__ = [
    # Views
    'register_user',
    'login_user', 
    'logout_user',
    'validate_token',
    'get_current_user',
    
    # Serializers
    'UserRegistrationSerializer',
    'UserLoginSerializer',
    'AuthenticationResponseSerializer',
    'TokenValidationSerializer',
    'UserContextSerializer',
    'LogoutSerializer',
    'ErrorResponseSerializer',
    'SuccessResponseSerializer'
]