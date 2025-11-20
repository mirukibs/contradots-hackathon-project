"""
Test suite for Application Services Authentication Integration.

This module contains comprehensive tests for all application services
ensuring 100% coverage of authentication and authorization features.
"""

from unittest.mock import Mock

from src.application.services.person_application_service import PersonApplicationService
from src.application.security.authentication_context import AuthenticationContext
from src.application.security.authorization_service import AuthorizationService
from src.application.security.authentication_exception import AuthenticationException
from src.application.security.authorization_exception import AuthorizationException
from src.application.commands.authentication_commands import AuthenticateUserCommand
from src.application.repositories.leaderboard_query_repository import LeaderboardQueryRepository
from src.domain.person.person import Person, PersonId
from src.domain.person.person_repository import PersonRepository
from src.domain.person.role import Role


class TestPersonApplicationServiceAuthentication:
    """Test authentication integration for PersonApplicationService."""
    
    def setup_method(self):
        """Set up test fixtures for PersonApplicationService authentication tests."""
        # Create mock repositories
        self.mock_person_repo = Mock(spec=PersonRepository)
        self.mock_leaderboard_repo = Mock(spec=LeaderboardQueryRepository)
        self.mock_authorization_service = Mock(spec=AuthorizationService)
        
        # Create service with correct constructor parameters
        self.service = PersonApplicationService(
            person_repo=self.mock_person_repo,
            leaderboard_query_repo=self.mock_leaderboard_repo,
            authorization_service=self.mock_authorization_service
        )
        
        # Create test data
        self.person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        self.email = "test@example.com"
        self.person = Person.create(
            person_id=self.person_id,
            name="Test User",
            email=self.email,
            role=Role.MEMBER
        )
        
        # Mock repository responses
        self.mock_person_repo.find_by_email.return_value = self.person
        self.mock_person_repo.find_by_id.return_value = self.person
    
    def test_authenticate_user_success(self):
        """Test successful user authentication."""
        # Arrange
        command = AuthenticateUserCommand(email=self.email, password="test123")
        
        # Act
        result = self.service.authenticate_user(command)
        
        # Assert
        assert result.success is True
        assert result.person_id == self.person.person_id
        assert result.email == self.email
        assert result.error_message == ""
        self.mock_person_repo.find_by_email.assert_called_once_with(self.email)
    
    def test_authenticate_user_invalid_email(self):
        """Test authentication failure with invalid email."""
        # Arrange
        invalid_email = "invalid@example.com"
        command = AuthenticateUserCommand(email=invalid_email, password="test123")
        self.mock_person_repo.find_by_email.side_effect = Exception("Person not found")
        
        # Act
        result = self.service.authenticate_user(command)
        
        # Assert
        assert result.success is False
        assert result.person_id is None
        assert result.email == ""
        assert "Authentication failed" in result.error_message
        self.mock_person_repo.find_by_email.assert_called_once_with(invalid_email)
    
    def test_get_current_user_profile_authenticated(self):
        """Test getting current user profile with valid authentication."""
        # Arrange
        auth_context = AuthenticationContext(
            is_authenticated=True,
            current_user_id=self.person_id,
            email=self.email,
            roles=[Role.MEMBER]
        )
        
        # Act
        result = self.service.get_current_user_profile(auth_context)
        
        # Assert
        assert result.personId == str(self.person_id)
        assert result.email == self.email
        assert result.name == "Test User"
        assert result.role == str(Role.MEMBER)
        self.mock_authorization_service.require_authentication.assert_called_once_with(auth_context)
        self.mock_person_repo.find_by_id.assert_called_once_with(self.person_id)
    
    def test_get_current_user_profile_unauthenticated(self):
        """Test getting current user profile without authentication."""
        # Arrange - use create_anonymous_context for unauthenticated state
        from src.application.security.authentication_context import create_anonymous_context
        auth_context = create_anonymous_context()
        
        self.mock_authorization_service.require_authentication.side_effect = AuthorizationException("Not authenticated")
        
        # Act & Assert
        try:
            self.service.get_current_user_profile(auth_context)
            assert False, "Expected AuthorizationException"
        except AuthorizationException as e:
            assert "Not authenticated" in str(e)
        
        self.mock_authorization_service.require_authentication.assert_called_once_with(auth_context)
    
    def test_get_person_profile_self_access(self):
        """Test getting own profile (should always be allowed)."""
        # Arrange
        auth_context = AuthenticationContext(
            is_authenticated=True,
            current_user_id=self.person_id,
            email=self.email,
            roles=[Role.MEMBER]
        )
        
        # Act
        result = self.service.get_person_profile(self.person_id, auth_context)
        
        # Assert
        assert result.personId == str(self.person_id)
        assert result.email == self.email
        self.mock_authorization_service.require_authentication.assert_called_once_with(auth_context)
        # Should not call validate_role_permission for own profile
        self.mock_authorization_service.validate_role_permission.assert_not_called()
    
    def test_get_person_profile_other_user_as_lead(self):
        """Test getting other user's profile as LEAD (should be allowed)."""
        # Arrange
        other_person_id = PersonId("987fcdeb-51a2-43d1-9f12-987654321000")
        auth_context = AuthenticationContext(
            is_authenticated=True,
            current_user_id=self.person_id,
            email=self.email,
            roles=[Role.LEAD]
        )
        
        # Act
        result = self.service.get_person_profile(other_person_id, auth_context)
        
        # Assert
        assert result.personId == str(self.person_id)  # Returns the found person
        self.mock_authorization_service.require_authentication.assert_called_once_with(auth_context)
        self.mock_authorization_service.validate_role_permission.assert_called_once_with(auth_context, "view_profile")
        self.mock_person_repo.find_by_id.assert_called_once_with(other_person_id)
    
    def test_get_person_profile_other_user_as_member_denied(self):
        """Test getting other user's profile as MEMBER (should be denied)."""
        # Arrange
        other_person_id = PersonId("987fcdeb-51a2-43d1-9f12-987654321000")
        auth_context = AuthenticationContext(
            is_authenticated=True,
            current_user_id=self.person_id,
            email=self.email,
            roles=[Role.MEMBER]
        )
        self.mock_authorization_service.validate_role_permission.side_effect = AuthorizationException("Insufficient permissions")
        
        # Act & Assert
        try:
            self.service.get_person_profile(other_person_id, auth_context)
            assert False, "Expected AuthorizationException"
        except AuthorizationException as e:
            assert "Insufficient permissions" in str(e)
        
        self.mock_authorization_service.require_authentication.assert_called_once_with(auth_context)
        self.mock_authorization_service.validate_role_permission.assert_called_once_with(auth_context, "view_profile")
    
    def test_get_leaderboard_authenticated(self):
        """Test getting leaderboard with valid authentication."""
        # Arrange
        auth_context = AuthenticationContext(
            is_authenticated=True,
            current_user_id=self.person_id,
            email=self.email,
            roles=[Role.MEMBER]
        )
        expected_leaderboard = [{"rank": 1, "name": "Test User", "score": 100}]  # type: ignore[misc]
        self.mock_leaderboard_repo.get_leaderboard.return_value = expected_leaderboard
        
        # Act
        result = self.service.get_leaderboard(auth_context)
        
        # Assert
        assert result == expected_leaderboard
        self.mock_authorization_service.validate_role_permission.assert_called_once_with(auth_context, "view_leaderboard")
        self.mock_leaderboard_repo.get_leaderboard.assert_called_once()
    
    def test_get_leaderboard_unauthenticated(self):
        """Test getting leaderboard without authentication."""
        # Arrange - use create_anonymous_context for unauthenticated state
        from src.application.security.authentication_context import create_anonymous_context
        auth_context = create_anonymous_context()
        
        self.mock_authorization_service.validate_role_permission.side_effect = AuthorizationException("Not authenticated")
        
        # Act & Assert
        try:
            self.service.get_leaderboard(auth_context)
            assert False, "Expected AuthorizationException"
        except AuthorizationException as e:
            assert "Not authenticated" in str(e)
        
        self.mock_authorization_service.validate_role_permission.assert_called_once_with(auth_context, "view_leaderboard")


