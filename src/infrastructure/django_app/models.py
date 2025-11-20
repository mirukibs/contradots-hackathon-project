"""
Django models for the Social Scoring System infrastructure.

This module defines Django ORM models that serve as the persistence layer
for domain objects while maintaining clean architecture principles.
"""

import uuid
from typing import Any
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class PersonProfile(models.Model):
    """
    Django model linking Django User to Person domain object.
    
    This model provides the bridge between Django's authentication system
    and our domain model, storing additional Person-specific data.
    """
    
    # Link to Django User
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='person_profile'
    )
    
    # Person domain object ID
    person_id = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier from Person domain object"
    )
    
    # Role enum values
    MEMBER = 'MEMBER'
    LEAD = 'LEAD'
    ROLE_CHOICES = [
        (MEMBER, 'Member'),
        (LEAD, 'Lead'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=MEMBER,
        help_text="User's role in the system"
    )
    
    # Person attributes
    full_name = models.CharField(
        max_length=100,
        help_text="Person's full name"
    )
    
    reputation_score = models.IntegerField(
        default=0,
        help_text="Current reputation score"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'person_profiles'
        indexes = [
            models.Index(fields=['person_id']),
            models.Index(fields=['role']),
            models.Index(fields=['reputation_score']),
        ]
    
    def clean(self):
        """Validate model data."""
        super().clean()
        
        if self.reputation_score < 0:
            raise ValidationError("Reputation score cannot be negative")
        
        if not self.full_name or not self.full_name.strip():
            raise ValidationError("Full name is required")
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Override save to ensure validation."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.full_name} ({self.user.email}) - {self.role}"
    
    def __repr__(self) -> str:
        return f"PersonProfile(person_id={self.person_id!r}, email='{self.user.email}', role='{self.role}')"


class Activity(models.Model):
    """
    Django model for Activity domain objects.
    
    Stores activity data in the database while maintaining
    separation from domain logic.
    """
    
    activity_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    name = models.CharField(
        max_length=200,
        help_text="Activity name"
    )
    
    description = models.TextField(
        help_text="Detailed activity description"
    )
    
    points = models.PositiveIntegerField(
        help_text="Points awarded for completing this activity"
    )
    
    # Link to the lead person
    lead_person = models.ForeignKey(
        PersonProfile,
        on_delete=models.CASCADE,
        related_name='created_activities',
        help_text="Person who created this activity"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the activity is currently active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'activities'
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['lead_person']),
        ]
    
    def clean(self):
        """Validate model data."""
        super().clean()
        
        if not self.name or not self.name.strip():
            raise ValidationError("Activity name is required")
        
        if not self.description or not self.description.strip():
            raise ValidationError("Activity description is required")
        
        if self.points <= 0:
            raise ValidationError("Points must be greater than zero")
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Override save to ensure validation."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.name} ({self.points} points)"
    
    def __repr__(self) -> str:
        return f"Activity(activity_id={self.activity_id!r}, name='{self.name}', points={self.points})"


class Action(models.Model):
    """
    Django model for Action domain objects.
    
    Stores action submissions and their validation status.
    """
    
    # Action status choices
    SUBMITTED = 'SUBMITTED'
    VALIDATED = 'VALIDATED'
    REJECTED = 'REJECTED'
    STATUS_CHOICES = [
        (SUBMITTED, 'Submitted'),
        (VALIDATED, 'Validated'),
        (REJECTED, 'Rejected'),
    ]
    
    action_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Links to person and activity
    person = models.ForeignKey(
        PersonProfile,
        on_delete=models.CASCADE,
        related_name='actions',
        help_text="Person who submitted this action"
    )
    
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='actions',
        help_text="Activity this action relates to"
    )
    
    description = models.TextField(
        help_text="Description of the action performed"
    )
    
    proof_hash = models.CharField(
        max_length=66,  # 0x + 64 hex characters
        help_text="Blockchain proof hash"
    )
    
    blockchain_action_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Action ID from the blockchain contract"
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=SUBMITTED,
        help_text="Current status of the action"
    )
    
    # Validation details
    validated_by = models.ForeignKey(
        PersonProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_actions',
        help_text="Person who validated this action"
    )
    
    validation_notes = models.TextField(
        blank=True,
        help_text="Notes from validation process"
    )
    
    points_awarded = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Points awarded if validated"
    )
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'actions'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['person']),
            models.Index(fields=['activity']),
            models.Index(fields=['submitted_at']),
            models.Index(fields=['blockchain_action_id']),
        ]
    
    def clean(self):
        """Validate model data."""
        super().clean()
        
        if not self.description or not self.description.strip():
            raise ValidationError("Action description is required")
        
        if not self.proof_hash or not self.proof_hash.strip():
            raise ValidationError("Proof hash is required")
        
        # Validate proof hash format (should start with 0x and be 66 chars)
        if not self.proof_hash.startswith('0x') or len(self.proof_hash) != 66:
            raise ValidationError("Proof hash must be a valid blockchain hash (0x + 64 hex chars)")
        
        # Validate that points_awarded is set for validated actions
        if self.status == self.VALIDATED and self.points_awarded is None:
            raise ValidationError("Points awarded must be set for validated actions")
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Override save to ensure validation."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"Action by {self.person.full_name} for {self.activity.name} - {self.status}"
    
    def __repr__(self) -> str:
        return f"Action(action_id={self.action_id!r}, person='{self.person.user.email}', activity='{self.activity.name}', status='{self.status}')"