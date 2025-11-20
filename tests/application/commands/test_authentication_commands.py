"""
Test suite for authentication commands.

This module contains comprehensive tests for AuthenticateUserCommand,
LoginCommand, and LogoutCommand to ensure 100% coverage.
"""

from src.application.commands.authentication_commands import (
    AuthenticateUserCommand, 
    LoginCommand, 
    LogoutCommand
)
from src.application.security.authentication_context import AuthenticationContext
from src.domain.person.person import PersonId
from src.domain.person.role import Role


class TestAuthenticateUserCommand:
    """Test cases for AuthenticateUserCommand class."""
    
    def test_authenticate_user_command_initialization_success(self):
        """Test successful initialization of AuthenticateUserCommand."""
        email = "test@example.com"
        password = "password123"
        
        command = AuthenticateUserCommand(email, password)
        
        assert command.email == "test@example.com"  # Normalized to lowercase and stripped
        assert command.password == "password123"
    
    def test_authenticate_user_command_email_normalization(self):
        """Test email normalization in AuthenticateUserCommand."""
        email = "  TEST@EXAMPLE.COM  "
        password = "password123"
        
        command = AuthenticateUserCommand(email, password)
        
        assert command.email == "test@example.com"
    
    def test_authenticate_user_command_empty_email(self):
        """Test AuthenticateUserCommand with empty email."""
        try:
            AuthenticateUserCommand("", "password123")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Email is required" in str(e)
    
    def test_authenticate_user_command_whitespace_email(self):
        """Test AuthenticateUserCommand with whitespace-only email."""
        try:
            AuthenticateUserCommand("   ", "password123")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Email is required" in str(e)
    
    def test_authenticate_user_command_none_email(self):
        """Test AuthenticateUserCommand with None email."""
        try:
            # Since the type hint doesn't allow None, we'll test the actual behavior
            # In a real scenario, this would be caught by type checking
            command = AuthenticateUserCommand(None, "password123")  # type: ignore
            assert False, "Should have raised an exception"
        except (ValueError, TypeError):
            # Could be ValueError from our validation or TypeError from Python
            assert True  # Any exception is acceptable here
    
    def test_authenticate_user_command_empty_password(self):
        """Test AuthenticateUserCommand with empty password."""
        try:
            AuthenticateUserCommand("test@example.com", "")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Password is required" in str(e)
    
    def test_authenticate_user_command_none_password(self):
        """Test AuthenticateUserCommand with None password."""
        try:
            # Since the type hint doesn't allow None, we'll test the actual behavior
            command = AuthenticateUserCommand("test@example.com", None)  # type: ignore
            assert False, "Should have raised an exception"
        except (ValueError, TypeError):
            # Could be ValueError from our validation or TypeError from Python
            assert True  # Any exception is acceptable here
    
    def test_authenticate_user_command_equality_same_email(self):
        """Test equality for commands with same email."""
        command1 = AuthenticateUserCommand("test@example.com", "password123")
        command2 = AuthenticateUserCommand("test@example.com", "different_password")
        
        assert command1 == command2  # Equality based on email only
    
    def test_authenticate_user_command_equality_different_email(self):
        """Test equality for commands with different email."""
        command1 = AuthenticateUserCommand("test1@example.com", "password123")
        command2 = AuthenticateUserCommand("test2@example.com", "password123")
        
        assert command1 != command2
    
    def test_authenticate_user_command_equality_non_command(self):
        """Test equality with non-command object."""
        command = AuthenticateUserCommand("test@example.com", "password123")
        
        assert command != "not a command"
        assert command != 42
        assert command != None
    
    def test_authenticate_user_command_repr(self):
        """Test string representation of AuthenticateUserCommand."""
        command = AuthenticateUserCommand("test@example.com", "password123")
        
        repr_str = repr(command)
        assert "AuthenticateUserCommand" in repr_str
        assert "test@example.com" in repr_str
        assert "password123" not in repr_str  # Password should not appear in repr


