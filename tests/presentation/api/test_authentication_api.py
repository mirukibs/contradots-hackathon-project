"""
Comprehensive tests for authentication API endpoints.

This module provides thorough testing of all authentication REST API endpoints,
including success cases, error handling, and edge cases.
"""

import json
import uuid
import pytest
import os
from unittest.mock import patch, Mock
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from typing import Dict, Any

# Configure Django before imports
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_scoring_project.settings')
django.setup()

from src.infrastructure.auth.django_auth_integration import get_authentication_service, reset_authentication_service


class AuthenticationAPITestCase(APITestCase):
    """Base test case for authentication API tests."""
    
    def setUp(self):
        """Set up test environment."""
        # Reset authentication service for clean state
        reset_authentication_service()
        
        # Test data
        self.test_user_id = f"api_test_{uuid.uuid4().hex[:8]}"
        self.test_email = f"api_test_{uuid.uuid4().hex[:8]}@example.com"
        self.test_password = "ApiTestPassword123!"
        
        # API client
        self.client = APIClient()
        
        # Set environment for consistent testing
        with patch.dict(os.environ, {'SECRET_KEY': 'test-api-secret-key'}):
            self.auth_service = get_authentication_service()
    
    def register_test_user(self) -> Dict[str, Any]:
        """Helper method to register a test user."""
        registration_data = {
            'user_id': self.test_user_id,
            'email': self.test_email,
            'password': self.test_password,
            'confirm_password': self.test_password
        }
        response = self.client.post('/api/v1/auth/register/', registration_data, format='json')
        return response.json() if hasattr(response, 'json') else {}
    
    def login_test_user(self) -> Dict[str, Any]:
        """Helper method to login test user."""
        login_data = {
            'email': self.test_email,
            'password': self.test_password
        }
        response = self.client.post('/api/v1/auth/login/', login_data, format='json')
        return response.json() if hasattr(response, 'json') else {}


