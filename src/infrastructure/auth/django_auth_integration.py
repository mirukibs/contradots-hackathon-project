"""
Django integration for authentication infrastructure.

This module provides Django-specific integration while keeping
authentication logic separate and testable.
"""

from typing import Optional, Any
import os
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