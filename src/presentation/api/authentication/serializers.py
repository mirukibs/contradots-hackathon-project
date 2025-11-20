"""
Authentication API serializers for the Social Scoring System.

This module provides Django REST Framework serializers for authentication
endpoints, handling request validation and response serialization.
"""

import re
from rest_framework import serializers
from typing import Dict, Any


class UserRegistrationSerializer(serializers.Serializer):
    """Serializer for user registration requests."""
    
    name = serializers.CharField(
        max_length=200,
        min_length=2,
        help_text="Full name of the user (2-200 characters)"
    )
    
    email = serializers.EmailField(
        help_text="Valid email address"
    )
    
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        help_text="Password (8-128 characters)"
    )
    
    confirm_password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        required=False,  # Make optional for frontend compatibility
        help_text="Password confirmation (optional)"
    )
    
    role = serializers.ChoiceField(
        choices=['member', 'lead'],
        default='member',
        required=False,
        help_text="User role (member or lead, defaults to member)"
    )
    
    def validate_name(self, value: str) -> str:
        """Validate name format and constraints."""
        # Name should not be empty or just whitespace
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Name cannot be empty or just whitespace"
            )
        
        # Name should contain at least one letter
        if not any(c.isalpha() for c in value):
            raise serializers.ValidationError(
                "Name must contain at least one letter"
            )
        
        return value.strip()
    
    def validate_password(self, value: str) -> str:
        """Validate password strength."""
        # Simplified validation for hackathon - just check minimum requirements
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter"
            )
        
        # Check for at least one lowercase letter  
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter"
            )
        
        # Check for at least one digit
        if not re.search(r'\d', value):
            raise serializers.ValidationError(
                "Password must contain at least one digit"
            )
        
        return value
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that passwords match if confirm_password is provided."""
        if 'confirm_password' in data and data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match'
            })
        return data


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login requests."""
    
    email = serializers.EmailField(
        help_text="Registered email address"
    )
    
    password = serializers.CharField(
        max_length=128,
        write_only=True,
        help_text="User password"
    )


class AuthenticationResponseSerializer(serializers.Serializer):
    """Serializer for authentication success responses."""
    
    token = serializers.CharField(
        read_only=True,
        help_text="Authentication token"
    )
    
    user_id = serializers.CharField(
        read_only=True,
        help_text="User identifier"
    )
    
    email = serializers.EmailField(
        read_only=True,
        help_text="User email address"
    )
    
    roles = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        help_text="User roles"
    )
    
    is_authenticated = serializers.BooleanField(
        read_only=True,
        default=True,
        help_text="Authentication status"
    )
    
    expires_at = serializers.IntegerField(
        read_only=True,
        help_text="Token expiration timestamp"
    )


class TokenValidationSerializer(serializers.Serializer):
    """Serializer for token validation requests."""
    
    token = serializers.CharField(
        help_text="Authentication token to validate"
    )


class UserContextSerializer(serializers.Serializer):
    """Serializer for authenticated user context information."""
    
    user_id = serializers.CharField(
        read_only=True,
        help_text="User identifier"
    )
    
    email = serializers.EmailField(
        read_only=True,
        help_text="User email address"
    )
    
    roles = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        help_text="User roles"
    )
    
    is_authenticated = serializers.BooleanField(
        read_only=True,
        help_text="Authentication status"
    )


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout requests."""
    
    token = serializers.CharField(
        help_text="Authentication token to revoke",
        required=False  # Can also be passed in Authorization header
    )


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses."""
    
    error = serializers.CharField(
        read_only=True,
        help_text="Error type or code"
    )
    
    message = serializers.CharField(
        read_only=True,
        help_text="Human-readable error message"
    )
    
    details = serializers.DictField(
        read_only=True,
        required=False,
        help_text="Additional error details"
    )


class SuccessResponseSerializer(serializers.Serializer):
    """Serializer for simple success responses."""
    
    success = serializers.BooleanField(
        read_only=True,
        default=True,
        help_text="Operation success status"
    )
    
    message = serializers.CharField(
        read_only=True,
        help_text="Success message"
    )