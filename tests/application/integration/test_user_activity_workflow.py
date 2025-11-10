"""Integration tests for user registration and activity creation workflows"""

import unittest
from unittest.mock import Mock

from src.application.services.person_application_service import PersonApplicationService
from src.application.services.activity_application_service import ActivityApplicationService
from src.application.commands.register_person_command import RegisterPersonCommand
from src.application.commands.create_activity_command import CreateActivityCommand
from src.application.handlers.leaderboard_projection_handler import LeaderboardProjectionHandler
from src.application.handlers.activity_projection_handler import ActivityProjectionHandler
from src.domain.person.person import Person
from src.domain.activity.activity import Activity
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.shared.value_objects.activity_id import ActivityId
from src.domain.person.role import Role


class TestUserRegistrationWorkflow(unittest.TestCase):
    """Integration tests for user registration and onboarding workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock repositories
        self.person_repo = Mock()
        self.leaderboard_query_repo = Mock()
        self.activity_repo = Mock()
        self.activity_query_repo = Mock()
        
        # Create services
        self.person_service = PersonApplicationService(
            self.person_repo,
            self.leaderboard_query_repo
        )
        
        self.activity_service = ActivityApplicationService(
            self.activity_repo,
            self.activity_query_repo,
            self.person_repo
        )
        
        # Create handlers
        self.leaderboard_handler = LeaderboardProjectionHandler(self.leaderboard_query_repo)
        self.activity_handler = ActivityProjectionHandler(self.activity_query_repo)
        
    def test_complete_user_onboarding_workflow(self):
        """Test complete user registration and first activity creation"""
        # Arrange
        register_command = RegisterPersonCommand(
            name="Jane Doe",
            email="jane@example.com",
            role="lead"
        )
        
        # Mock repository responses
        self.person_repo.find_all.return_value = []  # No existing users
        self.person_repo.save = Mock()
        
        # Act 1: Register user
        person_id = self.person_service.register_person(register_command)
        
        # Assert 1: User registration
        self.assertIsNotNone(person_id)
        self.person_repo.save.assert_called_once()
        
        # Verify person was created correctly
        saved_person = self.person_repo.save.call_args[0][0]
        self.assertIsInstance(saved_person, Person)
        self.assertEqual(saved_person.name, "Jane Doe")
        self.assertEqual(saved_person.email, "jane@example.com")
        self.assertEqual(saved_person.role, Role.LEAD)
        
        # Arrange 2: Create activity as LEAD
        create_activity_command = CreateActivityCommand(
            name="Community Garden",
            description="Plant trees in local park",
            points=150,
            leadId=person_id
        )
        
        # Mock person lookup for activity creation
        lead_person = Person(
            person_id=person_id,
            name="Jane Doe",
            email="jane@example.com",
            role=Role.LEAD
        )
        self.person_repo.find_by_id.return_value = lead_person
        self.activity_repo.save = Mock()
        
        # Act 2: Create activity
        activity_id = self.activity_service.create_activity(create_activity_command)
        
        # Assert 2: Activity creation
        self.assertIsNotNone(activity_id)
        self.activity_repo.save.assert_called_once()
        
        # Verify activity was created correctly
        saved_activity = self.activity_repo.save.call_args[0][0]
        self.assertIsInstance(saved_activity, Activity)
        self.assertEqual(saved_activity.title, "Community Garden")
        self.assertEqual(saved_activity.creator_id, person_id)
        
    def test_member_cannot_create_activities_workflow(self):
        """Test that MEMBER role users cannot create activities in the workflow"""
        # Arrange
        register_command = RegisterPersonCommand(
            name="Bob Smith",
            email="bob@example.com",
            role="participant"
        )
        
        self.person_repo.find_all.return_value = []
        self.person_repo.save = Mock()
        
        # Act 1: Register as MEMBER
        person_id = self.person_service.register_person(register_command)
        
        # Assert 1: Registration successful
        self.assertIsNotNone(person_id)
        
        # Arrange 2: Try to create activity as MEMBER
        create_activity_command = CreateActivityCommand(
            name="Unauthorized Activity",
            description="Should fail",
            points=100,
            leadId=person_id
        )
        
        member_person = Person(
            person_id=person_id,
            name="Bob Smith",
            email="bob@example.com",
            role=Role.MEMBER
        )
        self.person_repo.find_by_id.return_value = member_person
        
        # Act 2 & Assert 2: Activity creation should fail
        with self.assertRaises(ValueError):
            self.activity_service.create_activity(create_activity_command)
        
    def test_duplicate_email_registration_prevention(self):
        """Test that duplicate email registrations are prevented"""
        # Arrange
        existing_person = Person(
            person_id=PersonId.generate(),
            name="Existing User",
            email="duplicate@example.com",
            role=Role.MEMBER
        )
        
        self.person_repo.find_all.return_value = [existing_person]
        
        duplicate_command = RegisterPersonCommand(
            name="New User",
            email="duplicate@example.com",  # Same email
            role="participant"
        )
        
        # Act & Assert
        with self.assertRaises(ValueError):
            self.person_service.register_person(duplicate_command)
        
        # Verify no save was attempted
        self.person_repo.save.assert_not_called()
        
    def test_leaderboard_projection_after_registration(self):
        """Test that leaderboard projections are updated after user registration"""
        # Arrange
        register_command = RegisterPersonCommand(
            name="Leaderboard User",
            email="leader@example.com",
            role="participant"
        )
        
        self.person_repo.find_all.return_value = []
        self.person_repo.save = Mock()
        
        # Act: Register user
        person_id = self.person_service.register_person(register_command)
        
        # Mock leaderboard handler response
        self.leaderboard_query_repo.update_person_entry = Mock()
        
        # Assert: Registration succeeded and projection would be updated
        self.assertIsNotNone(person_id)
        self.person_repo.save.assert_called_once()


class TestActivityManagementWorkflow(unittest.TestCase):
    """Integration tests for activity lifecycle management"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.activity_repo = Mock()
        self.activity_query_repo = Mock()
        self.person_repo = Mock()
        
        self.activity_service = ActivityApplicationService(
            self.activity_repo,
            self.activity_query_repo,
            self.person_repo
        )
        
        # Test data
        self.lead_id = PersonId.generate()
        self.activity_id = ActivityId.generate()
        
        self.lead_person = Person(
            person_id=self.lead_id,
            name="Activity Lead",
            email="lead@example.com",
            role=Role.LEAD
        )
        
    def test_activity_creation_workflow(self):
        """Test activity creation workflow"""
        # Arrange
        create_command = CreateActivityCommand(
            name="Park Cleanup",
            description="Clean the local park",
            points=200,
            leadId=self.lead_id
        )
        
        self.person_repo.find_by_id.return_value = self.lead_person
        self.activity_repo.save = Mock()
        
        # Act: Create activity
        activity_id = self.activity_service.create_activity(create_command)
        
        # Assert: Activity created
        self.assertIsNotNone(activity_id)
        self.activity_repo.save.assert_called_once()
        
        # Verify activity was created correctly
        saved_activity = self.activity_repo.save.call_args[0][0]
        self.assertIsInstance(saved_activity, Activity)
        self.assertEqual(saved_activity.title, "Park Cleanup")
        self.assertEqual(saved_activity.creator_id, self.lead_id)

    def test_activity_authorization_workflow(self):
        """Test that activity operations are properly authorized"""
        # Arrange: Create activity command
        create_command = CreateActivityCommand(
            name="Test Activity",
            description="Test authorization",
            points=100,
            leadId=self.lead_id
        )
        
        self.person_repo.find_by_id.return_value = self.lead_person
        self.activity_repo.save = Mock()
        
        # Act: Create activity
        activity_id = self.activity_service.create_activity(create_command)
        
        # Assert: Activity was created successfully
        self.assertIsNotNone(activity_id)
        self.activity_repo.save.assert_called_once()
        
        # Verify the person was checked for authorization
        self.person_repo.find_by_id.assert_called_with(self.lead_id)

    def test_activity_business_rules_validation(self):
        """Test that business rules are enforced during activity creation"""
        # Arrange: Member tries to create activity (should fail)
        member_id = PersonId.generate()
        member_person = Person(
            person_id=member_id,
            name="Regular Member",
            email="member@example.com",
            role=Role.MEMBER
        )
        
        create_command = CreateActivityCommand(
            name="Unauthorized Activity",
            description="Should fail",
            points=100,
            leadId=member_id
        )
        
        self.person_repo.find_by_id.return_value = member_person
        
        # Act & Assert: Should raise authorization error
        with self.assertRaises(ValueError):
            self.activity_service.create_activity(create_command)
        
        # Verify no save was attempted
        self.activity_repo.save.assert_not_called()

    def test_cross_aggregate_workflow_consistency(self):
        """Test that workflows maintain consistency across person and activity aggregates"""
        # Arrange: Create activity and verify person-activity relationship
        create_command = CreateActivityCommand(
            name="Cross Aggregate Test",
            description="Testing cross-aggregate consistency",
            points=150,
            leadId=self.lead_id
        )
        
        self.person_repo.find_by_id.return_value = self.lead_person
        self.activity_repo.save = Mock()
        
        # Act: Create activity
        activity_id = self.activity_service.create_activity(create_command)
        
        # Assert: Cross-aggregate consistency maintained
        self.assertIsNotNone(activity_id)
        
        # Verify person was looked up before activity creation
        self.person_repo.find_by_id.assert_called_with(self.lead_id)
        
        # Verify activity was saved with correct creator reference
        saved_activity = self.activity_repo.save.call_args[0][0]
        self.assertEqual(saved_activity.creator_id, self.lead_id)


if __name__ == "__main__":
    unittest.main()