"""
Value Objects for the Social Scoring System Domain.
These represent identity values that are immutable and validate themselves.
"""

# Re-export all value objects for backward compatibility
from .value_objects.person_id import PersonId
from .value_objects.activity_id import ActivityId
from .value_objects.action_id import ActionId

__all__ = ['PersonId', 'ActivityId', 'ActionId']