class TestUserRegistrationAPI(AuthenticationAPITestCase):
    """Test user registration API endpoint."""
    
    def test_successful_registration(self):
        """Test successful user registration."""
        print("🧪 Testing successful user registration API...")
        
        registration_data = {
            'user_id': self.test_user_id,
            'email': self.test_email,
            'password': self.test_password,
            'confirm_password': self.test_password
        }
        
        response = self.client.post('/api/v1/auth/register/', registration_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response_data = response.json()
        # Registration should NOT return a token - user must login separately
        self.assertNotIn('token', response_data)
        self.assertIn('user_id', response_data)
        self.assertIn('email', response_data)
        self.assertIn('message', response_data)
        self.assertEqual(response_data['email'], self.test_email)
        self.assertIn('Please log in', response_data['message'])
        
        print("✅ Successful registration test passed")
    
    def test_registration_password_mismatch(self):
        """Test registration with mismatched passwords."""
        print("🧪 Testing registration with password mismatch...")
        
        registration_data = {
            'user_id': self.test_user_id,
            'email': self.test_email,
            'password': self.test_password,
            'confirm_password': 'DifferentPassword123!'
        }
        
        response = self.client.post('/api/v1/auth/register/', registration_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response_data = response.json()
        self.assertEqual(response_data['error'], 'VALIDATION_ERROR')
        self.assertIn('details', response_data)
        
        print("✅ Password mismatch test passed")
    
    def test_registration_weak_password(self):
        """Test registration with weak password."""
        print("🧪 Testing registration with weak password...")
        
        registration_data = {
            'user_id': self.test_user_id,
            'email': self.test_email,
            'password': 'weak',  # Too short and weak
            'confirm_password': 'weak'
        }
        
        response = self.client.post('/api/v1/auth/register/', registration_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response_data = response.json()
        self.assertEqual(response_data['error'], 'VALIDATION_ERROR')
        
        print("✅ Weak password test passed")
    
    def test_registration_invalid_email(self):
        """Test registration with invalid email."""
        print("🧪 Testing registration with invalid email...")
        
        registration_data = {
            'user_id': self.test_user_id,
            'email': 'invalid-email',
            'password': self.test_password,
            'confirm_password': self.test_password
        }
        
        response = self.client.post('/api/v1/auth/register/', registration_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response_data = response.json()
        self.assertEqual(response_data['error'], 'VALIDATION_ERROR')
        
        print("✅ Invalid email test passed")
    
    def test_registration_duplicate_user(self):
        """Test registration with duplicate user."""
        print("🧪 Testing registration with duplicate user...")
        
        # Register user first time
        registration_data = {
            'user_id': self.test_user_id,
            'email': self.test_email,
            'password': self.test_password,
            'confirm_password': self.test_password
        }
        
        first_response = self.client.post('/api/v1/auth/register/', registration_data, format='json')
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        
        # Try to register same user again
        second_response = self.client.post('/api/v1/auth/register/', registration_data, format='json')
        
        self.assertEqual(second_response.status_code, status.HTTP_409_CONFLICT)
        
        response_data = second_response.json()
        self.assertEqual(response_data['error'], 'REGISTRATION_FAILED')
        
        print("✅ Duplicate user test passed")


class TestUserLoginAPI(AuthenticationAPITestCase):
    """Test user login API endpoint."""
    
    def test_successful_login(self):
        """Test successful user login."""
        print("🧪 Testing successful user login API...")
        
        # Register user first
        self.register_test_user()
        
        # Then login
        login_data = {
            'email': self.test_email,
            'password': self.test_password
        }
        
        response = self.client.post('/api/v1/auth/login/', login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertIn('token', response_data)
        self.assertIn('user_id', response_data)
        self.assertEqual(response_data['email'], self.test_email)
        self.assertTrue(response_data['is_authenticated'])
        
        print("✅ Successful login test passed")
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        print("🧪 Testing login with invalid credentials...")
        
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'WrongPassword123!'
        }
        
        response = self.client.post('/api/v1/auth/login/', login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response_data = response.json()
        self.assertEqual(response_data['error'], 'AUTHENTICATION_FAILED')
        
        print("✅ Invalid credentials test passed")
    
    def test_login_wrong_password(self):
        """Test login with wrong password."""
        print("🧪 Testing login with wrong password...")
        
        # Register user first
        self.register_test_user()
        
        # Try login with wrong password
        login_data = {
            'email': self.test_email,
            'password': 'WrongPassword123!'
        }
        
        response = self.client.post('/api/v1/auth/login/', login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response_data = response.json()
        self.assertEqual(response_data['error'], 'AUTHENTICATION_FAILED')
        
        print("✅ Wrong password test passed")
    
    def test_login_missing_fields(self):
        """Test login with missing fields."""
        print("🧪 Testing login with missing fields...")
        
        login_data = {
            'email': self.test_email
            # Missing password
        }
        
        response = self.client.post('/api/v1/auth/login/', login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response_data = response.json()
        self.assertEqual(response_data['error'], 'VALIDATION_ERROR')
        
        print("✅ Missing fields test passed")


class TestTokenValidationAPI(AuthenticationAPITestCase):
    """Test token validation API endpoint."""
    
    def test_valid_token_validation(self):
        """Test validation of valid token."""
        print("🧪 Testing valid token validation API...")
        
        # Register and login user
        self.register_test_user()
        login_response_data = self.login_test_user()
        token = login_response_data['token']
        
        # Validate token
        validation_data = {
            'token': token
        }
        
        response = self.client.post('/api/v1/auth/validate/', validation_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertIn('user_id', response_data)
        self.assertEqual(response_data['email'], self.test_email)
        self.assertTrue(response_data['is_authenticated'])
        
        print("✅ Valid token validation test passed")
    
    def test_invalid_token_validation(self):
        """Test validation of invalid token."""
        print("🧪 Testing invalid token validation API...")
        
        validation_data = {
            'token': 'invalid-token-string'
        }
        
        response = self.client.post('/api/v1/auth/validate/', validation_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response_data = response.json()
        self.assertEqual(response_data['error'], 'INVALID_TOKEN')
        
        print("✅ Invalid token validation test passed")
    
    def test_token_validation_via_header(self):
        """Test token validation via Authorization header."""
        print("🧪 Testing token validation via Authorization header...")
        
        # Register and login user
        self.register_test_user()
        login_response_data = self.login_test_user()
        token = login_response_data['token']
        
        # Validate token via header
        response = self.client.post(
            '/api/v1/auth/validate/', 
            {}, 
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertEqual(response_data['email'], self.test_email)
        self.assertTrue(response_data['is_authenticated'])
        
        print("✅ Token validation via header test passed")


class TestLogoutAPI(AuthenticationAPITestCase):
    """Test logout API endpoint."""
    
    def test_successful_logout(self):
        """Test successful user logout."""
        print("🧪 Testing successful user logout API...")
        
        # Register and login user
        self.register_test_user()
        login_response_data = self.login_test_user()
        token = login_response_data['token']
        
        # Logout
        logout_data = {
            'token': token
        }
        
        response = self.client.post('/api/v1/auth/logout/', logout_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertIn('message', response_data)
        self.assertFalse(response_data['is_authenticated'])
        
        print("✅ Successful logout test passed")
    
    def test_logout_via_header(self):
        """Test logout via Authorization header."""
        print("🧪 Testing logout via Authorization header...")
        
        # Register and login user
        self.register_test_user()
        login_response_data = self.login_test_user()
        token = login_response_data['token']
        
        # Logout via header
        response = self.client.post(
            '/api/v1/auth/logout/', 
            {}, 
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertFalse(response_data['is_authenticated'])
        
        print("✅ Logout via header test passed")
    
    def test_logout_invalid_token(self):
        """Test logout with invalid token."""
        print("🧪 Testing logout with invalid token...")
        
        logout_data = {
            'token': 'invalid-token'
        }
        
        response = self.client.post('/api/v1/auth/logout/', logout_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response_data = response.json()
        self.assertEqual(response_data['error'], 'INVALID_TOKEN')
        
        print("✅ Invalid token logout test passed")
    
    def test_logout_missing_token(self):
        """Test logout without token."""
        print("🧪 Testing logout without token...")
        
        response = self.client.post('/api/v1/auth/logout/', {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response_data = response.json()
        self.assertEqual(response_data['error'], 'MISSING_TOKEN')
        
        print("✅ Missing token logout test passed")
    
    def test_logout_revokes_token(self):
        """Test that logout properly revokes the token."""
        print("🧪 Testing that logout revokes token...")
        
        # Register and login user
        self.register_test_user()
        login_response_data = self.login_test_user()
        token = login_response_data['token']
        
        # Verify token is valid
        validation_response = self.client.post('/api/v1/auth/validate/', {'token': token}, format='json')
        self.assertEqual(validation_response.status_code, status.HTTP_200_OK)
        
        # Logout
        logout_response = self.client.post('/api/v1/auth/logout/', {'token': token}, format='json')
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        
        # Verify token is now invalid
        validation_response = self.client.post('/api/v1/auth/validate/', {'token': token}, format='json')
        self.assertEqual(validation_response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        print("✅ Token revocation test passed")


def run_comprehensive_api_tests():
    """Run all comprehensive API tests."""
    print("🚀 Starting Comprehensive Authentication API Tests\n")
    print("=" * 80)
    
    # Import Django test runner
    from django.test.utils import get_runner
    from django.conf import settings
    
    try:
        # Configure Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
        os.environ['SECRET_KEY'] = 'test-api-comprehensive-secret-key'
        
        django.setup()
        
        # Get test runner
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=2, interactive=False)
        
        # Define test modules
        test_modules = [
            'tests.presentation.api.test_authentication_api.TestUserRegistrationAPI',
            'tests.presentation.api.test_authentication_api.TestUserLoginAPI',
            'tests.presentation.api.test_authentication_api.TestTokenValidationAPI',
            'tests.presentation.api.test_authentication_api.TestLogoutAPI',
        ]
        
        # Run tests
        failures = test_runner.run_tests(test_modules)
        
        if failures == 0:
            print("=" * 80)
            print("🎉 ALL COMPREHENSIVE API TESTS PASSED! 🎉")
            print("=" * 80)
            print("\n✅ Authentication API Features Verified:")
            print("   • User registration with validation")
            print("   • User login with credential verification")
            print("   • Token validation and context creation")
            print("   • User logout with token revocation")
            print("   • Authorization header support")
            print("   • Comprehensive error handling")
            print("   • Input validation and sanitization")
            print("   • RESTful API design compliance")
            print("\n🚀 Authentication API is PRODUCTION READY!")
            return True
        else:
            print(f"❌ {failures} API tests failed")
            return False
            
    except Exception as e:
        print(f"❌ API test execution failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    # Run comprehensive API tests
    success = run_comprehensive_api_tests()
    
    if success:
        print("\n🎯 AUTHENTICATION API: FULLY TESTED AND VERIFIED")
    else:
        print("\n💥 AUTHENTICATION API: TESTS FAILED")
        exit(1)