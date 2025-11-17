"""
Django integration for authentication infrastructure.

This module provides Django-specific integration while keeping
authentication logic separate and testable.
"""

from typing import Optional, Any
import os
from rest_framework import authentication
from rest_framework import exceptions
from .authentication_infrastructure import create_authentication_infrastructure


class DjangoAuthenticationService:
    """
    Django service wrapper for authentication infrastructure.
    
    Provides Django-specific authentication operations while delegating
    actual authentication logic to the infrastructure layer.
    """
    
    def __init__(self) -> None:
        """Initialize Django authentication service."""
        secret_key = os.environ.get('SECRET_KEY', 'default-secret-key-change-in-production')
        self._auth_infra, self._user_store = create_authentication_infrastructure(secret_key)
    
    def register_user(self, user_id: str, email: str, password: str) -> bool:
        """
        Register new user.
        
        Args:
            user_id: Unique user identifier
            email: User email address
            password: Plain text password
            
        Returns:
            True if user was registered successfully
        """
        from django.contrib.auth.models import User
        from django.db import IntegrityError
        
        try:
            print(f"DJANGO AUTH: Attempting to register user {email}")
            
            # Check if Django user already exists
            if User.objects.filter(email=email).exists():
                print(f"DJANGO AUTH: Django user with email {email} already exists")
                return False
            
            # Create Django User first
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                is_active=True
            )
            print(f"DJANGO AUTH: Created Django user {user.username}")
            
            # Then store in authentication infrastructure
            hashed_password = self._auth_infra.hash_password(password)
            auth_result = self._user_store.create_user(user_id, email, hashed_password)
            print(f"DJANGO AUTH: InMemory store result: {auth_result}")
            
            return auth_result
            
        except IntegrityError as e:
            # User already exists
            print(f"DJANGO AUTH: IntegrityError - User already exists: {e}")
            return False
        except Exception as e:
            print(f"DJANGO AUTH: Registration error: {e}")
            return False
    
    def authenticate_user(self, email: str, password: str) -> Optional[str]:
        """
        Authenticate user and return token.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            Authentication token if successful, None otherwise
        """
        user_info = self._user_store.authenticate_user(email, password, self._auth_infra)
        if user_info:
            return self._auth_infra.create_authentication_token(
                user_info['user_id'], 
                user_info['email']
            )
        return None
    
    def validate_token(self, token: str) -> Optional[dict[str, Any]]:
        """
        Validate authentication token.
        
        Args:
            token: Token to validate
            
        Returns:
            User information if token is valid
        """
        return self._auth_infra.validate_token(token)
    
    def logout_user(self, token: str) -> bool:
        """
        Logout user by revoking token.
        
        Args:
            token: Token to revoke
            
        Returns:
            True if logout was successful
        """
        return self._auth_infra.revoke_token(token)
    
    def get_user_info(self, email: str) -> Optional[dict[str, Any]]:
        """
        Get user information by email.
        
        Args:
            email: User email
            
        Returns:
            User information if found
        """
        return self._user_store.get_user_by_email(email)


# Global service instance
_auth_service: Optional[DjangoAuthenticationService] = None


def get_authentication_service() -> DjangoAuthenticationService:
    """
    Get global authentication service instance.
    
    Returns:
        Django authentication service instance
    """
    global _auth_service
    if _auth_service is None:
        _auth_service = DjangoAuthenticationService()
    return _auth_service


def reset_authentication_service() -> None:
    """Reset authentication service (useful for testing)."""
    global _auth_service
    _auth_service = None

class CustomTokenAuthentication(authentication.BaseAuthentication):
    """
    Custom token authentication for Django REST Framework.
    
    Integrates our TokenAuthenticationInfrastructure with DRF's
    authentication system.
    """
    
    keyword = 'Token'
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
        
        try:
            # Extract token from "Token <token>" format
            parts = auth_header.split()
            if len(parts) != 2 or parts[0] != self.keyword:
                return None
            
            token = parts[1]
            
            # Get authentication service
            auth_service = get_authentication_service()
            
            # Validate token
            user_info = auth_service.validate_token(token)
            
            if not user_info:
                raise exceptions.AuthenticationFailed('Invalid or expired token')
            
            # Create a simple user object with required attributes
            class AuthenticatedUser:
                def __init__(self, user_id, email):
                    self.id = user_id
                    self.pk = user_id  # Primary key required by DRF throttling
                    self.username = user_id
                    self.email = email
                    self.is_authenticated = True
                    self.is_active = True
                    self.is_anonymous = False
                    self.is_staff = False
                    
                    # Add groups property for role checking
                    class MockGroups:
                        def filter(self, name=None):
                            class MockQuerySet:
                                def exists(self):
                                    return False
                            return MockQuerySet()
                    
                    self.groups = MockGroups()
                
                def __str__(self):
                    return self.email
            
            user = AuthenticatedUser(user_info['user_id'], user_info['email'])
            
            return (user, token)
            
        except exceptions.AuthenticationFailed:
            raise
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the WWW-Authenticate
        header in a 401 Unauthenticated response.
        """
        return self.keyword
