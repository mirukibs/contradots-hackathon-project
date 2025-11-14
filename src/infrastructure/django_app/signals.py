"""
Django signals for the Social Scoring System infrastructure.

This module provides signal handlers for Django model events that trigger
domain events and maintain consistency between infrastructure and domain layers.
"""

from typing import Any
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PersonProfile, Activity, Action


@receiver(post_save, sender=PersonProfile)
def handle_person_profile_save(sender: Any, instance: PersonProfile, created: bool, **kwargs: Any) -> None:
    """Handle PersonProfile save signal to trigger domain events."""
    if created:
        # Trigger domain event for person registration
        # This would integrate with domain event dispatching
        pass


@receiver(post_save, sender=Activity)
def handle_activity_save(sender: Any, instance: Activity, created: bool, **kwargs: Any) -> None:
    """Handle Activity save signal to trigger domain events."""
    if created:
        # Trigger domain event for activity creation
        # This would integrate with domain event dispatching
        pass


@receiver(post_save, sender=Action)
def handle_action_save(sender: Any, instance: Action, created: bool, **kwargs: Any) -> None:
    """Handle Action save signal to trigger domain events."""
    if created:
        # Trigger domain event for action submission
        pass
    elif instance.status == 'VALIDATED':
        # Trigger domain event for action validation
        # Update person reputation score
        try:
            profile = instance.person
            profile.reputation_score += instance.activity.points
            profile.save()
        except PersonProfile.DoesNotExist:
            pass  # Handle gracefully


@receiver(post_delete, sender=PersonProfile)
def handle_person_profile_delete(sender: Any, instance: PersonProfile, **kwargs: Any) -> None:
    """Handle PersonProfile deletion signal."""
    # Clean up any related domain data
    pass


# Django User signals to maintain PersonProfile consistency
@receiver(post_save, sender=User)
def handle_user_save(sender: Any, instance: User, created: bool, **kwargs: Any) -> None:
    """Ensure PersonProfile exists for each User."""
    if created and not hasattr(instance, 'personprofile'):
        # Create a default PersonProfile if one doesn't exist
        # This handles cases where User is created outside our registration flow
        PersonProfile.objects.create(
            user=instance,
            role='MEMBER',  # Default role
            full_name=instance.first_name or instance.username,
            reputation_score=0,
            is_active=True
        )