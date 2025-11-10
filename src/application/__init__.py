"""
Application Layer - CQRS Architecture

This package contains the Application Layer implementation following the CQRS pattern.
It orchestrates domain logic without containing business rules itself.

Components:
- services: Application Services that coordinate use cases
- commands: Command objects for write operations
- dtos: Data Transfer Objects for read operations  
- repositories: Query-side repository interfaces
- events: Event infrastructure (EventStore, EventPublisher, EventHandler)
- handlers: Event handlers that bridge domain and application layers
"""

# Import main application services for easy access
from .services import (
    PersonApplicationService,
    ActivityApplicationService, 
    ActionApplicationService
)

# Import command objects
from .commands import (
    RegisterPersonCommand,
    CreateActivityCommand,
    SubmitActionCommand,
    DeactivateActivityCommand,
    ValidateProofCommand
)

# Import DTO objects  
from .dtos import (
    PersonProfileDto,
    LeaderboardDto,
    ActivityDto,
    ActivityDetailsDto,
    ActionDto
)

# Import event infrastructure
from .events import (
    EventStore,
    EventPublisher,
    EventHandler
)

# Import event handlers
from .handlers import (
    ReputationEventHandler,
    LeaderboardProjectionHandler,
    ActivityProjectionHandler
)

__all__ = [
    # Application Services
    'PersonApplicationService',
    'ActivityApplicationService', 
    'ActionApplicationService',
    # Commands
    'RegisterPersonCommand',
    'CreateActivityCommand',
    'SubmitActionCommand', 
    'DeactivateActivityCommand',
    'ValidateProofCommand',
    # DTOs
    'PersonProfileDto',
    'LeaderboardDto',
    'ActivityDto',
    'ActivityDetailsDto', 
    'ActionDto',
    # Event Infrastructure
    'EventStore',
    'EventPublisher',
    'EventHandler',
    # Event Handlers
    'ReputationEventHandler',
    'LeaderboardProjectionHandler',
    'ActivityProjectionHandler'
]