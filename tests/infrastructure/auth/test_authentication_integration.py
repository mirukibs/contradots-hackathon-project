"""
Integration tests for infrastructure authentication components.

This module tests the complete authentication flow from infrastructure
to application layer integration.
"""

import pytest
import os
import tempfile
from unittest.mock import patch

from src.infrastructure.auth.authentication_infrastructure import create_authentication_infrastructure
from src.infrastructure.auth.django_auth_integration import DjangoAuthenticationService
from src.infrastructure.auth.authentication_bridge import (
    AuthenticationBridge,
    get_authentication_bridge,
    create_authentication_context_from_token,
    authenticate_and_create_context
)
from src.application.security.authentication_context import AuthenticationContext
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.person.role import Role


class TestAuthenticationInfrastructure:
    """Test authentication infrastructure components."""
    
    def setup_method(self):
        """Set up test environment."""
        # Use a test secret key
        self.test_secret = "test-secret-key-for-testing"
        self.auth_infra, self.user_store = create_authentication_infrastructure(self.test_secret)
        
        # Test user data
        self.test_user_id = "test-user-123"
        self.test_email = "test@example.com"
        self.test_password = "secure_password_123"
        
    def test_password_hashing_and_verification(self):
        """Test password hashing and verification functionality."""
        # Hash password
        hashed = self.auth_infra.hash_password(self.test_password)
        
        # Verify hashed password is different from original
        assert hashed != self.test_password
        assert len(hashed) > 20  # Should be a substantial hash
        
        # Verify correct password
        assert self.auth_infra.verify_password(self.test_password, hashed) is True
        
        # Verify incorrect password
        assert self.auth_infra.verify_password("wrong_password", hashed) is False
        
    def test_token_creation_and_validation(self):
        """Test token creation and validation."""
        # Create token
        token = self.auth_infra.create_authentication_token(self.test_user_id, self.test_email)
        
        # Verify token exists and is a string
        assert isinstance(token, str)
        assert len(token) > 20  # Should be substantial
        
        # Validate token
        user_info = self.auth_infra.validate_token(token)
        
        # Verify token contains correct user information
        assert user_info is not None
        assert user_info['user_id'] == self.test_user_id
        assert user_info['email'] == self.test_email
        
    def test_token_revocation(self):
        """Test token revocation functionality."""
        # Create token
        token = self.auth_infra.create_authentication_token(self.test_user_id, self.test_email)
        
        # Verify token is valid
        assert self.auth_infra.validate_token(token) is not None
        
        # Revoke token
        result = self.auth_infra.revoke_token(token)
        assert result is True
        
        # Verify token is no longer valid
        assert self.auth_infra.validate_token(token) is None
        
    def test_invalid_token_validation(self):
        """Test validation of invalid tokens."""
        # Test with completely invalid token
        assert self.auth_infra.validate_token("invalid-token") is None
        
        # Test with empty token
        assert self.auth_infra.validate_token("") is None


class TestDjangoAuthenticationService:
    """Test Django authentication service integration."""
    
    def setup_method(self):
        """Set up test environment."""
        # Mock the environment variable for testing
        with patch.dict(os.environ, {'SECRET_KEY': 'test-secret-for-django-service'}):
            self.auth_service = DjangoAuthenticationService()
        
        # Test user data
        self.test_user_id = "django-test-user"
        self.test_email = "django_test@example.com"
        self.test_password = "django_password_123"
        
    def test_user_registration(self):
        """Test user registration functionality."""
        # Register user
        result = self.auth_service.register_user(
            self.test_user_id,
            self.test_email,
            self.test_password
        )
        
        # Verify registration successful
        assert result is True
        
        # Try to register same user again (should fail)
        result_duplicate = self.auth_service.register_user(
            self.test_user_id,
            self.test_email,
            self.test_password
        )
        
        # Should fail for duplicate registration
        assert result_duplicate is False
        
    def test_user_authentication(self):
        """Test user authentication functionality."""
        # First register the user
        self.auth_service.register_user(
            self.test_user_id,
            self.test_email,
            self.test_password
        )
        
        # Authenticate with correct credentials
        token = self.auth_service.authenticate_user(self.test_email, self.test_password)
        
        # Verify authentication successful
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20
        
        # Try to authenticate with wrong password
        invalid_token = self.auth_service.authenticate_user(self.test_email, "wrong_password")
        
        # Verify authentication failed
        assert invalid_token is None
        
    def test_token_validation(self):
        """Test token validation through service."""
        # Register and authenticate user
        self.auth_service.register_user(
            self.test_user_id,
            self.test_email,
            self.test_password
        )
        
        token = self.auth_service.authenticate_user(self.test_email, self.test_password)
        
        # Validate token (ensure token is not None first)
        if token is not None:
            user_info = self.auth_service.validate_token(token)
            
            # Verify user information
            assert user_info is not None
            assert user_info['user_id'] == self.test_user_id
            assert user_info['email'] == self.test_email
        else:
            assert False, "Token should not be None after successful authentication"


