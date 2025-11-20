"""
Django app configuration for the Social Scoring System infrastructure.

This module defines the Django app configuration for the infrastructure layer,
registering signal handlers and configuring the app for Django.
"""

from django.apps import AppConfig


class DjangoAppConfig(AppConfig):
    """Django application configuration for the infrastructure layer."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.infrastructure.django_app'
    verbose_name = 'Social Scoring System Infrastructure'
    
    def ready(self) -> None:
        """Called when Django starts up."""
        # Import signal handlers to ensure they are registered
        try:
            from . import signals  # type: ignore
        except ImportError:
            pass  # Signals module doesn't exist yet
        
        # Initialize the event system
        try:
            from ..events.event_publisher import initialize_event_system
            initialize_event_system()
        except ImportError as e:
            print(f"Warning: Could not initialize event system: {e}")
            pass  # Event system not yet complete