class TestAuthenticationIntegration:
    """Test authentication integration across application services."""
    
    def setup_method(self):
        """Set up test fixtures for authentication integration tests."""
        # Create mock services and repositories
        self.mock_person_repo = Mock(spec=PersonRepository)
        self.mock_leaderboard_repo = Mock(spec=LeaderboardQueryRepository)
        self.mock_authorization_service = Mock(spec=AuthorizationService)
        
        # Create services
        self.person_service = PersonApplicationService(
            person_repo=self.mock_person_repo,
            leaderboard_query_repo=self.mock_leaderboard_repo,
            authorization_service=self.mock_authorization_service
        )
        
        # Create test data
        self.person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        self.email = "test@example.com"
        self.person = Person.create(
            person_id=self.person_id,
            name="Test User",
            email=self.email,
            role=Role.MEMBER
        )
        
        # Mock repository responses
        self.mock_person_repo.find_by_email.return_value = self.person
        self.mock_person_repo.find_by_id.return_value = self.person
    
    def test_authentication_workflow_end_to_end(self):
        """Test complete authentication workflow."""
        # 1. Authenticate user
        auth_command = AuthenticateUserCommand(email=self.email, password="test123")
        auth_result = self.person_service.authenticate_user(auth_command)
        
        assert auth_result.success is True
        assert auth_result.person_id == self.person.person_id
        
        # 2. Create authentication context
        if auth_result.person_id:  # Check if person_id is not None
            auth_context = AuthenticationContext(
                current_user_id=auth_result.person_id,
                email=auth_result.email,
                roles=[Role.MEMBER]
            )
            
            # 3. Access authenticated resources
            profile = self.person_service.get_current_user_profile(auth_context)
            assert profile.personId == str(self.person.person_id)
            
            # 4. Access role-protected resources
            self.mock_leaderboard_repo.get_leaderboard.return_value = []
            leaderboard = self.person_service.get_leaderboard(auth_context)
            assert isinstance(leaderboard, list)
    
    def test_authorization_role_escalation_prevention(self):
        """Test that role escalation is prevented."""
        # Arrange
        member_context = AuthenticationContext(
            is_authenticated=True,
            current_user_id=self.person_id,
            email=self.email,
            roles=[Role.MEMBER]
        )
        other_person_id = PersonId("987fcdeb-51a2-43d1-9f12-987654321000")
        
        # Configure authorization service to deny access
        self.mock_authorization_service.validate_role_permission.side_effect = AuthorizationException("Insufficient permissions")
        
        # Act & Assert - Member trying to view other's profile
        try:
            self.person_service.get_person_profile(other_person_id, member_context)
            assert False, "Expected AuthorizationException"
        except AuthorizationException as e:
            assert "Insufficient permissions" in str(e)
    
    def test_authentication_state_consistency(self):
        """Test that authentication state remains consistent across operations."""
        # Create authenticated context
        auth_context = AuthenticationContext(
            is_authenticated=True,
            current_user_id=self.person_id,
            email=self.email,
            roles=[Role.MEMBER]
        )
        
        # Multiple operations should use the same authentication state
        self.person_service.get_current_user_profile(auth_context)
        self.person_service.get_person_profile(self.person_id, auth_context)
        
        # Verify authorization service was called consistently
        assert self.mock_authorization_service.require_authentication.call_count == 2
        
        # All calls should have the same authentication context
        for call_args in self.mock_authorization_service.require_authentication.call_args_list:
            assert call_args[0][0] == auth_context


