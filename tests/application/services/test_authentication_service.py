"""
Tests for authentication service.

This module contains comprehensive tests for the AuthenticationService
to ensure proper authentication workflows and error handling.
"""

from unittest.mock import Mock
from src.application.services.authentication_service import AuthenticationService
from src.application.commands.authentication_commands import LoginCommand, LogoutCommand
from src.application.dtos.authentication_dtos import LoginResult, UserInfo
from src.application.security.authentication_context import AuthenticationContext, create_anonymous_context
from src.application.security.authentication_exception import AuthenticationException
from src.domain.person.person import Person
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.person.role import Role


class TestAuthenticationService:
    """Test class for AuthenticationService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_person_repository = Mock()
        self.service = AuthenticationService(self.mock_person_repository)
        
        # Create test person
        self.test_person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        self.test_email = "test@example.com"
        self.test_name = "Test User"
        self.test_role = Role.MEMBER
        
        self.test_person = Mock(spec=Person)
        self.test_person.person_id = self.test_person_id
        self.test_person.email = self.test_email
        self.test_person.name = self.test_name
        self.test_person.role = self.test_role
        self.test_person.can_authenticate_with_email.return_value = True

    def test_authentication_service_initialization(self):
        """Test authentication service initialization."""
        # Arrange & Act
        service = AuthenticationService(self.mock_person_repository)
        
        # Assert
        assert service is not None
        assert hasattr(service, 'handle_login')
        assert hasattr(service, 'handle_logout')
        assert hasattr(service, 'create_authentication_context')
        assert hasattr(service, 'get_user_info')
        assert hasattr(service, 'validate_authentication')

    def test_handle_login_success(self):
        """Test successful login handling."""
        # Arrange
        command = LoginCommand(self.test_email, "password123")
        self.mock_person_repository.find_by_email.return_value = self.test_person
        
        # Act
        result = self.service.handle_login(command)
        
        # Assert
        assert isinstance(result, LoginResult)
        assert result.success
        assert result.person_id == self.test_person_id
        assert result.email == self.test_email
        self.mock_person_repository.find_by_email.assert_called_once_with(self.test_email)
        self.test_person.can_authenticate_with_email.assert_called_once_with(self.test_email)

    def test_handle_login_invalid_email_credentials(self):
        """Test login with invalid email credentials."""
        # Arrange
        command = LoginCommand(self.test_email, "password123")
        self.mock_person_repository.find_by_email.return_value = self.test_person
        self.test_person.can_authenticate_with_email.return_value = False
        
        # Act
        result = self.service.handle_login(command)
        
        # Assert
        assert isinstance(result, LoginResult)
        assert not result.success
        assert result.error_message == "Invalid email credentials"
        self.mock_person_repository.find_by_email.assert_called_once_with(self.test_email)
        self.test_person.can_authenticate_with_email.assert_called_once_with(self.test_email)

    def test_handle_login_person_not_found(self):
        """Test login when person is not found."""
        # Arrange
        command = LoginCommand("nonexistent@example.com", "password123")
        self.mock_person_repository.find_by_email.side_effect = Exception("Person not found")
        
        # Act
        result = self.service.handle_login(command)
        
        # Assert
        assert isinstance(result, LoginResult)
        assert not result.success
        assert "Authentication failed: Person not found" in result.error_message
        self.mock_person_repository.find_by_email.assert_called_once_with("nonexistent@example.com")

    def test_handle_logout_authenticated_user(self):
        """Test logout with authenticated user."""
        # Arrange
        context = AuthenticationContext(
            current_user_id=self.test_person_id,
            email=self.test_email,
            roles=[self.test_role],
            is_authenticated=True
        )
        command = LogoutCommand(context)
        
        # Act
        result = self.service.handle_logout(command)
        
        # Assert
        assert result is True

    def test_handle_logout_unauthenticated_user(self):
        """Test logout with unauthenticated user."""
        # Arrange
        context = create_anonymous_context()
        command = LogoutCommand(context)
        
        # Act
        result = self.service.handle_logout(command)
        
        # Assert
        assert result is False

    def test_handle_logout_exception(self):
        """Test logout when exception occurs."""
        # Arrange
        mock_context = Mock()
        # Make is_authenticated a property that raises an exception when accessed
        type(mock_context).is_authenticated = property(lambda self: (_ for _ in ()).throw(Exception("Context error")))
        command = LogoutCommand(mock_context)
        
        # Act
        result = self.service.handle_logout(command)
        
        # Assert
        assert result is False

    def test_create_authentication_context_success(self):
        """Test successful creation of authentication context."""
        # Arrange
        login_result = LoginResult.successful(self.test_person_id, self.test_email)
        self.mock_person_repository.find_by_id.return_value = self.test_person
        
        # Act
        context = self.service.create_authentication_context(login_result)
        
        # Assert
        assert isinstance(context, AuthenticationContext)
        assert context.current_user_id == self.test_person_id
        assert context.email == self.test_email
        assert context.roles == [self.test_role]
        assert context.is_authenticated is True
        self.mock_person_repository.find_by_id.assert_called_once_with(self.test_person_id)

    def test_create_authentication_context_failed_login(self):
        """Test creation of authentication context from failed login."""
        # Arrange
        login_result = LoginResult.failed("Login failed")
        
        # Act & Assert
        try:
            self.service.create_authentication_context(login_result)
            assert False, "Expected AuthenticationException to be raised"
        except AuthenticationException as e:
            assert "Cannot create context from failed login" in str(e)

    def test_create_authentication_context_missing_person_id(self):
        """Test creation of authentication context with missing person ID."""
        # Arrange
        login_result = Mock()
        login_result.success = True
        login_result.person_id = None
        login_result.email = self.test_email
        
        # Act & Assert
        try:
            self.service.create_authentication_context(login_result)
            assert False, "Expected AuthenticationException to be raised"
        except AuthenticationException as e:
            assert "Person ID missing from login result" in str(e)

    def test_create_authentication_context_person_not_found(self):
        """Test creation of authentication context when person not found."""
        # Arrange
        login_result = LoginResult.successful(self.test_person_id, self.test_email)
        self.mock_person_repository.find_by_id.side_effect = Exception("Person not found")
        
        # Act & Assert
        try:
            self.service.create_authentication_context(login_result)
            assert False, "Expected AuthenticationException to be raised"
        except AuthenticationException as e:
            assert "Failed to get person roles" in str(e)
            assert e.email == self.test_email

    def test_get_user_info_success(self):
        """Test successful user info retrieval."""
        # Arrange
        context = AuthenticationContext(
            current_user_id=self.test_person_id,
            email=self.test_email,
            roles=[self.test_role],
            is_authenticated=True
        )
        self.mock_person_repository.find_by_id.return_value = self.test_person
        
        # Act
        user_info = self.service.get_user_info(context)
        
        # Assert
        assert isinstance(user_info, UserInfo)
        assert user_info.person_id == self.test_person_id
        assert user_info.email == self.test_email
        assert user_info.name == self.test_name
        assert user_info.role == self.test_role.value
        self.mock_person_repository.find_by_id.assert_called_once_with(self.test_person_id)

    def test_get_user_info_unauthenticated(self):
        """Test user info retrieval for unauthenticated user."""
        # Arrange
        context = create_anonymous_context()
        
        # Act & Assert
        try:
            self.service.get_user_info(context)
            assert False, "Expected AuthenticationException to be raised"
        except AuthenticationException as e:
            assert "User is not authenticated" in str(e)

    def test_get_user_info_person_not_found(self):
        """Test user info retrieval when person not found."""
        # Arrange
        context = AuthenticationContext(
            current_user_id=self.test_person_id,
            email=self.test_email,
            roles=[self.test_role],
            is_authenticated=True
        )
        self.mock_person_repository.find_by_id.side_effect = Exception("Person not found")
        
        # Act & Assert
        try:
            self.service.get_user_info(context)
            assert False, "Expected AuthenticationException to be raised"
        except AuthenticationException as e:
            assert "Failed to get user info: Person not found" in str(e)
            assert e.email == self.test_email

    def test_validate_authentication_success(self):
        """Test successful authentication validation."""
        # Arrange
        context = AuthenticationContext(
            current_user_id=self.test_person_id,
            email=self.test_email,
            roles=[self.test_role],
            is_authenticated=True
        )
        self.mock_person_repository.find_by_id.return_value = self.test_person
        
        # Act
        result = self.service.validate_authentication(context)
        
        # Assert
        assert result is True
        self.mock_person_repository.find_by_id.assert_called_once_with(self.test_person_id)
        self.test_person.can_authenticate_with_email.assert_called_once_with(self.test_email)

    def test_validate_authentication_unauthenticated(self):
        """Test authentication validation for unauthenticated context."""
        # Arrange
        context = create_anonymous_context()
        
        # Act
        result = self.service.validate_authentication(context)
        
        # Assert
        assert result is False

    def test_validate_authentication_person_not_found(self):
        """Test authentication validation when person not found."""
        # Arrange
        context = AuthenticationContext(
            current_user_id=self.test_person_id,
            email=self.test_email,
            roles=[self.test_role],
            is_authenticated=True
        )
        self.mock_person_repository.find_by_id.side_effect = Exception("Person not found")
        
        # Act
        result = self.service.validate_authentication(context)
        
        # Assert
        assert result is False
        self.mock_person_repository.find_by_id.assert_called_once_with(self.test_person_id)

    def test_validate_authentication_invalid_credentials(self):
        """Test authentication validation with invalid credentials."""
        # Arrange
        context = AuthenticationContext(
            current_user_id=self.test_person_id,
            email=self.test_email,
            roles=[self.test_role],
            is_authenticated=True
        )
        self.mock_person_repository.find_by_id.return_value = self.test_person
        self.test_person.can_authenticate_with_email.return_value = False
        
        # Act
        result = self.service.validate_authentication(context)
        
        # Assert
        assert result is False
        self.mock_person_repository.find_by_id.assert_called_once_with(self.test_person_id)
        self.test_person.can_authenticate_with_email.assert_called_once_with(self.test_email)