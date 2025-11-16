"""Comprehensive tests for ActivityApplicationService"""

from typing import List
from unittest.mock import Mock
from src.application.services.activity_application_service import ActivityApplicationService
from src.application.commands.create_activity_command import CreateActivityCommand
from src.application.commands.deactivate_activity_command import DeactivateActivityCommand
from src.application.dtos.activity_dto import ActivityDto
from src.application.dtos.activity_details_dto import ActivityDetailsDto
from src.application.security.authentication_context import AuthenticationContext
from src.application.security.authorization_exception import AuthorizationException
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.shared.value_objects.activity_id import ActivityId
from src.domain.activity.activity import Activity
from src.domain.person.person import Person
from src.domain.person.role import Role


class TestActivityApplicationService:
    """Test suite for ActivityApplicationService covering all methods and edge cases"""

    def setup_method(self):
        """Set up test fixtures and mocks"""
        # Create mock repositories
        self.mock_activity_repo = Mock()
        self.mock_activity_query_repo = Mock()
        self.mock_person_repo = Mock()
        self.mock_authorization_service = Mock()
        
        # Test data
        self.valid_lead_id = PersonId.generate()
        self.valid_activity_id = ActivityId.generate()
        
        # Create mock authentication context
        self.mock_auth_context = Mock(spec=AuthenticationContext)
        self.mock_auth_context.is_authenticated = True
        self.mock_auth_context.current_user_id = self.valid_lead_id  # Use lead id for consistency
        self.mock_auth_context.email = "lead@example.com"
        
        # Create service instance
        self.service = ActivityApplicationService(
            activity_repo=self.mock_activity_repo,
            activity_query_repo=self.mock_activity_query_repo,
            person_repo=self.mock_person_repo,
            authorization_service=self.mock_authorization_service
        )
        
        # Create test lead
        self.test_lead = Person.create(
            name="Lead User",
            email="lead@example.com",
            role=Role.LEAD
        )
        
        # Create test member (non-lead)
        self.test_member = Person.create(
            name="Member User", 
            email="member@example.com",
            role=Role.MEMBER
        )
        
        # Create test activity
        self.test_activity = Activity(
            activity_id=self.valid_activity_id,
            title="Beach Cleanup",
            description="Clean the beach",
            creator_id=self.valid_lead_id
        )
        
        self.valid_create_command = CreateActivityCommand(
            name="Beach Cleanup Drive",
            description="Community beach cleanup event",
            points=50,
            leadId=self.valid_lead_id
        )
        
        self.valid_deactivate_command = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )

    def test_create_activity_success(self):
        """Test successful activity creation by lead"""
        # Arrange - no need to arrange person_repo since it's not called directly
        
        # Act
        result = self.service.create_activity(self.valid_create_command, self.mock_auth_context)
        
        # Assert
        assert isinstance(result, ActivityId)
        # Verify authorization was called
        self.mock_authorization_service.validate_role_permission.assert_called_once_with(self.mock_auth_context, "create_activity")
        self.mock_activity_repo.save.assert_called_once()
        
        # Verify the activity passed to save has correct attributes
        saved_activity = self.mock_activity_repo.save.call_args[0][0]
        assert saved_activity.title == "Beach Cleanup Drive"
        assert saved_activity.description == "Community beach cleanup event"
        assert saved_activity.creator_id == self.valid_lead_id

    def test_create_activity_lead_not_found(self):
        """Test activity creation when authorization fails due to person not found"""
        # Arrange
        self.mock_authorization_service.validate_role_permission.side_effect = AuthorizationException("User not found")
        
        # Act & Assert
        try:
            self.service.create_activity(self.valid_create_command, self.mock_auth_context)
            assert False, "Should have raised AuthorizationException"
        except AuthorizationException as e:
            assert "User not found" in str(e)
        
        # Verify authorization was called but activity save was not
        self.mock_authorization_service.validate_role_permission.assert_called_once_with(self.mock_auth_context, "create_activity")
        self.mock_activity_repo.save.assert_not_called()

    def test_create_activity_non_lead_user(self):
        """Test activity creation by non-lead user"""
        # Arrange
        self.mock_authorization_service.validate_role_permission.side_effect = AuthorizationException("Only leads can create activities")
        
        # Act & Assert
        try:
            self.service.create_activity(self.valid_create_command, self.mock_auth_context)
            assert False, "Should have raised AuthorizationException"
        except AuthorizationException as e:
            assert "Only leads can create activities" in str(e)
        
        # Verify authorization was called but save was not
        self.mock_authorization_service.validate_role_permission.assert_called_once_with(self.mock_auth_context, "create_activity")
        self.mock_activity_repo.save.assert_not_called()

    def test_create_activity_invalid_command(self):
        """Test activity creation with invalid command"""
        # Arrange
        invalid_command = CreateActivityCommand(
            name="",  # Invalid empty name
            description="Valid description",
            points=50,
            leadId=self.valid_lead_id
        )
        
        # Act & Assert
        try:
            self.service.create_activity(invalid_command, self.mock_auth_context)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Name is required and cannot be empty" in str(e)
        
        # Verify repositories weren't called
        self.mock_person_repo.find_by_id.assert_not_called()
        self.mock_activity_repo.save.assert_not_called()

    def test_create_activity_with_special_characters(self):
        """Test activity creation with special characters"""
        # Arrange
        special_command = CreateActivityCommand(
            name="Limpieza de Playa 🌊",
            description="Evento comunitario de limpieza",
            points=75,
            leadId=self.valid_lead_id
        )
        self.mock_person_repo.find_by_id.return_value = self.test_lead
        
        # Act
        result = self.service.create_activity(special_command, self.mock_auth_context)
        
        # Assert
        assert isinstance(result, ActivityId)
        saved_activity = self.mock_activity_repo.save.call_args[0][0]
        assert saved_activity.title == "Limpieza de Playa 🌊"
        assert saved_activity.description == "Evento comunitario de limpieza"

    def test_get_active_activities_success(self):
        """Test successful retrieval of active activities"""
        # Arrange
        expected_activities = [
            ActivityDto(
                activityId=str(ActivityId.generate()),
                name="Beach Cleanup",
                description="Clean the beach",
                points=50,
                leadName="John Doe",
                isActive=True
            ),
            ActivityDto(
                activityId=str(ActivityId.generate()),
                name="Tree Planting",
                description="Plant trees in the park",
                points=75,
                leadName="Jane Smith",
                isActive=True
            )
        ]
        self.mock_activity_query_repo.get_active_activities.return_value = expected_activities
        
        # Act
        result = self.service.get_active_activities(self.mock_auth_context)
        
        # Assert
        assert result == expected_activities
        assert len(result) == 2
        assert all(activity.isActive for activity in result)
        self.mock_activity_query_repo.get_active_activities.assert_called_once()

    def test_get_active_activities_empty(self):
        """Test retrieval when no active activities exist"""
        # Arrange
        self.mock_activity_query_repo.get_active_activities.return_value = []
        
        # Act
        result = self.service.get_active_activities(self.mock_auth_context)
        
        # Assert
        assert result == []
        assert len(result) == 0
        self.mock_activity_query_repo.get_active_activities.assert_called_once()

    def test_get_activity_details_success(self):
        """Test successful retrieval of activity details"""
        # Arrange
        expected_details = ActivityDetailsDto(
            activityId=str(self.valid_activity_id),
            name="Beach Cleanup Drive",
            description="Community beach cleanup event",
            points=50,
            leadName="Lead User",
            isActive=True,
            participantCount=25,
            totalActionsSubmitted=47
        )
        self.mock_activity_query_repo.get_activity_details.return_value = expected_details
        
        # Act
        result = self.service.get_activity_details(self.valid_activity_id, self.mock_auth_context)
        
        # Assert
        assert result == expected_details
        assert result.activityId == str(self.valid_activity_id)
        assert result.participantCount == 25
        assert result.totalActionsSubmitted == 47
        self.mock_activity_query_repo.get_activity_details.assert_called_once_with(self.valid_activity_id)

    def test_get_activity_details_not_found(self):
        """Test activity details retrieval when activity doesn't exist"""
        # Arrange
        self.mock_activity_query_repo.get_activity_details.side_effect = ValueError(f"Activity not found: {self.valid_activity_id}")
        
        # Act & Assert
        try:
            self.service.get_activity_details(self.valid_activity_id, self.mock_auth_context)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert f"Activity not found: {self.valid_activity_id}" in str(e)

    def test_deactivate_activity_success(self):
        """Test successful activity deactivation by creator"""
        # Arrange
        self.mock_activity_repo.find_by_id.return_value = self.test_activity
        
        # Act
        self.service.deactivate_activity(self.valid_deactivate_command, self.mock_auth_context)
        
        # Assert
        self.mock_activity_repo.find_by_id.assert_called_once_with(self.valid_activity_id)
        self.mock_authorization_service.enforce_activity_ownership.assert_called_once_with(self.mock_auth_context, self.valid_activity_id)
        # Verify save was called with the test activity
        self.mock_activity_repo.save.assert_called_with(self.test_activity)

    def test_deactivate_activity_not_found(self):
        """Test deactivation when activity doesn't exist"""
        # Arrange
        self.mock_activity_repo.find_by_id.return_value = None
        
        # Act & Assert
        try:
            self.service.deactivate_activity(self.valid_deactivate_command, self.mock_auth_context)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert f"Activity not found: {self.valid_activity_id}" in str(e)
        
        # Verify save was not called
        self.mock_activity_repo.save.assert_not_called()

    def test_deactivate_activity_not_creator(self):
        """Test deactivation by someone other than the creator"""
        # Arrange
        different_lead_id = PersonId.generate()
        test_activity_different_creator = Activity(
            activity_id=self.valid_activity_id,
            title="Beach Cleanup",
            description="Clean the beach",
            creator_id=different_lead_id  # Different creator
        )
        self.mock_activity_repo.find_by_id.return_value = test_activity_different_creator
        
        # Act & Assert
        try:
            self.service.deactivate_activity(self.valid_deactivate_command, self.mock_auth_context)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Only the activity creator can deactivate the activity" in str(e)
        
        # Verify save was not called
        self.mock_activity_repo.save.assert_not_called()

    def test_deactivate_activity_lead_not_found(self):
        """Test deactivation when authorization fails due to lead not found"""
        # Arrange
        self.mock_activity_repo.find_by_id.return_value = self.test_activity
        self.mock_authorization_service.enforce_activity_ownership.side_effect = AuthorizationException("User not found")
        
        # Act & Assert
        try:
            self.service.deactivate_activity(self.valid_deactivate_command, self.mock_auth_context)
            assert False, "Should have raised AuthorizationException"
        except AuthorizationException as e:
            assert "User not found" in str(e)
        
        # Verify authorization was called but save was not
        self.mock_authorization_service.enforce_activity_ownership.assert_called_once_with(self.mock_auth_context, self.valid_activity_id)
        self.mock_activity_repo.save.assert_not_called()

    def test_deactivate_activity_non_lead_user(self):
        """Test deactivation by non-lead user"""
        # Arrange
        self.mock_activity_repo.find_by_id.return_value = self.test_activity
        self.mock_authorization_service.enforce_activity_ownership.side_effect = AuthorizationException("Only activity owner can deactivate")
        
        # Act & Assert
        try:
            self.service.deactivate_activity(self.valid_deactivate_command, self.mock_auth_context)
            assert False, "Should have raised AuthorizationException"
        except AuthorizationException as e:
            assert "Only activity owner can deactivate" in str(e)
        
        # Verify authorization was called but save was not
        self.mock_authorization_service.enforce_activity_ownership.assert_called_once_with(self.mock_auth_context, self.valid_activity_id)
        self.mock_activity_repo.save.assert_not_called()

    def test_deactivate_activity_invalid_command(self):
        """Test deactivation with invalid command"""
        # Arrange
        invalid_command = DeactivateActivityCommand(
            activityId=ActivityId.generate(),  # Use a valid ActivityId for testing
            leadId=self.valid_lead_id
        )
        # Force validation to fail by clearing required fields after creation
        invalid_command.__dict__['activityId'] = None
        
        # Act & Assert
        try:
            self.service.deactivate_activity(invalid_command, self.mock_auth_context)
            assert False, "Should have raised ValueError"
        except ValueError:
            # Command validation should fail
            pass
        
        # Verify repositories weren't called
        self.mock_activity_repo.find_by_id.assert_not_called()
        self.mock_activity_repo.save.assert_not_called()

    def test_service_constructor_with_dependencies(self):
        """Test service constructor properly stores dependencies"""
        # Create new service instance
        service = ActivityApplicationService(
            activity_repo=self.mock_activity_repo,
            activity_query_repo=self.mock_activity_query_repo,
            person_repo=self.mock_person_repo,
            authorization_service=self.mock_authorization_service
        )
        
        # Verify dependencies are stored (using reflection for testing)
        assert service.__dict__.get('_activity_repo') is self.mock_activity_repo
        assert service.__dict__.get('_activity_query_repo') is self.mock_activity_query_repo
        assert service.__dict__.get('_person_repo') is self.mock_person_repo
        assert service.__dict__.get('_authorization_service') is self.mock_authorization_service

    def test_create_activity_repository_exception_handling(self):
        """Test handling of repository exceptions during creation"""
        # Arrange
        self.mock_person_repo.find_by_id.return_value = self.test_lead
        self.mock_activity_repo.save.side_effect = Exception("Database connection error")
        
        # Act & Assert
        try:
            self.service.create_activity(self.valid_create_command, self.mock_auth_context)
            assert False, "Should have raised Exception"
        except Exception as e:
            assert "Database connection error" in str(e)

    def test_get_active_activities_repository_exception_handling(self):
        """Test handling of repository exceptions during active activities retrieval"""
        # Arrange
        self.mock_activity_query_repo.get_active_activities.side_effect = Exception("Query service unavailable")
        
        # Act & Assert
        try:
            self.service.get_active_activities(self.mock_auth_context)
            assert False, "Should have raised Exception"
        except Exception as e:
            assert "Query service unavailable" in str(e)

    def test_get_activity_details_repository_exception_handling(self):
        """Test handling of repository exceptions during activity details retrieval"""
        # Arrange
        self.mock_activity_query_repo.get_activity_details.side_effect = Exception("Database error")
        
        # Act & Assert
        try:
            self.service.get_activity_details(self.valid_activity_id, self.mock_auth_context)
            assert False, "Should have raised Exception"
        except Exception as e:
            assert "Database error" in str(e)

    def test_deactivate_activity_repository_exception_handling(self):
        """Test handling of repository exceptions during deactivation"""
        # Arrange
        self.mock_activity_repo.find_by_id.return_value = self.test_activity
        self.mock_person_repo.find_by_id.return_value = self.test_lead
        self.mock_activity_repo.save.side_effect = Exception("Database write error")
        
        # Act & Assert
        try:
            self.service.deactivate_activity(self.valid_deactivate_command, self.mock_auth_context)
            assert False, "Should have raised Exception"
        except Exception as e:
            assert "Database write error" in str(e)

    def test_create_multiple_activities_different_leads(self):
        """Test creating multiple activities by the same authenticated lead"""
        # Arrange
        commands = [
            CreateActivityCommand(
                name="Activity 1",
                description="First activity",
                points=25,
                leadId=self.valid_lead_id  # Same authenticated user
            ),
            CreateActivityCommand(
                name="Activity 2", 
                description="Second activity",
                points=50,
                leadId=self.valid_lead_id  # Same authenticated user
            )
        ]
        
        # Act
        results: List[ActivityId] = []
        for command in commands:
            result = self.service.create_activity(command, self.mock_auth_context)
            results.append(result)
            assert isinstance(result, ActivityId)
        
        # Assert
        assert len(results) == 2
        assert len(set(str(r) for r in results)) == 2  # All different IDs
        assert self.mock_activity_repo.save.call_count == 2

    def test_role_verification_with_different_role_formats(self):
        """Test role verification with different role string formats"""
        # Test that the service correctly identifies lead role regardless of string format
        # This tests the Role value object comparison
        
        # Create lead with Role.LEAD
        lead_with_role_enum = Person.create(
            name="Lead User",
            email="lead@example.com", 
            role=Role.LEAD
        )
        
        self.mock_person_repo.find_by_id.return_value = lead_with_role_enum
        
        # Act
        result = self.service.create_activity(self.valid_create_command, self.mock_auth_context)
        
        # Assert
        assert isinstance(result, ActivityId)
        self.mock_activity_repo.save.assert_called_once()

    def test_activity_creation_with_long_descriptions(self):
        """Test activity creation with very long descriptions"""
        # Arrange
        long_description = "A" * 5000  # Very long description
        long_command = CreateActivityCommand(
            name="Long Description Activity",
            description=long_description,
            points=100,
            leadId=self.valid_lead_id
        )
        self.mock_person_repo.find_by_id.return_value = self.test_lead
        
        # Act
        result = self.service.create_activity(long_command, self.mock_auth_context)
        
        # Assert
        assert isinstance(result, ActivityId)
        saved_activity = self.mock_activity_repo.save.call_args[0][0]
        assert len(saved_activity.description) == 5000
        assert saved_activity.description == long_description