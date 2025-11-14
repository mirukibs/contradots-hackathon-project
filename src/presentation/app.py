"""
Main Flask application for the Social Scoring System.

This module sets up the Flask app, registers blueprints, 
and configures dependency injection.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from typing import Any, Dict

# Presentation layer imports
from src.presentation.controllers.person_controller import create_person_controller
from src.presentation.controllers.activity_controller import create_activity_controller
from src.presentation.controllers.action_controller import create_action_controller
from src.presentation.middleware.authentication import AuthenticationMiddleware

# Application layer imports  
from src.application.services.person_application_service import PersonApplicationService
from src.application.services.activity_application_service import ActivityApplicationService
from src.application.services.action_application_service import ActionApplicationService
from src.application.security.authorization_service import AuthorizationService

# Infrastructure imports (these will be created later)
# For now, we'll use mock implementations
from src.infrastructure.repositories.memory_person_repository import MemoryPersonRepository
from src.infrastructure.repositories.memory_activity_repository import MemoryActivityRepository
from src.infrastructure.repositories.memory_action_repository import MemoryActionRepository
from src.infrastructure.query_repositories.memory_leaderboard_query_repository import MemoryLeaderboardQueryRepository
from src.infrastructure.query_repositories.memory_activity_query_repository import MemoryActivityQueryRepository
from src.infrastructure.query_repositories.memory_action_query_repository import MemoryActionQueryRepository
from src.infrastructure.events.memory_event_publisher import MemoryEventPublisher


def create_app(config: Dict[str, Any] = None) -> Flask:
    """
    Application factory function.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Default configuration
    app.config.update({
        'SECRET_KEY': 'dev-secret-key',
        'JWT_SECRET': 'jwt-secret-key',
        'DEBUG': True
    })
    
    # Override with provided config
    if config:
        app.config.update(config)
    
    # Enable CORS for all routes
    CORS(app)
    
    # Set up dependency injection
    _setup_dependencies(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({'status': 'healthy', 'service': 'social-scoring-system'})
    
    # API info endpoint
    @app.route('/api/v1/info')
    def api_info():
        """API information endpoint."""
        return jsonify({
            'name': 'Social Scoring System API',
            'version': 'v1.0.0',
            'description': 'API for the blockchain-based social scoring system',
            'endpoints': {
                'person': '/api/v1/person/',
                'activity': '/api/v1/activity/',
                'action': '/api/v1/action/'
            }
        })
    
    return app


def _setup_dependencies(app: Flask) -> None:
    """Set up dependency injection container."""
    
    # Repository implementations (in-memory for now)
    person_repo = MemoryPersonRepository()
    activity_repo = MemoryActivityRepository()
    action_repo = MemoryActionRepository()
    
    # Query repository implementations
    leaderboard_query_repo = MemoryLeaderboardQueryRepository()
    activity_query_repo = MemoryActivityQueryRepository()
    action_query_repo = MemoryActionQueryRepository()
    
    # Event infrastructure
    event_publisher = MemoryEventPublisher()
    
    # Security services
    authorization_service = AuthorizationService(person_repo)
    
    # Application services
    person_service = PersonApplicationService(
        person_repo=person_repo,
        leaderboard_query_repo=leaderboard_query_repo,
        authorization_service=authorization_service
    )
    
    activity_service = ActivityApplicationService(
        activity_repo=activity_repo,
        activity_query_repo=activity_query_repo,
        person_repo=person_repo,
        authorization_service=authorization_service
    )
    
    action_service = ActionApplicationService(
        action_repo=action_repo,
        action_query_repo=action_query_repo,
        activity_repo=activity_repo,
        event_publisher=event_publisher,
        authorization_service=authorization_service
    )
    
    # Store services in app context
    app.person_service = person_service
    app.activity_service = activity_service
    app.action_service = action_service


def _register_blueprints(app: Flask) -> None:
    """Register all API blueprints."""
    
    # Register person routes
    person_blueprint = create_person_controller(app.person_service)
    app.register_blueprint(person_blueprint)
    
    # Register activity routes
    activity_blueprint = create_activity_controller(app.activity_service)
    app.register_blueprint(activity_blueprint)
    
    # Register action routes
    action_blueprint = create_action_controller(app.action_service)
    app.register_blueprint(action_blueprint)


def _register_error_handlers(app: Flask) -> None:
    """Register global error handlers."""
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({
            'error': {
                'message': 'Endpoint not found',
                'code': 'NOT_FOUND'
            }
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors."""
        return jsonify({
            'error': {
                'message': 'Method not allowed',
                'code': 'METHOD_NOT_ALLOWED'
            }
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify({
            'error': {
                'message': 'Internal server error',
                'code': 'INTERNAL_ERROR'
            }
        }), 500


if __name__ == '__main__':
    """Run the application in development mode."""
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)