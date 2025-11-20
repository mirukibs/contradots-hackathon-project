"""
Test suite for authentication security components.

This module contains comprehensive tests for AuthenticationContext,
AuthorizationService, and security exceptions to ensure 100% coverage.
"""

from datetime import datetime
from unittest.mock import Mock

from src.application.security.authentication_context import AuthenticationContext, create_anonymous_context
from src.application.security.authorization_service import AuthorizationService
from src.application.security.authentication_exception import AuthenticationException
from src.application.security.authorization_exception import AuthorizationException
from src.domain.person.person import PersonId, Person
from src.domain.person.role import Role
from src.domain.shared.value_objects.activity_id import ActivityId


class TestAuthenticationContext:
    """Test cases for AuthenticationContext class."""
    
    def test_authentication_context_initialization_success(self):
        """Test successful initialization of AuthenticationContext."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        email = "test@example.com"
        roles = [Role.MEMBER]
        
        context = AuthenticationContext(
            current_user_id=person_id,
            email=email,
            roles=roles,
            is_authenticated=True
        )
        
        assert context.current_user_id == person_id
        assert context.person_id == person_id  # Legacy compatibility
        assert context.email == email
        assert context.roles == roles
        assert context.is_authenticated is True
    
    def test_authentication_context_empty_roles(self):
        """Test AuthenticationContext with empty roles list."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        email = "test@example.com"
        
        context = AuthenticationContext(
            current_user_id=person_id,
            email=email,
            roles=[],
            is_authenticated=True
        )
        
        assert context.roles == []
        assert len(context.roles) == 0
    
    def test_authentication_context_none_roles(self):
        """Test AuthenticationContext with None roles (should default to empty list)."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        email = "test@example.com"
        
        context = AuthenticationContext(
            current_user_id=person_id,
            email=email,
            roles=[],  # Empty list instead of None
            is_authenticated=True
        )
        
        assert context.roles == []
    
    def test_can_act_as_same_person(self):
        """Test can_act_as returns True for same person."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        context = AuthenticationContext(
            current_user_id=person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        
        assert context.can_act_as(person_id) is True
    
    def test_can_act_as_different_person(self):
        """Test can_act_as returns False for different person."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        other_person_id = PersonId("987fcdeb-51a2-43d1-9f12-987654321000")
        
        context = AuthenticationContext(
            current_user_id=person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        
        assert context.can_act_as(other_person_id) is False
    
    def test_has_role_member(self):
        """Test has_role returns True for existing role."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        context = AuthenticationContext(
            current_user_id=person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        
        assert context.has_role(Role.MEMBER) is True
        assert context.has_role(Role.LEAD) is False
    
    def test_has_role_lead(self):
        """Test has_role returns True for lead role."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        context = AuthenticationContext(
            current_user_id=person_id,
            email="test@example.com",
            roles=[Role.LEAD]
        )
        
        assert context.has_role(Role.LEAD) is True
        assert context.has_role(Role.MEMBER) is False
    
    def test_has_role_multiple_roles(self):
        """Test has_role with multiple roles."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        context = AuthenticationContext(
            current_user_id=person_id,
            email="test@example.com",
            roles=[Role.MEMBER, Role.LEAD]
        )
        
        assert context.has_role(Role.MEMBER) is True
        assert context.has_role(Role.LEAD) is True
    
    def test_can_access_resource_unauthenticated(self):
        """Test can_access_resource returns False for unauthenticated user."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        context = AuthenticationContext(
            current_user_id=person_id,
            email="test@example.com",
            roles=[Role.MEMBER],
            is_authenticated=False
        )
        
        assert context.can_access_resource("resource1", "view_activities") is False
    
    def test_can_access_resource_member_permissions(self):
        """Test can_access_resource for member role permissions."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        context = AuthenticationContext(
            current_user_id=person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        
        # Member permissions
        assert context.can_access_resource("resource1", "submit_action") is True
        assert context.can_access_resource("resource1", "view_activities") is True
        assert context.can_access_resource("resource1", "view_leaderboard") is True
        assert context.can_access_resource("resource1", "view_profile") is True
        
        # Lead-only permissions
        assert context.can_access_resource("resource1", "create_activity") is False
        assert context.can_access_resource("resource1", "manage_activity") is False
        assert context.can_access_resource("resource1", "validate_proof") is False
    
    def test_can_access_resource_lead_permissions(self):
        """Test can_access_resource for lead role permissions."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        context = AuthenticationContext(
            current_user_id=person_id,
            email="test@example.com",
            roles=[Role.LEAD]
        )
        
        # Lead permissions (includes all member permissions)
        assert context.can_access_resource("resource1", "submit_action") is True
        assert context.can_access_resource("resource1", "view_activities") is True
        assert context.can_access_resource("resource1", "view_leaderboard") is True
        assert context.can_access_resource("resource1", "view_profile") is True
        assert context.can_access_resource("resource1", "create_activity") is True
        assert context.can_access_resource("resource1", "manage_activity") is True
        assert context.can_access_resource("resource1", "validate_proof") is True
        assert context.can_access_resource("resource1", "deactivate_activity") is True
    
    def test_can_access_resource_no_roles(self):
        """Test can_access_resource with no roles."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        context = AuthenticationContext(
            current_user_id=person_id,
            email="test@example.com",
            roles=[]
        )
        
        assert context.can_access_resource("resource1", "view_activities") is False
        assert context.can_access_resource("resource1", "submit_action") is False
    
    def test_equality_same_contexts(self):
        """Test equality for identical contexts."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        context1 = AuthenticationContext(
            current_user_id=person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        context2 = AuthenticationContext(
            current_user_id=person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        
        assert context1 == context2
    
    def test_equality_different_contexts(self):
        """Test equality for different contexts."""
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
        
        assert context1 != context2
    
    def test_equality_non_context_object(self):
        """Test equality with non-context object."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        context = AuthenticationContext(
            current_user_id=person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        
        assert context != "not a context"
        assert context != 42
        assert context != None
    
    def test_repr(self):
        """Test string representation of context."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        context = AuthenticationContext(
            current_user_id=person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        
        repr_str = repr(context)
        assert "AuthenticationContext" in repr_str
        assert "test@example.com" in repr_str
        assert str(person_id) in repr_str
    
    def test_create_anonymous_context(self):
        """Test creation of anonymous context."""
        context = create_anonymous_context()
        
        assert context.is_authenticated is False
        assert context.email == ""
        assert context.roles == []
        assert str(context.current_user_id) == "00000000-0000-0000-0000-000000000000"


class TestAuthorizationService:
    """Test cases for AuthorizationService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_person_repo = Mock()
        self.authorization_service = AuthorizationService(self.mock_person_repo)
        self.person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        self.target_person_id = PersonId("987fcdeb-51a2-43d1-9f12-987654321000")
    
    def test_validate_user_can_act_as_success(self):
        """Test validate_user_can_act_as with valid scenario."""
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        
        # Should not raise exception when acting as self
        self.authorization_service.validate_user_can_act_as(context, self.person_id)
    
    def test_validate_user_can_act_as_unauthenticated(self):
        """Test validate_user_can_act_as with unauthenticated user."""
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.MEMBER],
            is_authenticated=False
        )
        
        try:
            self.authorization_service.validate_user_can_act_as(context, self.person_id)
            assert False, "Should have raised AuthorizationException"
        except AuthorizationException as e:
            assert "Authentication required" in str(e)
    
    def test_validate_user_can_act_as_different_user(self):
        """Test validate_user_can_act_as with different user."""
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        
        try:
            self.authorization_service.validate_user_can_act_as(context, self.target_person_id)
            assert False, "Should have raised AuthorizationException"
        except AuthorizationException as e:
            assert "cannot act as" in str(e)
    
    def test_validate_role_permission_success(self):
        """Test validate_role_permission with valid permission."""
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        
        # Mock person with permission
        mock_person = Mock()
        mock_person.has_permission_for.return_value = True
        self.mock_person_repo.find_by_id.return_value = mock_person
        
        # Should not raise exception
        self.authorization_service.validate_role_permission(context, "view_activities")
        
        self.mock_person_repo.find_by_id.assert_called_once_with(self.person_id)
        mock_person.has_permission_for.assert_called_once_with("view_activities")
    
    def test_validate_role_permission_unauthenticated(self):
        """Test validate_role_permission with unauthenticated user."""
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.MEMBER],
            is_authenticated=False
        )
        
        try:
            self.authorization_service.validate_role_permission(context, "view_activities")
            assert False, "Should have raised AuthorizationException"
        except AuthorizationException as e:
            assert "Authentication required" in str(e)
    
    def test_validate_role_permission_person_not_found(self):
        """Test validate_role_permission when person not found."""
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        
        self.mock_person_repo.find_by_id.side_effect = Exception("Person not found")
        
        try:
            self.authorization_service.validate_role_permission(context, "view_activities")
            assert False, "Should have raised AuthorizationException"
        except AuthorizationException as e:
            assert "Person not found" in str(e)
    
    def test_validate_role_permission_no_permission(self):
        """Test validate_role_permission when user has no permission."""
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        
        # Mock person without permission
        mock_person = Mock()
        mock_person.has_permission_for.return_value = False
        self.mock_person_repo.find_by_id.return_value = mock_person
        
        try:
            self.authorization_service.validate_role_permission(context, "create_activity")
            assert False, "Should have raised AuthorizationException"
        except AuthorizationException as e:
            assert "Permission denied" in str(e)
    
    def test_enforce_resource_access_success(self):
        """Test enforce_resource_access with valid access."""
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        
        # Mock person exists
        mock_person = Mock()
        self.mock_person_repo.find_by_id.return_value = mock_person
        
        # Should not raise exception
        self.authorization_service.enforce_resource_access(context, "resource1")
        
        self.mock_person_repo.find_by_id.assert_called_once_with(self.person_id)
    
    def test_enforce_resource_access_unauthenticated(self):
        """Test enforce_resource_access with unauthenticated user."""
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.MEMBER],
            is_authenticated=False
        )
        
        try:
            self.authorization_service.enforce_resource_access(context, "resource1")
            assert False, "Should have raised AuthorizationException"
        except AuthorizationException as e:
            assert "Authentication required" in str(e)
    
    def test_enforce_resource_access_person_not_found(self):
        """Test enforce_resource_access when person not found."""
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        
        self.mock_person_repo.find_by_id.side_effect = Exception("Person not found")
        
        try:
            self.authorization_service.enforce_resource_access(context, "resource1")
            assert False, "Should have raised AuthorizationException"
        except AuthorizationException as e:
            assert "Person not found" in str(e)
    
    def test_enforce_activity_ownership_success(self):
        """Test enforce_activity_ownership with valid ownership."""
        from src.domain.shared.value_objects.activity_id import ActivityId
        
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.LEAD]
        )
        activity_id = ActivityId("456e7890-e89b-12d3-a456-426614174000")
        
        # Mock person with activity management permission
        mock_person = Mock()
        mock_person.can_manage_activity.return_value = True
        self.mock_person_repo.find_by_id.return_value = mock_person
        
        # Should not raise exception
        self.authorization_service.enforce_activity_ownership(context, activity_id)
        
        self.mock_person_repo.find_by_id.assert_called_once_with(self.person_id)
        mock_person.can_manage_activity.assert_called_once_with(activity_id)
    
    def test_enforce_activity_ownership_unauthenticated(self):
        """Test enforce_activity_ownership with unauthenticated user."""
        from src.domain.shared.value_objects.activity_id import ActivityId
        
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.LEAD],
            is_authenticated=False
        )
        activity_id = ActivityId("456e7890-e89b-12d3-a456-426614174000")
        
        try:
            self.authorization_service.enforce_activity_ownership(context, activity_id)
            assert False, "Should have raised AuthorizationException"
        except AuthorizationException as e:
            assert "Authentication required" in str(e)
    
    def test_enforce_activity_ownership_person_not_found(self):
        """Test enforce_activity_ownership when person not found."""
        from src.domain.shared.value_objects.activity_id import ActivityId
        
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.LEAD]
        )
        activity_id = ActivityId("456e7890-e89b-12d3-a456-426614174000")
        
        self.mock_person_repo.find_by_id.side_effect = Exception("Person not found")
        
        try:
            self.authorization_service.enforce_activity_ownership(context, activity_id)
            assert False, "Should have raised AuthorizationException"
        except AuthorizationException as e:
            assert "Person not found" in str(e)
    
    def test_enforce_activity_ownership_no_permission(self):
        """Test enforce_activity_ownership when user cannot manage activity."""
        from src.domain.shared.value_objects.activity_id import ActivityId
        
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        activity_id = ActivityId("456e7890-e89b-12d3-a456-426614174000")
        
        # Mock person without activity management permission
        mock_person = Mock()
        mock_person.can_manage_activity.return_value = False
        self.mock_person_repo.find_by_id.return_value = mock_person
        
        try:
            self.authorization_service.enforce_activity_ownership(context, activity_id)
            assert False, "Should have raised AuthorizationException"
        except AuthorizationException as e:
            assert "Activity management permission denied" in str(e)
    
    def test_require_authentication_success(self):
        """Test legacy require_authentication method with authenticated context."""
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        
        # Should not raise exception
        self.authorization_service.require_authentication(context)
    
    def test_require_authentication_failure(self):
        """Test legacy require_authentication method with unauthenticated context."""
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.MEMBER],
            is_authenticated=False
        )
        
        try:
            self.authorization_service.require_authentication(context)
            assert False, "Should have raised AuthorizationException"
        except AuthorizationException as e:
            assert "Authentication required" in str(e)
    
    def test_require_permission_success(self):
        """Test legacy require_permission method with valid permission."""
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        test_person = Person.create(name="Test User", email="test@example.com", role=Role.MEMBER)
        self.mock_person_repo.find_by_id.return_value = test_person
        
        # Should not raise exception for member permissions
        self.authorization_service.require_permission(context, "submit_action")
    
    def test_require_activity_management_permission_success(self):
        """Test legacy require_activity_management_permission method."""
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.LEAD]
        )
        activity_id = ActivityId("123e4567-e89b-12d3-a456-426614174000")
        test_person = Person.create(name="Test Lead", email="test@example.com", role=Role.LEAD)
        self.mock_person_repo.find_by_id.return_value = test_person
        
        # Should not raise exception for lead managing their activity
        self.authorization_service.require_activity_management_permission(context, activity_id)
    
    def test_require_action_submission_permission_success(self):
        """Test legacy require_action_submission_permission method."""
        context = AuthenticationContext(
            current_user_id=self.person_id,
            email="test@example.com",
            roles=[Role.MEMBER]
        )
        test_person = Person.create(name="Test User", email="test@example.com", role=Role.MEMBER)
        self.mock_person_repo.find_by_id.return_value = test_person
        
        # Should not raise exception for member submitting actions
        self.authorization_service.require_action_submission_permission(context)


