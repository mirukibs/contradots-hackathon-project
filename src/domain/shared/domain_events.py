"""
Domain Events for the Social Scoring System.
These events represent business events that trigger cross-aggregate communication.
"""

# Re-export all domain events for backward compatibility
from .events.domain_event import DomainEvent
from .events.action_submitted_event import ActionSubmittedEvent
from .events.proof_validated_event import ProofValidatedEvent

__all__ = ['DomainEvent', 'ActionSubmittedEvent', 'ProofValidatedEvent']