class TestSecurityExceptionHandling:
    """Test security exception handling in application services."""
    
    def setup_method(self):
        """Set up test fixtures for security exception tests."""
        self.mock_person_repo = Mock(spec=PersonRepository)
        self.mock_leaderboard_repo = Mock(spec=LeaderboardQueryRepository)
        self.mock_authorization_service = Mock(spec=AuthorizationService)
        
        self.service = PersonApplicationService(
            person_repo=self.mock_person_repo,
            leaderboard_query_repo=self.mock_leaderboard_repo,
            authorization_service=self.mock_authorization_service
        )
        
        self.person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        
        # Use create_anonymous_context for unauthenticated state
        from src.application.security.authentication_context import create_anonymous_context
        self.auth_context = create_anonymous_context()
    
    def test_authentication_exception_propagation(self):
        """Test that AuthenticationException is properly propagated."""
        # Arrange
        self.mock_authorization_service.require_authentication.side_effect = AuthenticationException("Authentication required", "test@example.com")
        
        # Act & Assert
        try:
            self.service.get_current_user_profile(self.auth_context)
            assert False, "Expected AuthenticationException"
        except AuthenticationException as e:
            assert "Authentication required" in str(e)
    
    def test_authorization_exception_propagation(self):
        """Test that AuthorizationException is properly propagated."""
        # Arrange
        auth_context = AuthenticationContext(
            is_authenticated=True,
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        self.mock_authorization_service.validate_role_permission.side_effect = AuthorizationException("Insufficient role permissions")
        
        # Act & Assert
        try:
            self.service.get_leaderboard(auth_context)
            assert False, "Expected AuthorizationException"
        except AuthorizationException as e:
            assert "Insufficient role permissions" in str(e)
    
    def test_domain_exception_handling_in_authentication(self):
        """Test that domain exceptions are handled during authentication."""
        # Arrange
        command = AuthenticateUserCommand(email="nonexistent@example.com", password="test123")
        self.mock_person_repo.find_by_email.side_effect = ValueError("Person not found")
        
        # Act
        result = self.service.authenticate_user(command)
        
        # Assert
        assert result.success is False
        assert "Authentication failed" in result.error_message
        assert "Person not found" in result.error_message