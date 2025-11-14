"""
Authentication Infrastructure for Social Scoring System.

This module provides clean authentication infrastructure using token-based
authentication while maintaining separation from presentation concerns.
"""

from typing import Optional, Any
from abc import ABC, abstractmethod


class AuthenticationInfrastructure(ABC):
    """
    Abstract authentication infrastructure interface.
    
    Defines the contract for authentication infrastructure implementations
    while keeping them separate from presentation layer concerns.
    """
    
    @abstractmethod
    def create_authentication_token(self, user_id: str, email: str) -> str:
        """Create authentication token for user."""
        pass
    
    @abstractmethod
    def validate_token(self, token: str) -> Optional[dict[str, Any]]:
        """Validate token and return user information."""
        pass
    
    @abstractmethod
    def revoke_token(self, token: str) -> bool:
        """Revoke authentication token."""
        pass
    
    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash password for storage."""
        pass
    
    @abstractmethod
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        pass


class TokenAuthenticationInfrastructure(AuthenticationInfrastructure):
    """
    Token-based authentication infrastructure.
    
    Provides secure token generation and validation without depending
    on specific frameworks like Django or Knox.
    """
    
    def __init__(self, secret_key: str, token_expiry_hours: int = 24) -> None:
        """
        Initialize token authentication infrastructure.
        
        Args:
            secret_key: Secret key for token signing
            token_expiry_hours: Token expiration time in hours
        """
        self._secret_key = secret_key
        self._token_expiry_hours = token_expiry_hours
        self._active_tokens: set[str] = set()
    
    def create_authentication_token(self, user_id: str, email: str) -> str:
        """
        Create JWT-like authentication token.
        
        Args:
            user_id: Unique user identifier
            email: User email address
            
        Returns:
            Authentication token string
        """
        import json
        import time
        import hashlib
        import secrets
        
        # Create token payload
        payload: dict[str, Any] = {
            'user_id': user_id,
            'email': email,
            'issued_at': int(time.time()),
            'expires_at': int(time.time()) + (self._token_expiry_hours * 3600),
            'nonce': secrets.token_hex(16)
        }
        
        # Create token string
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hashlib.sha256(
            f"{payload_str}{self._secret_key}".encode()
        ).hexdigest()
        
        token = f"{payload_str.encode().hex()}.{signature}"
        self._active_tokens.add(token)
        
        return token
    
    def validate_token(self, token: str) -> Optional[dict[str, Any]]:
        """
        Validate authentication token.
        
        Args:
            token: Token string to validate
            
        Returns:
            User information if valid, None if invalid
        """
        try:
            import json
            import time
            import hashlib
            
            if token not in self._active_tokens:
                return None
            
            # Split token parts
            payload_hex, signature = token.split('.')
            payload_str = bytes.fromhex(payload_hex).decode()
            
            # Verify signature
            expected_signature = hashlib.sha256(
                f"{payload_str}{self._secret_key}".encode()
            ).hexdigest()
            
            if signature != expected_signature:
                return None
            
            # Parse payload
            payload = json.loads(payload_str)
            
            # Check expiration
            if time.time() > payload['expires_at']:
                self._active_tokens.discard(token)
                return None
            
            return {
                'user_id': payload['user_id'],
                'email': payload['email'],
                'issued_at': payload['issued_at'],
                'expires_at': payload['expires_at']
            }
            
        except Exception:
            return None
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke authentication token.
        
        Args:
            token: Token to revoke
            
        Returns:
            True if token was revoked, False if not found
        """
        if token in self._active_tokens:
            self._active_tokens.remove(token)
            return True
        return False
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using secure algorithm.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        import hashlib
        import secrets
        
        # Generate salt
        salt = secrets.token_hex(32)
        
        # Hash password with salt
        password_hash = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode(), 
            salt.encode(), 
            100000  # iterations
        ).hex()
        
        return f"{salt}${password_hash}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plain text password
            hashed: Hashed password from storage
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            import hashlib
            
            salt, stored_hash = hashed.split('$')
            
            # Hash provided password with stored salt
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt.encode(),
                100000
            ).hex()
            
            return password_hash == stored_hash
        except Exception:
            return False
    
    def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired tokens from active set.
        
        Returns:
            Number of tokens cleaned up
        """
        import time
        
        expired_tokens: set[str] = set()
        
        for token in self._active_tokens.copy():
            token_info = self.validate_token(token)
            if not token_info or time.time() > token_info['expires_at']:
                expired_tokens.add(token)
        
        for expired_token in expired_tokens:
            self._active_tokens.discard(expired_token)
        
        return len(expired_tokens)


class InMemoryUserStore:
    """
    Simple in-memory user store for authentication infrastructure.
    
    In production, this would be replaced by a proper database
    integration through the repository pattern.
    """
    
    def __init__(self) -> None:
        """Initialize empty user store."""
        self._users: dict[str, dict[str, Any]] = {}
    
    def create_user(self, user_id: str, email: str, hashed_password: str) -> bool:
        """
        Create user in store.
        
        Args:
            user_id: Unique user identifier
            email: User email address
            hashed_password: Pre-hashed password
            
        Returns:
            True if user was created, False if already exists
        """
        if email in self._users:
            return False
        
        self._users[email] = {
            'user_id': user_id,
            'email': email,
            'password_hash': hashed_password,
            'is_active': True
        }
        
        return True
    
    def authenticate_user(self, email: str, password: str, auth_infra: AuthenticationInfrastructure) -> Optional[dict[str, Any]]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email
            password: Plain text password
            auth_infra: Authentication infrastructure for password verification
            
        Returns:
            User info if authenticated, None otherwise
        """
        if email not in self._users:
            return None
        
        user = self._users[email]
        
        if not user['is_active']:
            return None
        
        if auth_infra.verify_password(password, user['password_hash']):
            return {
                'user_id': user['user_id'],
                'email': user['email']
            }
        
        return None
    
    def get_user_by_email(self, email: str) -> Optional[dict[str, Any]]:
        """
        Get user information by email.
        
        Args:
            email: User email
            
        Returns:
            User info if found, None otherwise
        """
        return self._users.get(email)
    
    def deactivate_user(self, email: str) -> bool:
        """
        Deactivate user account.
        
        Args:
            email: User email
            
        Returns:
            True if user was deactivated, False if not found
        """
        if email in self._users:
            self._users[email]['is_active'] = False
            return True
        return False


def create_authentication_infrastructure(secret_key: str) -> tuple[AuthenticationInfrastructure, InMemoryUserStore]:
    """
    Factory function to create authentication infrastructure.
    
    Args:
        secret_key: Secret key for token signing
        
    Returns:
        Tuple of (authentication_infrastructure, user_store)
    """
    auth_infra = TokenAuthenticationInfrastructure(secret_key)
    user_store = InMemoryUserStore()
    
    return auth_infra, user_store