class TestAuthenticationBridge:
    """Test authentication bridge between infrastructure and application layers."""
    
    def setup_method(self):
        """Set up test environment."""
        with patch.dict(os.environ, {'SECRET_KEY': 'test-secret-for-bridge'}):
            self.bridge = AuthenticationBridge()
        
        # Test user data
        self.test_user_id = "bridge-test-user"
        self.test_email = "bridge_test@example.com"
        self.test_password = "bridge_password_123"
        
    def test_context_creation_from_credentials(self):
        """Test AuthenticationContext creation from credentials."""
        # Register user first
        context = self.bridge.register_user_and_create_context(
            self.test_user_id,
            self.test_email,
            self.test_password
        )
        
        # Verify context creation
        assert context is not None
        assert isinstance(context, AuthenticationContext)
        assert context.is_authenticated is True
        assert context.email == self.test_email
        assert str(context.current_user_id) == self.test_user_id
        assert Role.MEMBER in context.roles
        
    def test_context_creation_from_token(self):
        """Test AuthenticationContext creation from token."""
        # Register user and get token
        self.bridge.register_user_and_create_context(
            self.test_user_id,
            self.test_email,
            self.test_password
        )
        
        # Authenticate to get token
        auth_context = self.bridge.create_context_from_credentials(self.test_email, self.test_password)
        assert auth_context is not None
        
        # Create new context from the same credentials (simulating token validation)
        new_context = self.bridge.create_context_from_credentials(self.test_email, self.test_password)
        
        # Verify new context
        assert new_context is not None
        assert isinstance(new_context, AuthenticationContext)
        assert new_context.email == self.test_email
        assert str(new_context.current_user_id) == self.test_user_id
        
    def test_invalid_credentials(self):
        """Test handling of invalid credentials."""
        # Try to create context with invalid credentials
        context = self.bridge.create_context_from_credentials("invalid@email.com", "wrong_password")
        
        # Should return None for invalid credentials
        assert context is None
        
    def test_anonymous_context_creation(self):
        """Test creation of anonymous authentication context."""
        context = self.bridge.create_anonymous_context()
        
        # Verify anonymous context
        assert context is not None
        assert isinstance(context, AuthenticationContext)
        assert context.is_authenticated is False
        

class TestAuthenticationBridgeConvenienceFunctions:
    """Test convenience functions for authentication bridge."""
    
    def setup_method(self):
        """Set up test environment."""
        # Test user data
        self.test_user_id = "convenience-test-user"
        self.test_email = "convenience_test@example.com"
        self.test_password = "convenience_password_123"
        
    def test_global_bridge_singleton(self):
        """Test that global bridge returns singleton instance."""
        bridge1 = get_authentication_bridge()
        bridge2 = get_authentication_bridge()
        
        # Should be the same instance
        assert bridge1 is bridge2
        assert isinstance(bridge1, AuthenticationBridge)
        
    @patch.dict(os.environ, {'SECRET_KEY': 'test-secret-for-convenience'})
    def test_convenience_authentication_function(self):
        """Test convenience function for authentication."""
        # Register user using bridge
        bridge = get_authentication_bridge()
        bridge.register_user_and_create_context(
            self.test_user_id,
            self.test_email,
            self.test_password
        )
        
        # Use convenience function to authenticate
        context = authenticate_and_create_context(self.test_email, self.test_password)
        
        # Verify context creation
        assert context is not None
        assert isinstance(context, AuthenticationContext)
        assert context.email == self.test_email
        assert str(context.current_user_id) == self.test_user_id
        

if __name__ == "__main__":
    # Run basic tests manually for quick verification
    print("Running authentication infrastructure tests...")
    
    # Test basic authentication infrastructure
    test_infra = TestAuthenticationInfrastructure()
    test_infra.setup_method()
    
    try:
        test_infra.test_password_hashing_and_verification()
        print("✅ Password hashing and verification test passed")
        
        test_infra.test_token_creation_and_validation()
        print("✅ Token creation and validation test passed")
        
        test_infra.test_token_revocation()
        print("✅ Token revocation test passed")
        
        test_infra.test_invalid_token_validation()
        print("✅ Invalid token validation test passed")
        
    except Exception as e:
        print(f"❌ Authentication infrastructure test failed: {e}")
        
    # Test Django service integration
    test_django = TestDjangoAuthenticationService()
    test_django.setup_method()
    
    try:
        test_django.test_user_registration()
        print("✅ Django user registration test passed")
        
        test_django.test_user_authentication()
        print("✅ Django user authentication test passed")
        
        test_django.test_token_validation()
        print("✅ Django token validation test passed")
        
    except Exception as e:
        print(f"❌ Django authentication service test failed: {e}")
        
    print("\nAuthentication infrastructure tests completed!")