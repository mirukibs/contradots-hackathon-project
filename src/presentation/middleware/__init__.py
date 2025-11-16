"""
Authentication middleware for Django REST Framework integration.

This middleware integrates the infrastructure authentication system
with Django REST Framework for seamless authentication handling.
"""

from django.utils.deprecation import MiddlewareMixin
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from typing import Optional, Tuple, Any
import logging

from ...infrastructure.auth.authentication_bridge import get_authentication_bridge

logger = logging.getLogger(__name__)


class AuthenticationContextMiddleware(MiddlewareMixin):
    """
    Middleware that adds authentication context to requests.
    
    This middleware extracts authentication tokens from requests
    and adds the corresponding AuthenticationContext to the request
    object for use in views and other middleware.
    """
    
    def process_request(self, request):
        """Process incoming request to add authentication context."""
        try:
            # For now, just add basic attributes without complex logic
            request.auth_context = None
            if not hasattr(request, 'user'):
                request.user = SimpleAnonymousUser()
            return None
        except Exception as e:
            logger.error(f"Error in AuthenticationContextMiddleware: {e}")
            request.auth_context = None
            request.user = SimpleAnonymousUser()
            return None


class SimpleAnonymousUser:
    """Simple anonymous user for Django compatibility."""
    
    @property
    def is_authenticated(self):
        return False
    
    @property  
    def is_anonymous(self):
        return True
    
    @property
    def is_active(self):
        return False
    
    def __str__(self):
        return "AnonymousUser"


class AuthenticatedUser:
    """
    Minimal user object for Django compatibility.
    
    This class provides a minimal user interface that Django
    expects while delegating to our AuthenticationContext.
    """
    
    def __init__(self, auth_context):
        """Initialize with authentication context."""
        self._auth_context = auth_context
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self._auth_context.is_authenticated if self._auth_context else False
    
    @property
    def is_anonymous(self) -> bool:
        """Check if user is anonymous."""
        return not self.is_authenticated
    
    @property
    def email(self) -> str:
        """Get user email."""
        return self._auth_context.email
    
    @property
    def id(self) -> str:
        """Get user ID."""
        return str(self._auth_context.current_user_id)
    
    @property
    def pk(self) -> str:
        """Get primary key (same as ID)."""
        return self.id
    
    def __str__(self) -> str:
        """String representation."""
        return f"AuthenticatedUser({self.email})"


class AnonymousUser:
    """Anonymous user for unauthenticated requests."""
    
    @property
    def is_authenticated(self) -> bool:
        """Anonymous users are not authenticated."""
        return False
    
    @property
    def is_anonymous(self) -> bool:
        """Anonymous users are anonymous."""
        return True
    
    @property
    def email(self) -> str:
        """Anonymous users have no email."""
        return ""
    
    @property
    def id(self) -> Optional[str]:
        """Anonymous users have no ID."""
        return None
    
    @property
    def pk(self) -> Optional[str]:
        """Anonymous users have no primary key."""
        return None
    
    def __str__(self) -> str:
        """String representation."""
        return "AnonymousUser"


class TokenAuthentication(BaseAuthentication):
    """
    DRF Authentication class for token-based authentication.
    
    This class integrates with Django REST Framework's authentication
    system to provide token-based authentication using our infrastructure.
    """
    
    keyword = 'Bearer'
    model = None
    
    def authenticate(self, request: Request) -> Optional[Tuple[Any, str]]:
        """
        Authenticate the request and return user and token.
        
        Returns:
            Tuple of (user, token) if authenticated, None otherwise
        """
        auth_header = self.get_authorization_header(request)
        if not auth_header or not auth_header.startswith(b'Bearer '):
            return None
        
        try:
            token = auth_header.decode('utf-8')[7:]  # Remove 'Bearer ' prefix
        except UnicodeDecodeError:
            raise AuthenticationFailed('Invalid token header. Token should be UTF-8.')
        
        return self.authenticate_credentials(token)
    
    def authenticate_credentials(self, token: str) -> Tuple[AuthenticatedUser, str]:
        """
        Authenticate the token and return user.
        
        Args:
            token: Authentication token
            
        Returns:
            Tuple of (user, token)
            
        Raises:
            AuthenticationFailed: If authentication fails
        """
        try:
            auth_bridge = get_authentication_bridge()
            auth_context = auth_bridge.create_context_from_token(token)
            
            if not auth_context or not auth_context.is_authenticated:
                raise AuthenticationFailed('Invalid or expired token')
            
            # Create user object for DRF
            user = AuthenticatedUser(auth_context)
            
            return user, token
            
        except Exception as e:
            raise AuthenticationFailed(f'Authentication failed: {str(e)}')
    
    def get_authorization_header(self, request: Request) -> bytes:
        """
        Get authorization header from request.
        
        Args:
            request: DRF request object
            
        Returns:
            Authorization header as bytes
        """
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if isinstance(auth, str):
            auth = auth.encode('iso-8859-1')
        return auth
    
    def authenticate_header(self, request: Request) -> str:
        """
        Return a string to be used as the value of the WWW-Authenticate
        header in a 401 Unauthenticated response.
        """
        return self.keyword