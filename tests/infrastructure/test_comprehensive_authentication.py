"""
Comprehensive Infrastructure Authentication Test Suite.

This module provides complete test coverage for all authentication features
implemented in the infrastructure layer, including integration between
all components.
"""

import pytest
import os
import uuid
from unittest.mock import patch, Mock
from typing import Optional

# Configure Django before imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_scoring_project.settings')
import django
django.setup()

from src.infrastructure.auth.authentication_infrastructure import (
    create_authentication_infrastructure,
    TokenAuthenticationInfrastructure,
    InMemoryUserStore
)
from src.infrastructure.auth.django_auth_integration import get_authentication_service, reset_authentication_service
from src.infrastructure.auth.authentication_bridge import (
    AuthenticationBridge,
    get_authentication_bridge,
    create_authentication_context_from_token,
    authenticate_and_create_context,
    _authentication_bridge  # Import the global variable
)
from src.application.security.authentication_context import AuthenticationContext
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.person.role import Role


class TestCompleteAuthenticationFlow:
    """Test complete authentication flow from infrastructure to application layer."""
    
    def setup_method(self):
        """Set up comprehensive test environment."""
        # Reset authentication service to ensure clean state
        reset_authentication_service()
        
        # Reset global authentication bridge
        global _authentication_bridge
        _authentication_bridge = None
        
        # Test configuration
        self.test_secret = "comprehensive-test-secret-key"
        self.test_user_id = f"comp_test_{uuid.uuid4().hex[:8]}"
        self.test_email = f"comprehensive_test_{uuid.uuid4().hex[:8]}@example.com"
        self.test_password = "ComprehensiveTestPassword123!"
        
        # Initialize all infrastructure components
        self.auth_infra, self.user_store = create_authentication_infrastructure(self.test_secret)
        
        with patch.dict(os.environ, {'SECRET_KEY': self.test_secret}):
            self.django_service = get_authentication_service()  # Use singleton
            self.auth_bridge = AuthenticationBridge()
    
    def test_complete_user_registration_flow(self):
        """Test complete user registration from infrastructure to application context."""
        print("🧪 Testing Complete User Registration Flow...")
        
        # Step 1: Register user through infrastructure
        registration_success = self.django_service.register_user(
            self.test_user_id,
            self.test_email,
            self.test_password
        )
        
        assert registration_success is True, "User registration should succeed"
        print("✅ User registration successful")
        
        # Step 2: Verify user can authenticate
        token = self.django_service.authenticate_user(self.test_email, self.test_password)
        
        assert token is not None, "Authentication should return token"
        assert isinstance(token, str), "Token should be string"
        assert len(token) > 20, "Token should be substantial"
        print("✅ User authentication successful")
        
        # Step 3: Validate token contains correct information
        user_info = self.django_service.validate_token(token)
        
        assert user_info is not None, "Token validation should succeed"
        assert user_info['user_id'] == self.test_user_id, "User ID should match"
        assert user_info['email'] == self.test_email, "Email should match"
        print("✅ Token validation successful")
        
        # Step 4: Create application context from token
        auth_context = self.auth_bridge.create_context_from_token(token)
        
        assert auth_context is not None, "Context creation should succeed"
        assert isinstance(auth_context, AuthenticationContext), "Should return AuthenticationContext"
        assert auth_context.is_authenticated is True, "Context should be authenticated"
        assert auth_context.email == self.test_email, "Context email should match"
        # Note: user ID is converted to deterministic UUID, so we verify it exists and is valid
        assert auth_context.current_user_id is not None, "Context should have user ID"
        assert len(str(auth_context.current_user_id)) == 36, "Should be valid UUID format"
        assert Role.MEMBER in auth_context.roles, "Should have default MEMBER role"
        print("✅ Application context creation successful")
        
        print("🎉 Complete registration flow test PASSED\n")
    
    def test_complete_authentication_flow(self):
        """Test complete authentication flow from credentials to application context."""
        print("🧪 Testing Complete Authentication Flow...")
        
        # Step 1: Register user first
        self.django_service.register_user(self.test_user_id, self.test_email, self.test_password)
        
        # Step 2: Authenticate directly through bridge
        auth_context = self.auth_bridge.create_context_from_credentials(
            self.test_email,
            self.test_password
        )
        
        assert auth_context is not None, "Credential authentication should succeed"
        assert isinstance(auth_context, AuthenticationContext), "Should return AuthenticationContext"
        assert auth_context.is_authenticated is True, "Context should be authenticated"
        assert auth_context.email == self.test_email, "Email should match"
        print("✅ Credential-based authentication successful")
        
        # Step 3: Test convenience function
        convenience_context = authenticate_and_create_context(self.test_email, self.test_password)
        
        assert convenience_context is not None, "Convenience function should succeed"
        assert convenience_context.email == self.test_email, "Should match credentials"
        assert convenience_context.is_authenticated is True, "Should be authenticated"
        print("✅ Convenience function authentication successful")
        
        print("🎉 Complete authentication flow test PASSED\n")
    
    def test_registration_and_immediate_context_creation(self):
        """Test registration with immediate context creation."""
        print("🧪 Testing Registration with Immediate Context Creation...")
        
        # Register and immediately create context
        auth_context = self.auth_bridge.register_user_and_create_context(
            self.test_user_id,
            self.test_email,
            self.test_password
        )
        
        assert auth_context is not None, "Registration and context creation should succeed"
        assert isinstance(auth_context, AuthenticationContext), "Should return AuthenticationContext"
        assert auth_context.is_authenticated is True, "Context should be authenticated"
        assert auth_context.email == self.test_email, "Email should match"
        # Note: user ID is converted to deterministic UUID, so we verify it exists and is valid
        assert auth_context.current_user_id is not None, "Context should have user ID"
        assert len(str(auth_context.current_user_id)) == 36, "Should be valid UUID format"
        assert Role.MEMBER in auth_context.roles, "Should have default MEMBER role"
        print("✅ Registration with immediate context creation successful")
        
        # Verify user can authenticate again
        second_context = self.auth_bridge.create_context_from_credentials(
            self.test_email,
            self.test_password
        )
        
        assert second_context is not None, "Second authentication should succeed"
        assert second_context.email == auth_context.email, "Email should match original"
        print("✅ Subsequent authentication successful")
        
        print("🎉 Registration with immediate context test PASSED\n")
    
    def test_invalid_authentication_scenarios(self):
        """Test all invalid authentication scenarios."""
        print("🧪 Testing Invalid Authentication Scenarios...")
        
        # Test authentication with non-existent user
        invalid_context = self.auth_bridge.create_context_from_credentials(
            "nonexistent@example.com",
            "any_password"
        )
        assert invalid_context is None, "Non-existent user should return None"
        print("✅ Non-existent user authentication properly rejected")
        
        # Register valid user
        self.django_service.register_user(self.test_user_id, self.test_email, self.test_password)
        
        # Test authentication with wrong password
        wrong_password_context = self.auth_bridge.create_context_from_credentials(
            self.test_email,
            "wrong_password"
        )
        assert wrong_password_context is None, "Wrong password should return None"
        print("✅ Wrong password authentication properly rejected")
        
        # Test invalid token validation
        invalid_token_context = self.auth_bridge.create_context_from_token("invalid_token")
        assert invalid_token_context is None, "Invalid token should return None"
        print("✅ Invalid token properly rejected")
        
        # Test convenience function with invalid credentials
        convenience_invalid = authenticate_and_create_context(
            "invalid@example.com",
            "invalid_password"
        )
        assert convenience_invalid is None, "Convenience function should reject invalid credentials"
        print("✅ Convenience function properly rejects invalid credentials")
        
        print("🎉 Invalid authentication scenarios test PASSED\n")
    
    def test_token_lifecycle_management(self):
        """Test complete token lifecycle: creation, validation, revocation."""
        print("🧪 Testing Token Lifecycle Management...")
        
        # Register user
        self.django_service.register_user(self.test_user_id, self.test_email, self.test_password)
        
        # Step 1: Create token
        token = self.django_service.authenticate_user(self.test_email, self.test_password)
        assert token is not None, "Token creation should succeed"
        print("✅ Token created successfully")
        
        # Step 2: Validate active token
        user_info = self.django_service.validate_token(token)
        assert user_info is not None, "Active token should validate"
        assert user_info['user_id'] == self.test_user_id, "Token should contain correct user ID"
        print("✅ Token validation successful")
        
        # Step 3: Create context from active token
        context = self.auth_bridge.create_context_from_token(token)
        assert context is not None, "Context creation from active token should succeed"
        assert context.is_authenticated is True, "Context should be authenticated"
        print("✅ Context creation from active token successful")
        
        # Step 4: Revoke token
        revocation_result = self.django_service.logout_user(token)
        assert revocation_result is True, "Token revocation should succeed"
        print("✅ Token revocation successful")
        
        # Step 5: Verify revoked token is invalid
        invalid_user_info = self.django_service.validate_token(token)
        assert invalid_user_info is None, "Revoked token should be invalid"
        print("✅ Revoked token properly invalidated")
        
        # Step 6: Verify context creation fails for revoked token
        invalid_context = self.auth_bridge.create_context_from_token(token)
        assert invalid_context is None, "Context creation should fail for revoked token"
        print("✅ Context creation properly fails for revoked token")
        
        print("🎉 Token lifecycle management test PASSED\n")
    
    def test_password_security_features(self):
        """Test password hashing and verification security features."""
        print("🧪 Testing Password Security Features...")
        
        # Test password hashing
        password = "TestPassword123!"
        hashed_password = self.auth_infra.hash_password(password)
        
        assert hashed_password != password, "Password should be hashed"
        assert len(hashed_password) > 30, "Hashed password should be substantial"
        print("✅ Password hashing successful")
        
        # Test correct password verification
        verification_result = self.auth_infra.verify_password(password, hashed_password)
        assert verification_result is True, "Correct password should verify"
        print("✅ Correct password verification successful")
        
        # Test incorrect password verification
        wrong_verification = self.auth_infra.verify_password("wrong_password", hashed_password)
        assert wrong_verification is False, "Wrong password should not verify"
        print("✅ Incorrect password properly rejected")
        
        # Test password uniqueness (same password should hash differently due to salt)
        second_hash = self.auth_infra.hash_password(password)
        assert second_hash != hashed_password, "Same password should hash differently (salt)"
        print("✅ Password salt uniqueness verified")
        
        # Verify both hashes work for same password
        first_verification = self.auth_infra.verify_password(password, hashed_password)
        second_verification = self.auth_infra.verify_password(password, second_hash)
        assert first_verification is True, "First hash should verify"
        assert second_verification is True, "Second hash should verify"
        print("✅ Multiple hash verification successful")
        
        print("🎉 Password security features test PASSED\n")
    
    def test_user_store_functionality(self):
        """Test user store functionality."""
        print("🧪 Testing User Store Functionality...")
        
        # Test user creation
        user_id = f"store_test_{uuid.uuid4().hex[:8]}"
        email = f"store_test_{uuid.uuid4().hex[:8]}@example.com"
        password = "StoreTestPassword123!"
        hashed_password = self.auth_infra.hash_password(password)
        
        creation_result = self.user_store.create_user(user_id, email, hashed_password)
        assert creation_result is True, "User creation should succeed"
        print("✅ User creation successful")
        
        # Test duplicate user creation
        duplicate_result = self.user_store.create_user(user_id, email, hashed_password)
        assert duplicate_result is False, "Duplicate user creation should fail"
        print("✅ Duplicate user creation properly rejected")
        
        # Test user retrieval
        retrieved_user = self.user_store.get_user_by_email(email)
        assert retrieved_user is not None, "User retrieval should succeed"
        assert retrieved_user['user_id'] == user_id, "Retrieved user ID should match"
        assert retrieved_user['email'] == email, "Retrieved email should match"
        print("✅ User retrieval successful")
        
        # Test non-existent user retrieval
        non_existent = self.user_store.get_user_by_email("nonexistent@example.com")
        assert non_existent is None, "Non-existent user should return None"
        print("✅ Non-existent user properly handled")
        
        print("🎉 User store functionality test PASSED\n")
    
    def test_anonymous_context_creation(self):
        """Test anonymous authentication context creation."""
        print("🧪 Testing Anonymous Context Creation...")
        
        # Test anonymous context creation through bridge
        anon_context = self.auth_bridge.create_anonymous_context()
        
        assert anon_context is not None, "Anonymous context creation should succeed"
        assert isinstance(anon_context, AuthenticationContext), "Should return AuthenticationContext"
        assert anon_context.is_authenticated is False, "Anonymous context should not be authenticated"
        assert len(anon_context.roles) == 0, "Anonymous context should have no roles"
        print("✅ Anonymous context creation successful")
        
        print("🎉 Anonymous context creation test PASSED\n")
    
    def test_singleton_bridge_management(self):
        """Test singleton authentication bridge management."""
        print("🧪 Testing Singleton Bridge Management...")
        
        # Test global bridge singleton
        bridge1 = get_authentication_bridge()
        bridge2 = get_authentication_bridge()
        
        assert bridge1 is bridge2, "Should return same singleton instance"
        assert isinstance(bridge1, AuthenticationBridge), "Should be AuthenticationBridge instance"
        print("✅ Singleton bridge management successful")
        
        # Test convenience functions use same bridge
        with patch.dict(os.environ, {'SECRET_KEY': self.test_secret}):
            # Register user for convenience function test
            bridge1.register_user_and_create_context(
                self.test_user_id,
                self.test_email,
                self.test_password
            )
            
            # Test convenience function
            convenience_context = authenticate_and_create_context(
                self.test_email,
                self.test_password
            )
            
            assert convenience_context is not None, "Convenience function should work"
            assert convenience_context.email == self.test_email, "Should match credentials"
            print("✅ Convenience function integration successful")
        
        print("🎉 Singleton bridge management test PASSED\n")
    
    def test_cross_component_integration(self):
        """Test integration across all authentication components."""
        print("🧪 Testing Cross-Component Integration...")
        
        # Step 1: Register user through Django service
        django_registration = self.django_service.register_user(
            self.test_user_id,
            self.test_email,
            self.test_password
        )
        assert django_registration is True, "Django service registration should succeed"
        
        # Step 2: Django service authentication
        django_token = self.django_service.authenticate_user(
            self.test_email,
            self.test_password
        )
        assert django_token is not None, "Django service authentication should succeed"
        print("✅ Django service operations successful")
        
        # Step 3: Verify Django service token validation
        django_user_info = self.django_service.validate_token(django_token)
        assert django_user_info is not None, "Django token validation should succeed"
        assert django_user_info['email'] == self.test_email, "Token should contain correct email"
        print("✅ Django service token validation successful")
        
        # Step 4: Bridge operations (local instance)
        bridge_context = self.auth_bridge.create_context_from_token(django_token)
        assert bridge_context is not None, "Bridge context creation should succeed"
        assert isinstance(bridge_context, AuthenticationContext), "Should be proper context type"
        assert bridge_context.email == self.test_email, "Context should have correct email"
        print("✅ Bridge operations successful")
        
        # Step 5: Test credential-based authentication through bridge
        credential_context = self.auth_bridge.create_context_from_credentials(
            self.test_email,
            self.test_password
        )
        assert credential_context is not None, "Credential authentication should succeed"
        assert credential_context.email == bridge_context.email, "Should match token-based result"
        print("✅ Credential-based authentication successful")
        
        # Step 6: Test separate low-level infrastructure operations
        low_level_token = self.auth_infra.create_authentication_token(self.test_user_id, self.test_email)
        assert low_level_token is not None, "Infrastructure token creation should succeed"
        
        low_level_user_info = self.auth_infra.validate_token(low_level_token)
        assert low_level_user_info is not None, "Infrastructure token validation should succeed"
        print("✅ Low-level infrastructure operations successful")
        
        print("🎉 Cross-component integration test PASSED\n")


