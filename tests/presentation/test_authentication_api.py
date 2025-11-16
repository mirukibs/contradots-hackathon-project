"""
Comprehensive tests for authentication API endpoints.

This module tests all authentication API endpoints including registration,
login, logout, token validation, and user context retrieval.
"""

import json
import os
import uuid
from unittest.mock import patch

# Configure Django FIRST before any Django imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_scoring_project.settings')
import django
django.setup()

# Now import Django modules after configuration
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from src.infrastructure.auth.django_auth_integration import reset_authentication_service
from src.infrastructure.auth.authentication_bridge import get_authentication_bridge


class AuthenticationAPITestCase(APITestCase):
    """Base test case for authentication API tests."""
    
    def setUp(self):
        """Set up test environment."""
        # Reset authentication service for clean state
        reset_authentication_service()
        
        # Set test secret key
        self.test_secret = "test-api-secret-key"
        os.environ['SECRET_KEY'] = self.test_secret
        
        # Create API client
        self.client = APIClient()
        
        # Test data - no user_id needed anymore, it's auto-generated
        self.test_user_data = {
            'email': f'api_test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'ApiTestPassword123!',
            'confirm_password': 'ApiTestPassword123!'
        }
        
        # API endpoints
        self.register_url = '/api/v1/auth/register/'
        self.login_url = '/api/v1/auth/login/'
        self.logout_url = '/api/v1/auth/logout/'
        self.validate_url = '/api/v1/auth/validate/'
        self.me_url = '/api/v1/auth/me/'


