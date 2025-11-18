"""
Activity and Action API serializers for the Social Scoring System.

This module provides Django REST Framework serializers for activity and action
endpoints, handling request validation and response serialization.
"""

import re
from rest_framework import serializers
from typing import Dict, Any


# ==================== Activity Serializers ====================

class CreateActivitySerializer(serializers.Serializer):
    """Serializer for activity creation requests."""
    
    name = serializers.CharField(
        max_length=200,
        min_length=3,
        help_text="Name of the activity (3-200 characters)"
    )
    
    description = serializers.CharField(
        max_length=1000,
        min_length=10,
        help_text="Description of the activity (10-1000 characters)"
    )
    
    points = serializers.IntegerField(
        min_value=1,
        max_value=1000,
        help_text="Points awarded for completing the activity (1-1000)"
    )
    
    def validate_name(self, value: str) -> str:
        """Validate activity name format and constraints."""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Activity name cannot be empty or just whitespace"
            )
        
        # Name should contain at least one letter
        if not any(c.isalpha() for c in value):
            raise serializers.ValidationError(
                "Activity name must contain at least one letter"
            )
        
        return value.strip()
    
    def validate_description(self, value: str) -> str:
        """Validate activity description."""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Activity description cannot be empty or just whitespace"
            )
        
        return value.strip()


class ActivityResponseSerializer(serializers.Serializer):
    """Serializer for activity response data."""
    
    activityId = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    points = serializers.IntegerField(read_only=True)
    leadName = serializers.CharField(read_only=True)
    isActive = serializers.BooleanField(read_only=True)


class ActivityDetailsResponseSerializer(serializers.Serializer):
    """Serializer for detailed activity response data."""
    
    activityId = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    points = serializers.IntegerField(read_only=True)
    leadName = serializers.CharField(read_only=True)
    isActive = serializers.BooleanField(read_only=True)
    totalActions = serializers.IntegerField(read_only=True)
    validatedActions = serializers.IntegerField(read_only=True)


class DeactivateActivitySerializer(serializers.Serializer):
    """Serializer for activity deactivation requests."""
    
    activityId = serializers.CharField(
        help_text="ID of the activity to deactivate"
    )
    
    def validate_activityId(self, value: str) -> str:
        """Validate activity ID format (UUID)."""
        import uuid
        try:
            uuid.UUID(value)
        except ValueError:
            raise serializers.ValidationError(
                "Activity ID must be a valid UUID"
            )
        return value


# ==================== Action Serializers ====================

class SubmitActionSerializer(serializers.Serializer):
    """Serializer for action submission requests."""
    
    activityId = serializers.CharField(
        help_text="ID of the activity this action is for"
    )
    
    description = serializers.CharField(
        max_length=500,
        min_length=10,
        help_text="Description of the action taken (10-500 characters)"
    )
    
    proofHash = serializers.CharField(
        max_length=66,
        min_length=66,
        help_text="Hash of the proof document/image (must be 0x + 64 hex chars, 66 characters)"
    )
    
    def validate_activityId(self, value: str) -> str:
        """Validate activity ID format (UUID)."""
        import uuid
        try:
            uuid.UUID(value)
        except ValueError:
            raise serializers.ValidationError(
                "Activity ID must be a valid UUID"
            )
        return value
    
    def validate_description(self, value: str) -> str:
        """Validate action description."""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Action description cannot be empty or just whitespace"
            )
        
        return value.strip()
    
    def validate_proofHash(self, value: str) -> str:
        """Validate proof hash format."""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Proof hash cannot be empty or just whitespace"
            )
        value = value.strip()
        if len(value) != 66:
            raise serializers.ValidationError(
                f"Proof hash must be exactly 66 characters (0x + 64 hex chars), got {len(value)} chars"
            )
        if not value.startswith('0x'):
            raise serializers.ValidationError(
                "Proof hash must start with '0x'"
            )
        if not re.match(r'^0x[a-fA-F0-9]{64}$', value):
            raise serializers.ValidationError(
                "Proof hash must be a 0x-prefixed 64-character hexadecimal string"
            )
        return value


class ActionResponseSerializer(serializers.Serializer):
    """Serializer for action response data."""
    
    actionId = serializers.CharField(read_only=True)
    personName = serializers.CharField(read_only=True)
    activityName = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    submittedAt = serializers.CharField(read_only=True)


class ValidateProofSerializer(serializers.Serializer):
    """Serializer for proof validation requests."""
    
    actionId = serializers.CharField(
        help_text="ID of the action to validate"
    )
    
    isValid = serializers.BooleanField(
        help_text="Whether the proof is valid (true) or invalid (false)"
    )
    
    validatorComment = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Optional comment from the validator"
    )
    
    def validate_actionId(self, value: str) -> str:
        """Validate action ID format (UUID)."""
        import uuid
        try:
            uuid.UUID(value)
        except ValueError:
            raise serializers.ValidationError(
                "Action ID must be a valid UUID"
            )
        return value
    
    def validate_validatorComment(self, value: str) -> str:
        """Validate validator comment."""
        if value:
            return value.strip()
        return ""


# ==================== Leaderboard & Profile Serializers ====================

class LeaderboardEntrySerializer(serializers.Serializer):
    """Serializer for leaderboard entry data."""
    
    personId = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    reputationScore = serializers.IntegerField(read_only=True)
    rank = serializers.IntegerField(read_only=True)


class PersonProfileSerializer(serializers.Serializer):
    """Serializer for person profile data."""
    
    personId = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    reputationScore = serializers.IntegerField(read_only=True)


# ==================== Response Wrapper Serializers ====================

# Note: Standard API responses are handled directly in views for better flexibility

class ActivityListResponseSerializer(serializers.Serializer):
    """Response serializer for activity list endpoints."""
    
    activities = ActivityResponseSerializer(many=True, read_only=True)
    total = serializers.IntegerField(read_only=True)


class ActionListResponseSerializer(serializers.Serializer):
    """Response serializer for action list endpoints."""
    
    actions = ActionResponseSerializer(many=True, read_only=True)
    total = serializers.IntegerField(read_only=True)


class LeaderboardResponseSerializer(serializers.Serializer):
    """Response serializer for leaderboard endpoints."""
    
    leaderboard = LeaderboardEntrySerializer(many=True, read_only=True)
    total = serializers.IntegerField(read_only=True)
    currentUserRank = serializers.IntegerField(read_only=True, required=False)
