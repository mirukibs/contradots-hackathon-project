"""
Infrastructure layer for the Social Scoring System.

This layer contains concrete implementations of interfaces defined in
the application and domain layers, including:

- Database repositories (Django ORM)
- Authentication infrastructure (Django REST Knox)
- External service adapters
- Event publishing mechanisms
- Configuration and dependency injection

The infrastructure layer depends on domain and application layers
but never the other way around, following clean architecture principles.
"""