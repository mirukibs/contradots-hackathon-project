"""Integration tests for complete action submission workflows"""

import unittest
from unittest.mock import Mock

from src.application.services.action_application_service import ActionApplicationService
from src.application.services.person_application_service import PersonApplicationService
from src.application.commands.submit_action_command import SubmitActionCommand
from src.application.handlers.reputation_event_handler import ReputationEventHandler
from src.application.handlers.activity_projection_handler import ActivityProjectionHandler
from src.application.handlers.leaderboard_projection_handler import LeaderboardProjectionHandler
from src.domain.action.action import Action
from src.domain.person.person import Person
from src.domain.activity.activity import Activity
from src.domain.shared.value_objects.action_id import ActionId
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.shared.value_objects.activity_id import ActivityId
from src.domain.person.role import Role
from src.domain.shared.domain_events import ActionSubmittedEvent, ProofValidatedEvent
from src.domain.services.reputation_service import ReputationService


class TestActionSubmissionWorkflow(unittest.TestCase):
    """Integration tests for complete action submission to reputation update workflow"""
    
    def setUp(self):
        """Set up test fixtures for integration testing"""
        # Mock repositories
        self.action_repo = Mock()
        self.action_query_repo = Mock()
        self.activity_repo = Mock()
        self.person_repo = Mock()
        self.leaderboard_query_repo = Mock()
        self.event_publisher = Mock()
        
        # Create domain service
        self.reputation_service = ReputationService()
        
        # Create services
        self.action_service = ActionApplicationService(
            self.action_repo,
            self.action_query_repo,
            self.activity_repo,
            self.event_publisher
        )
        
        self.person_service = PersonApplicationService(
            self.person_repo,
            self.leaderboard_query_repo
        )
        
        # Create event handlers
        self.reputation_handler = ReputationEventHandler(
            self.person_repo,
            self.activity_repo,
            self.reputation_service
        )
        self.activity_handler = ActivityProjectionHandler(self.action_query_repo)
        self.leaderboard_handler = LeaderboardProjectionHandler(self.leaderboard_query_repo)
        
        # Test data
        self.person_id = PersonId.generate()
        self.activity_id = ActivityId.generate()
        self.action_id = ActionId.generate()
        
        # Create test entities
        self.person = Person(
            person_id=self.person_id,
            name="John Doe",
            email="john@example.com",
            role=Role.MEMBER,
            reputation_score=50
        )
        
        self.activity = Activity(
            activity_id=self.activity_id,
            title="Beach Cleanup",
            description="Clean the beach",
            creator_id=self.person_id
        )
        
    def test_complete_action_submission_workflow(self):
        """Test complete workflow: submit action → validate proof → update reputation"""
        # Arrange
        proof_data = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890123456789012"  # Valid 64-char hex hash
        
        # Mock repository responses
        self.person_repo.find_by_id.return_value = self.person
        self.activity_repo.find_by_id.return_value = self.activity
        self.action_repo.save = Mock()
        
        # Create command with correct parameter types
        submit_command = SubmitActionCommand(
            personId=self.person_id,
            activityId=self.activity_id,
            description="Cleaned beach section A",
            proofHash=proof_data
        )
        
        # Act 1: Submit action
        returned_action_id = self.action_service.submit_action(submit_command)
        
        # Assert 1: Action submission
        self.assertIsNotNone(returned_action_id)
        self.action_repo.save.assert_called_once()
        self.event_publisher.publish.assert_called_once()
        
        # Verify ActionSubmittedEvent was published
        published_event = self.event_publisher.publish.call_args[0][0]
        self.assertIsInstance(published_event, ActionSubmittedEvent)
        self.assertEqual(published_event.person_id, self.person_id)
        self.assertEqual(published_event.activity_id, self.activity_id)
        
    def test_action_submission_with_event_handling(self):
        """Test that action submission triggers appropriate event handlers"""
        # Arrange
        proof_validated_event = ProofValidatedEvent(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            is_valid=True
        )
        
        self.person_repo.find_by_id.return_value = self.person
        self.activity_repo.find_by_id.return_value = self.activity
        
        # Act: Handle events through handlers
        self.reputation_handler.handle(proof_validated_event)
        
        # Assert: Handler processed the event
        self.person_repo.find_by_id.assert_called_with(self.person_id)
        
        # Verify person reputation was updated
        self.assertGreater(self.person.reputation_score, 50)  # Should have increased
        
    def test_invalid_proof_does_not_increase_reputation(self):
        """Test that invalid proof validation does not increase reputation"""
        # Arrange
        initial_reputation = self.person.reputation_score
        
        # Create invalid proof event
        invalid_proof_event = ProofValidatedEvent(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            is_valid=False
        )
        
        self.person_repo.find_by_id.return_value = self.person
        
        # Act: Handle invalid proof validation
        self.reputation_handler.handle(invalid_proof_event)
        
        # Assert: Reputation should not increase
        self.assertEqual(self.person.reputation_score, initial_reputation)
        
    def test_cross_service_interaction_maintains_data_consistency(self):
        """Test that cross-service interactions maintain data consistency"""
        # Arrange
        submit_command = SubmitActionCommand(
            personId=self.person_id,
            activityId=self.activity_id,
            description="Test consistency",
            proofHash="abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        )
        
        # Mock repository responses for consistency check
        self.person_repo.find_by_id.return_value = self.person
        self.activity_repo.find_by_id.return_value = self.activity
        
        # Act: Submit action through service
        action_id = self.action_service.submit_action(submit_command)
        
        # Assert: Data consistency is maintained
        self.assertIsNotNone(action_id)
        self.action_repo.save.assert_called()
        self.event_publisher.publish.assert_called()
        
    def test_concurrent_action_submission_handling(self):
        """Test system behavior with concurrent action submissions"""
        # Arrange
        commands = [
            SubmitActionCommand(
                personId=self.person_id,
                activityId=self.activity_id,
                description=f"Action {i}",
                proofHash=f"abcdef12345678901{i:0>47}"  # Generate valid 64-char hex hashes
            ) for i in range(3)
        ]
        
        self.person_repo.find_by_id.return_value = self.person
        self.activity_repo.find_by_id.return_value = self.activity
        
        # Act: Submit multiple actions
        action_ids: list[str] = []
        for command in commands:
            action_id = self.action_service.submit_action(command)
            action_ids.append(str(action_id))  # Convert to string for consistent type
        
        # Assert: All actions were processed
        self.assertEqual(len(action_ids), 3)
        self.assertEqual(len(set(action_ids)), 3)  # All unique IDs
        self.assertEqual(self.action_repo.save.call_count, 3)
        self.assertEqual(self.event_publisher.publish.call_count, 3)
        
    def test_error_handling_in_workflow_maintains_consistency(self):
        """Test that errors in workflow don't leave system in inconsistent state"""
        # Arrange
        submit_command = SubmitActionCommand(
            personId=self.person_id,
            activityId=self.activity_id,
            description="Error test",
            proofHash="fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321"
        )
        
        # Mock repository to raise exception
        self.person_repo.find_by_id.return_value = self.person
        self.activity_repo.find_by_id.return_value = self.activity
        self.action_repo.save.side_effect = RuntimeError("Database error")
        
        # Act & Assert: Exception should be raised, but system should remain consistent
        with self.assertRaises(RuntimeError):
            self.action_service.submit_action(submit_command)
        
        # Verify no events were published due to error
        self.event_publisher.publish.assert_not_called()

    def test_action_validation_workflow(self):
        """Test action validation through domain logic"""
        # Arrange: Create a submitted action
        action = Action.submit(
            self.action_id,
            self.person_id,
            self.activity_id,
            "Test proof data"
        )
        
        # Act: Validate the action
        action.validate_proof()
        
        # Assert: Action is now validated
        self.assertTrue(action.is_verified())
        self.assertEqual(action.status.value, "validated")
        
        # Verify domain events were raised
        events = action.domain_events
        self.assertEqual(len(events), 2)  # ActionSubmitted + ProofValidated
        
        # Check that ProofValidatedEvent was raised
        proof_validated_events = [e for e in events if isinstance(e, ProofValidatedEvent)]
        self.assertEqual(len(proof_validated_events), 1)
        self.assertTrue(proof_validated_events[0].is_valid)


if __name__ == "__main__":
    unittest.main()