class TestLoginCommand:
    """Test cases for LoginCommand class."""
    
    def test_login_command_initialization_success(self):
        """Test successful initialization of LoginCommand."""
        email = "test@example.com"
        password = "password123"
        
        command = LoginCommand(email, password)
        
        assert command.email == "test@example.com"
        assert command.password == "password123"
    
    def test_login_command_email_normalization(self):
        """Test email normalization in LoginCommand."""
        email = "  TEST@EXAMPLE.COM  "
        password = "password123"
        
        command = LoginCommand(email, password)
        
        assert command.email == "test@example.com"
    
    def test_login_command_empty_email(self):
        """Test LoginCommand with empty email."""
        try:
            LoginCommand("", "password123")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Email is required" in str(e)
    
    def test_login_command_whitespace_email(self):
        """Test LoginCommand with whitespace-only email."""
        try:
            LoginCommand("   ", "password123")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Email is required" in str(e)
    
    def test_login_command_none_email(self):
        """Test LoginCommand with None email."""
        try:
            # Since the type hint doesn't allow None, we'll test the actual behavior
            command = LoginCommand(None, "password123")  # type: ignore
            assert False, "Should have raised an exception"
        except (ValueError, TypeError):
            # Could be ValueError from our validation or TypeError from Python
            assert True  # Any exception is acceptable here
    
    def test_login_command_empty_password(self):
        """Test LoginCommand with empty password."""
        try:
            LoginCommand("test@example.com", "")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Password is required" in str(e)
    
    def test_login_command_none_password(self):
        """Test LoginCommand with None password."""
        try:
            # Since the type hint doesn't allow None, we'll test the actual behavior
            command = LoginCommand("test@example.com", None)  # type: ignore
            assert False, "Should have raised an exception"
        except (ValueError, TypeError):
            # Could be ValueError from our validation or TypeError from Python
            assert True  # Any exception is acceptable here
    
    def test_login_command_equality_same_email(self):
        """Test equality for commands with same email."""
        command1 = LoginCommand("test@example.com", "password123")
        command2 = LoginCommand("test@example.com", "different_password")
        
        assert command1 == command2  # Equality based on email only
    
    def test_login_command_equality_different_email(self):
        """Test equality for commands with different email."""
        command1 = LoginCommand("test1@example.com", "password123")
        command2 = LoginCommand("test2@example.com", "password123")
        
        assert command1 != command2
    
    def test_login_command_equality_non_command(self):
        """Test equality with non-command object."""
        command = LoginCommand("test@example.com", "password123")
        
        assert command != "not a command"
        assert command != 42
        assert command != None
    
    def test_login_command_repr(self):
        """Test string representation of LoginCommand."""
        command = LoginCommand("test@example.com", "password123")
        
        repr_str = repr(command)
        assert "LoginCommand" in repr_str
        assert "test@example.com" in repr_str
        assert "password123" not in repr_str  # Password should not appear in repr


class TestLogoutCommand:
    """Test cases for LogoutCommand class."""
    
    def test_logout_command_initialization_success(self):
        """Test successful initialization of LogoutCommand."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        context = AuthenticationContext(
            current_user_id=person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        
        command = LogoutCommand(context)
        
        assert command.context == context
    
    def test_logout_command_equality_same_context(self):
        """Test equality for commands with same context."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        context = AuthenticationContext(
            current_user_id=person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        
        command1 = LogoutCommand(context)
        command2 = LogoutCommand(context)
        
        assert command1 == command2
    
    def test_logout_command_equality_different_context(self):
        """Test equality for commands with different context."""
        person_id1 = PersonId("123e4567-e89b-12d3-a456-426614174000")
        person_id2 = PersonId("987fcdeb-51a2-43d1-9f12-987654321000")
        
        context1 = AuthenticationContext(
            current_user_id=person_id1,
            email="test1@example.com",
            roles=[Role.MEMBER]
        )
        context2 = AuthenticationContext(
            current_user_id=person_id2,
            email="test2@example.com",
            roles=[Role.LEAD]
        )
        
        command1 = LogoutCommand(context1)
        command2 = LogoutCommand(context2)
        
        assert command1 != command2
    
    def test_logout_command_equality_non_command(self):
        """Test equality with non-command object."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        context = AuthenticationContext(
            current_user_id=person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        command = LogoutCommand(context)
        
        assert command != "not a command"
        assert command != 42
        assert command != None
    
    def test_logout_command_repr(self):
        """Test string representation of LogoutCommand."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        context = AuthenticationContext(
            current_user_id=person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        command = LogoutCommand(context)
        
        repr_str = repr(command)
        assert "LogoutCommand" in repr_str
        assert str(person_id) in repr_str