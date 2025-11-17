"""
Event publishing infrastructure for the Social Scoring System.

This module provides the infrastructure for publishing domain events
and connecting them to event handlers in an asynchronous, decoupled manner.
"""

from typing import List, Dict, Type, Callable, Any
from threading import Lock
import logging
from abc import ABC, abstractmethod

from ...domain.shared.events.domain_event import DomainEvent

logger = logging.getLogger(__name__)


class EventPublisher(ABC):
    """
    Abstract base class for event publishers.
    
    Defines the interface for publishing domain events to registered handlers.
    """
    
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event to all registered handlers.
        
        Args:
            event: The domain event to publish
        """
        pass
    
    @abstractmethod
    def register_handler(self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]) -> None:
        """
        Register an event handler for a specific event type.
        
        Args:
            event_type: The type of event to handle
            handler: The handler function that processes the event
        """
        pass


class InMemoryEventPublisher(EventPublisher):
    """
    In-memory implementation of EventPublisher.
    
    Stores event handlers in memory and publishes events synchronously.
    For production use, consider using a message queue or event store.
    """
    
    def __init__(self) -> None:
        """Initialize the event publisher with empty handler registry."""
        self._handlers: Dict[Type[DomainEvent], List[Callable[[DomainEvent], None]]] = {}
        self._lock = Lock()
    
    def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event to all registered handlers.
        
        Args:
            event: The domain event to publish
        """
        event_type = type(event)
        
        with self._lock:
            handlers = self._handlers.get(event_type, [])
        
        logger.info(f"Publishing event {event_type.__name__} to {len(handlers)} handlers")
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type.__name__}: {e}")
                # Continue processing other handlers even if one fails
    
    def register_handler(self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]) -> None:
        """
        Register an event handler for a specific event type.
        
        Args:
            event_type: The type of event to handle
            handler: The handler function that processes the event
        """
        with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)
        
        logger.info(f"Registered handler for {event_type.__name__}")
    
    def get_handler_count(self, event_type: Type[DomainEvent]) -> int:
        """
        Get the number of handlers registered for an event type.
        
        Args:
            event_type: The event type to check
            
        Returns:
            Number of registered handlers
        """
        with self._lock:
            return len(self._handlers.get(event_type, []))


class DjangoSignalEventBridge:
    """
    Bridge between Django signals and domain event publishing.
    
    This class connects Django model signals to domain event publication,
    allowing the domain layer to remain independent of Django.
    """
    
    def __init__(self, event_publisher: EventPublisher) -> None:
        """
        Initialize the bridge with an event publisher.
        
        Args:
            event_publisher: The event publisher to use for domain events
        """
        self._event_publisher = event_publisher
    
    def publish_domain_event(self, event: DomainEvent) -> None:
        """
        Publish a domain event through the event publisher.
        
        Args:
            event: The domain event to publish
        """
        self._event_publisher.publish(event)
    
    def connect_model_signals(self) -> None:
        """
        Connect Django model signals to domain event publication.
        
        This method should be called during Django app initialization
        to set up the signal handlers.
        """
        from django.db.models.signals import post_save, post_delete
        from ..django_app.models import PersonProfile, Activity, Action
        from ...domain.shared.events.action_submitted_event import ActionSubmittedEvent
        from ...domain.shared.events.proof_validated_event import ProofValidatedEvent
        from ...domain.shared.value_objects.person_id import PersonId
        from ...domain.activity.activity import ActivityId
        from ...domain.shared.value_objects.action_id import ActionId
        import uuid
        from datetime import datetime
        
        # Connect Action signals
        def handle_action_submitted(sender, instance, created, **kwargs):
            if created:
                event = ActionSubmittedEvent(
                    action_id=ActionId(instance.action_id),
                    person_id=PersonId(instance.person.person_id),
                    activity_id=ActivityId(instance.activity.activity_id),
                    description=instance.description,
                    proof_hash=instance.proof_hash or ""
                )
                self.publish_domain_event(event)
        
        def handle_action_validated(sender, instance, created, **kwargs):
            if not created and instance.status == Action.VALIDATED:
                event = ProofValidatedEvent(
                    action_id=ActionId(instance.action_id),
                    person_id=PersonId(instance.person.person_id),
                    activity_id=ActivityId(instance.activity.activity_id),
                    is_valid=True
                )
                self.publish_domain_event(event)
        
        post_save.connect(handle_action_submitted, sender=Action)
        post_save.connect(handle_action_validated, sender=Action)
        
        logger.info("Django signal event bridge connected")


# Global event publisher instance
_event_publisher: EventPublisher = InMemoryEventPublisher()
_signal_bridge: DjangoSignalEventBridge = DjangoSignalEventBridge(_event_publisher)


def get_event_publisher() -> EventPublisher:
    """
    Get the global event publisher instance.
    
    Returns:
        The configured event publisher
    """
    return _event_publisher


def get_signal_bridge() -> DjangoSignalEventBridge:
    """
    Get the global Django signal bridge instance.
    
    Returns:
        The configured signal bridge
    """
    return _signal_bridge


def initialize_event_system() -> None:
    """
    Initialize the event system by connecting all handlers and signals.
    
    This function should be called during Django app initialization.
    """
    from ...application.handlers.reputation_event_handler import ReputationEventHandler
    from ...domain.shared.events.action_submitted_event import ActionSubmittedEvent
    from ...domain.shared.events.proof_validated_event import ProofValidatedEvent
    from ...infrastructure.persistence.django_repositories import DjangoPersonRepository
    from ...infrastructure.persistence.django_repositories import DjangoActivityRepository
    from ...domain.services.reputation_service import ReputationService
    
    # Create repositories and services
    person_repo = DjangoPersonRepository()
    activity_repo = DjangoActivityRepository()
    reputation_service = ReputationService()
    
    # Register event handlers
    reputation_handler = ReputationEventHandler(
        person_repo=person_repo,
        activity_repo=activity_repo,
        reputation_service=reputation_service
    )
    
    publisher = get_event_publisher()
    
    # Register handlers for domain events
    publisher.register_handler(ActionSubmittedEvent, reputation_handler.handle)
    publisher.register_handler(ProofValidatedEvent, reputation_handler.handle)
    
    # Connect Django signals to domain events
    get_signal_bridge().connect_model_signals()
    
    logger.info("Event system initialized successfully")