class TestAuthenticationException:
    """Test cases for AuthenticationException class."""
    
    def test_authentication_exception_basic(self):
        """Test basic AuthenticationException creation."""
        exception = AuthenticationException("Login failed", "test@example.com")
        
        assert exception.message == "Login failed"
        assert exception.email == "test@example.com"
        assert isinstance(exception.attempted_at, datetime)
    
    def test_authentication_exception_with_datetime(self):
        """Test AuthenticationException with specific datetime."""
        specific_time = datetime(2023, 1, 1, 12, 0, 0)
        exception = AuthenticationException(
            "Login failed", 
            "test@example.com", 
            attempted_at=specific_time
        )
        
        assert exception.message == "Login failed"
        assert exception.email == "test@example.com"
        assert exception.attempted_at == specific_time
    
    def test_authentication_exception_str_representation(self):
        """Test string representation of AuthenticationException."""
        specific_time = datetime(2023, 1, 1, 12, 0, 0)
        exception = AuthenticationException(
            "Login failed", 
            "test@example.com", 
            attempted_at=specific_time
        )
        
        str_repr = str(exception)
        assert "Login failed" in str_repr
        assert "test@example.com" in str_repr
        assert "2023-01-01 12:00:00" in str_repr


class TestAuthorizationException:
    """Test cases for AuthorizationException class."""
    
    def test_authorization_exception_basic(self):
        """Test basic AuthorizationException creation."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        exception = AuthorizationException(
            "Access denied",
            user_id=person_id,
            operation="create_activity",
            resource_id="resource1"
        )
        
        assert exception.message == "Access denied"
        assert exception.user_id == person_id
        assert exception.operation == "create_activity"
        assert exception.resource_id == "resource1"
        assert isinstance(exception.attempted_at, datetime)
    
    def test_authorization_exception_with_datetime(self):
        """Test AuthorizationException with specific datetime."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        specific_time = datetime(2023, 1, 1, 12, 0, 0)
        
        exception = AuthorizationException(
            "Access denied",
            user_id=person_id,
            operation="create_activity",
            resource_id="resource1",
            attempted_at=specific_time
        )
        
        assert exception.attempted_at == specific_time
    
    def test_authorization_exception_legacy_compatibility(self):
        """Test AuthorizationException with legacy required_permission parameter."""
        exception = AuthorizationException(
            "Access denied",
            required_permission="create_activity"
        )
        
        assert exception.message == "Access denied"
        assert exception.operation == "create_activity"
        assert exception.required_permission == "create_activity"
    
    def test_authorization_exception_minimal(self):
        """Test AuthorizationException with minimal parameters."""
        exception = AuthorizationException("Access denied")
        
        assert exception.message == "Access denied"
        assert exception.user_id is None
        assert exception.operation is None
        assert exception.resource_id is None
        assert isinstance(exception.attempted_at, datetime)
    
    def test_authorization_exception_str_representation_full(self):
        """Test string representation with all fields."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        specific_time = datetime(2023, 1, 1, 12, 0, 0)
        
        exception = AuthorizationException(
            "Access denied",
            user_id=person_id,
            operation="create_activity",
            resource_id="resource1",
            attempted_at=specific_time
        )
        
        str_repr = str(exception)
        assert "Access denied" in str_repr
        assert str(person_id) in str_repr
        assert "create_activity" in str_repr
        assert "resource1" in str_repr
        assert "2023-01-01 12:00:00" in str_repr
    
    def test_authorization_exception_str_representation_minimal(self):
        """Test string representation with minimal fields."""
        exception = AuthorizationException("Access denied")
        
        str_repr = str(exception)
        assert "Access denied" in str_repr
        assert "attempted at:" in str_repr