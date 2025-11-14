"""
Authentication middleware for HTTP requests.

Handles JWT token validation and creates authentication context.
"""

from typing import Optional, Any, Dict
from functools import wraps
from flask import request, jsonify, g
import jwt
from datetime import datetime, timezone

from src.application.security.authentication_context import AuthenticationContext, create_anonymous_context
from src.domain.person.role import Role
from src.domain.shared.value_objects.person_id import PersonId


class AuthenticationMiddleware:
    """Middleware for handling HTTP authentication."""
    
    def __init__(self, jwt_secret: str = "your-secret-key"):
        self.jwt_secret = jwt_secret
    
    def extract_auth_context(self, request_headers: Dict[str, str]) -> AuthenticationContext:
        """
        Extract authentication context from HTTP request headers.
        
        Args:
            request_headers: HTTP request headers
            
        Returns:
            AuthenticationContext for the request
        """
        auth_header = request_headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return create_anonymous_context()
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # Extract user information from JWT payload
            person_id = PersonId(payload['person_id'])
            email = payload['email']
            roles = [Role(role) for role in payload.get('roles', [])]
            
            return AuthenticationContext(
                current_user_id=person_id,
                email=email,
                roles=roles,
                is_authenticated=True
            )
            
        except jwt.InvalidTokenError:
            return create_anonymous_context()
        except Exception:
            return create_anonymous_context()
    
    def create_jwt_token(self, person_id: PersonId, email: str, roles: list[Role]) -> str:
        """
        Create JWT token for authenticated user.
        
        Args:
            person_id: User's person ID
            email: User's email
            roles: User's roles
            
        Returns:
            JWT token string
        """
        payload = {
            'person_id': str(person_id),
            'email': email,
            'roles': [role.value for role in roles],
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc).timestamp() + 3600  # 1 hour expiry
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')


# Flask decorators for authentication
def require_authentication(f):
    """Decorator that requires authentication for the route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_middleware = AuthenticationMiddleware()
        auth_context = auth_middleware.extract_auth_context(dict(request.headers))
        
        if not auth_context.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Store auth context in Flask's g object for use in the route
        g.auth_context = auth_context
        return f(*args, **kwargs)
    return decorated_function


def require_role(*required_roles):
    """Decorator that requires specific roles for the route."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_middleware = AuthenticationMiddleware()
            auth_context = auth_middleware.extract_auth_context(dict(request.headers))
            
            if not auth_context.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Check if user has any of the required roles
            user_has_required_role = any(
                auth_context.has_role(role) for role in required_roles
            )
            
            if not user_has_required_role:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            g.auth_context = auth_context
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def optional_authentication(f):
    """Decorator that allows optional authentication for the route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_middleware = AuthenticationMiddleware()
        auth_context = auth_middleware.extract_auth_context(dict(request.headers))
        
        # Always store auth context (may be anonymous)
        g.auth_context = auth_context
        return f(*args, **kwargs)
    return decorated_function