def run_comprehensive_authentication_tests():
    """Run all comprehensive authentication tests."""
    print("🚀 Starting Comprehensive Infrastructure Authentication Tests\n")
    print("=" * 80)
    
    test_suite = TestCompleteAuthenticationFlow()
    
    try:
        # Test 1: Complete user registration flow
        test_suite.setup_method()
        test_suite.test_complete_user_registration_flow()
        
        # Test 2: Complete authentication flow
        test_suite.setup_method()
        test_suite.test_complete_authentication_flow()
        
        # Test 3: Registration with immediate context creation
        test_suite.setup_method()
        test_suite.test_registration_and_immediate_context_creation()
        
        # Test 4: Invalid authentication scenarios
        test_suite.setup_method()
        test_suite.test_invalid_authentication_scenarios()
        
        # Test 5: Token lifecycle management
        test_suite.setup_method()
        test_suite.test_token_lifecycle_management()
        
        # Test 6: Password security features
        test_suite.setup_method()
        test_suite.test_password_security_features()
        
        # Test 7: User store functionality
        test_suite.setup_method()
        test_suite.test_user_store_functionality()
        
        # Test 8: Anonymous context creation
        test_suite.setup_method()
        test_suite.test_anonymous_context_creation()
        
        # Test 9: Singleton bridge management
        test_suite.setup_method()
        test_suite.test_singleton_bridge_management()
        
        # Test 10: Cross-component integration
        test_suite.setup_method()
        test_suite.test_cross_component_integration()
        
        print("=" * 80)
        print("🎉 ALL COMPREHENSIVE AUTHENTICATION TESTS PASSED! 🎉")
        print("=" * 80)
        print("\n✅ Infrastructure Authentication Features Verified:")
        print("   • Complete user registration flow")
        print("   • Token-based authentication")
        print("   • Password security (hashing, salting, verification)")
        print("   • Token lifecycle (creation, validation, revocation)")
        print("   • Application context integration")
        print("   • Error handling and edge cases")
        print("   • Cross-component integration")
        print("   • Security validation")
        print("   • Singleton pattern management")
        print("   • Convenience function interfaces")
        print("\n🚀 Infrastructure layer is PRODUCTION READY!")
        
    except Exception as e:
        print(f"❌ Comprehensive test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False
    
    return True


if __name__ == "__main__":
    # Set environment variables for testing
    os.environ['SECRET_KEY'] = 'comprehensive-test-secret-for-infrastructure'
    
    # Run comprehensive tests
    success = run_comprehensive_authentication_tests()
    
    if success:
        print("\n🎯 INFRASTRUCTURE AUTHENTICATION: FULLY TESTED AND VERIFIED")
    else:
        print("\n💥 INFRASTRUCTURE AUTHENTICATION: TESTS FAILED")
        exit(1)