class UserRegistrationAPITests(AuthenticationAPITestCase):
    """Test user registration API endpoint."""
    
    def test_successful_registration(self):
        """Test successful user registration."""
        response = self.client.post(self.register_url, self.test_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        # Registration should NOT return a token - user must login separately
        self.assertNotIn('token', response_data)
        self.assertIn('user_id', response_data)
        self.assertIn('email', response_data)
        self.assertEqual(response_data['email'], self.test_user_data['email'])
        self.assertIn('Please log in', response_data['message'])
        
    def test_registration_with_invalid_email(self):
        """Test registration with invalid email format."""
        invalid_data = self.test_user_data.copy()
        invalid_data['email'] = 'invalid-email'
        
        response = self.client.post(self.register_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(response_data['error'], 'VALIDATION_ERROR')
        
    def test_registration_with_weak_password(self):
        """Test registration with weak password."""
        weak_data = self.test_user_data.copy()
        weak_data['password'] = 'weak'
        weak_data['confirm_password'] = 'weak'
        
        response = self.client.post(self.register_url, weak_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(response_data['error'], 'VALIDATION_ERROR')
        
    def test_registration_with_mismatched_passwords(self):
        """Test registration with mismatched passwords."""
        mismatch_data = self.test_user_data.copy()
        mismatch_data['confirm_password'] = 'DifferentPassword123!'
        
        response = self.client.post(self.register_url, mismatch_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(response_data['error'], 'VALIDATION_ERROR')
        
    def test_registration_with_missing_fields(self):
        """Test registration with missing required fields."""
        incomplete_data = {
            'email': self.test_user_data['email'],
            # Missing password, confirm_password
        }
        
        response = self.client.post(self.register_url, incomplete_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(response_data['error'], 'VALIDATION_ERROR')
        
    def test_duplicate_user_registration(self):
        """Test registration with already existing user."""
        # Register user first time
        response1 = self.client.post(self.register_url, self.test_user_data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Try to register same user again
        response2 = self.client.post(self.register_url, self.test_user_data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_409_CONFLICT)
        response_data = response2.json()
        self.assertEqual(response_data['error'], 'REGISTRATION_FAILED')


class UserLoginAPITests(AuthenticationAPITestCase):
    """Test user login API endpoint."""
    
    def setUp(self):
        """Set up test environment with registered user."""
        super().setUp()
        # Register a user for login tests (registration doesn't return token)
        self.client.post(self.register_url, self.test_user_data, format='json')
        
    def test_successful_login(self):
        """Test successful user login."""
        login_data = {
            'email': self.test_user_data['email'],
            'password': self.test_user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn('token', response_data)
        self.assertIn('user_id', response_data)
        self.assertEqual(response_data['email'], login_data['email'])
        self.assertEqual(response_data['is_authenticated'], True)
        
    def test_login_with_wrong_password(self):
        """Test login with incorrect password."""
        login_data = {
            'email': self.test_user_data['email'],
            'password': 'WrongPassword123!'
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response_data = response.json()
        self.assertEqual(response_data['error'], 'AUTHENTICATION_FAILED')
        
    def test_login_with_nonexistent_user(self):
        """Test login with non-existent user."""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123!'
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response_data = response.json()
        self.assertEqual(response_data['error'], 'AUTHENTICATION_FAILED')
        
    def test_login_with_invalid_email_format(self):
        """Test login with invalid email format."""
        login_data = {
            'email': 'invalid-email-format',
            'password': self.test_user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(response_data['error'], 'VALIDATION_ERROR')
        
    def test_login_with_missing_fields(self):
        """Test login with missing required fields."""
        incomplete_data = {
            'email': self.test_user_data['email']
            # Missing password
        }
        
        response = self.client.post(self.login_url, incomplete_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(response_data['error'], 'VALIDATION_ERROR')


class TokenValidationAPITests(AuthenticationAPITestCase):
    """Test token validation API endpoint."""
    
    def setUp(self):
        """Set up test environment with authenticated user."""
        super().setUp()
        # Register user first
        self.client.post(self.register_url, self.test_user_data, format='json')
        # Then login to get token
        login_data = {
            'email': self.test_user_data['email'],
            'password': self.test_user_data['password']
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        self.token = login_response.json()['token']
        
    def test_valid_token_validation(self):
        """Test validation of valid token."""
        # Test with Authorization header
        response = self.client.post(
            self.validate_url, 
            {}, 
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn('user_id', response_data)
        self.assertEqual(response_data['email'], self.test_user_data['email'])
        self.assertEqual(response_data['is_authenticated'], True)
        
    def test_token_validation_in_body(self):
        """Test validation with token in request body."""
        validation_data = {'token': self.token}
        
        response = self.client.post(self.validate_url, validation_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data['is_authenticated'], True)
        
    def test_invalid_token_validation(self):
        """Test validation of invalid token."""
        invalid_token = 'invalid.token.here'
        
        response = self.client.post(
            self.validate_url, 
            {}, 
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {invalid_token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response_data = response.json()
        self.assertEqual(response_data['error'], 'INVALID_TOKEN')
        
    def test_missing_token_validation(self):
        """Test validation without token."""
        response = self.client.post(self.validate_url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(response_data['error'], 'MISSING_TOKEN')


class UserLogoutAPITests(AuthenticationAPITestCase):
    """Test user logout API endpoint."""
    
    def setUp(self):
        """Set up test environment with authenticated user."""
        super().setUp()
        # Register user first
        self.client.post(self.register_url, self.test_user_data, format='json')
        # Then login to get token
        login_data = {
            'email': self.test_user_data['email'],
            'password': self.test_user_data['password']
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        self.token = login_response.json()['token']
        
    def test_successful_logout(self):
        """Test successful user logout."""
        response = self.client.post(
            self.logout_url, 
            {}, 
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn('message', response_data)
        self.assertEqual(response_data['is_authenticated'], False)
        
    def test_logout_with_token_in_body(self):
        """Test logout with token in request body."""
        logout_data = {'token': self.token}
        
        response = self.client.post(self.logout_url, logout_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data['is_authenticated'], False)
        
    def test_logout_with_invalid_token(self):
        """Test logout with invalid token."""
        invalid_token = 'invalid.token.here'
        
        response = self.client.post(
            self.logout_url, 
            {}, 
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {invalid_token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response_data = response.json()
        self.assertEqual(response_data['error'], 'INVALID_TOKEN')
        
    def test_logout_without_token(self):
        """Test logout without token."""
        response = self.client.post(self.logout_url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(response_data['error'], 'MISSING_TOKEN')
        
    def test_token_invalid_after_logout(self):
        """Test that token becomes invalid after logout."""
        # Logout first
        logout_response = self.client.post(
            self.logout_url, 
            {}, 
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        
        # Try to validate the token after logout
        validation_response = self.client.post(
            self.validate_url, 
            {}, 
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(validation_response.status_code, status.HTTP_401_UNAUTHORIZED)


class CurrentUserAPITests(AuthenticationAPITestCase):
    """Test current user context API endpoint."""
    
    def setUp(self):
        """Set up test environment with authenticated user."""
        super().setUp()
        # Register user first
        self.client.post(self.register_url, self.test_user_data, format='json')
        # Then login to get token
        login_data = {
            'email': self.test_user_data['email'],
            'password': self.test_user_data['password']
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        self.token = login_response.json()['token']
        
    def test_get_current_user_authenticated(self):
        """Test getting current user context when authenticated."""
        response = self.client.get(
            self.me_url,
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        
        # This endpoint should work with proper authentication
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn('user_id', response_data)
        self.assertEqual(response_data['email'], self.test_user_data['email'])
        
    def test_get_current_user_unauthenticated(self):
        """Test getting current user context when not authenticated."""
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(response_data['error'], 'MISSING_TOKEN')


class AuthenticationIntegrationTests(AuthenticationAPITestCase):
    """Integration tests for complete authentication flows."""
    
    def test_complete_registration_login_logout_flow(self):
        """Test complete flow: register -> login -> validate -> logout."""
        # 1. Register user (no token returned)
        register_response = self.client.post(self.register_url, self.test_user_data, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        register_data = register_response.json()
        self.assertNotIn('token', register_data)  # Registration doesn't return token
        
        # 2. Login with credentials to get token
        login_data = {
            'email': self.test_user_data['email'],
            'password': self.test_user_data['password']
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        login_token = login_response.json()['token']
        
        # 3. Validate login token
        validate_response = self.client.post(
            self.validate_url, 
            {}, 
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {login_token}'
        )
        self.assertEqual(validate_response.status_code, status.HTTP_200_OK)
        
        # 4. Logout
        logout_response = self.client.post(
            self.logout_url, 
            {}, 
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {login_token}'
        )
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        
        # 5. Verify token is invalid after logout
        validate2_response = self.client.post(
            self.validate_url, 
            {}, 
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {login_token}'
        )
        self.assertEqual(validate2_response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_multiple_concurrent_sessions(self):
        """Test that users can have multiple active sessions."""
        # Register user
        register_response = self.client.post(self.register_url, self.test_user_data, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        
        # Create multiple login sessions
        login_data = {
            'email': self.test_user_data['email'],
            'password': self.test_user_data['password']
        }
        
        # First session
        login1_response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(login1_response.status_code, status.HTTP_200_OK)
        token1 = login1_response.json()['token']
        
        # Second session
        login2_response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(login2_response.status_code, status.HTTP_200_OK)
        token2 = login2_response.json()['token']
        
        # Both tokens should be valid
        validate1_response = self.client.post(
            self.validate_url, 
            {}, 
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {token1}'
        )
        self.assertEqual(validate1_response.status_code, status.HTTP_200_OK)
        
        validate2_response = self.client.post(
            self.validate_url, 
            {}, 
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {token2}'
        )
        self.assertEqual(validate2_response.status_code, status.HTTP_200_OK)
        
        # Logout one session
        logout1_response = self.client.post(
            self.logout_url, 
            {}, 
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {token2}'
        )
        self.assertEqual(logout1_response.status_code, status.HTTP_200_OK)
        
        # First token should still be valid, second should be invalid
        validate3_response = self.client.post(
            self.validate_url, 
            {}, 
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {token1}'
        )
        self.assertEqual(validate3_response.status_code, status.HTTP_200_OK)
        
        validate4_response = self.client.post(
            self.validate_url, 
            {}, 
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {token2}'
        )
        self.assertEqual(validate4_response.status_code, status.HTTP_401_UNAUTHORIZED)


def run_all_authentication_api_tests():
    """Run all authentication API tests."""
    import unittest
    
    # Create test suite
    test_classes = [
        UserRegistrationAPITests,
        UserLoginAPITests,
        TokenValidationAPITests,
        UserLogoutAPITests,
        CurrentUserAPITests,
        AuthenticationIntegrationTests,
    ]
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("🚀 Running Authentication API Tests")
    print("=" * 80)
    
    success = run_all_authentication_api_tests()
    
    if success:
        print("\n🎉 ALL AUTHENTICATION API TESTS PASSED!")
        print("🔐 Authentication APIs are ready for production!")
    else:
        print("\n❌ SOME AUTHENTICATION API TESTS FAILED")
        print("🔧 Please fix the issues before deploying")
        exit(1)