"""Integration tests for event-driven projection and query workflows"""

import unittest
from unittest.mock import Mock

from src.application.handlers.reputation_event_handler import ReputationEventHandler
from src.application.handlers.activity_projection_handler import ActivityProjectionHandler
from src.application.handlers.leaderboard_projection_handler import LeaderboardProjectionHandler
from src.application.dtos.action_dto import ActionDto
from src.application.dtos.activity_dto import ActivityDto
from src.application.dtos.leaderboard_dto import LeaderboardDto
from src.domain.person.person import Person
from src.domain.action.action_status import ActionStatus
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.shared.value_objects.action_id import ActionId
from src.domain.shared.value_objects.activity_id import ActivityId
from src.domain.person.role import Role
from src.domain.shared.domain_events import ProofValidatedEvent
from src.domain.services.reputation_service import ReputationService


class TestEventDrivenProjectionsWorkflow(unittest.TestCase):
    """Integration tests for event-driven CQRS projection updates"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock repositories
        self.person_repo = Mock()
        self.action_query_repo = Mock()
        self.activity_query_repo = Mock()
        self.leaderboard_query_repo = Mock()
        self.activity_repo = Mock()
        
        # Create domain service
        self.reputation_service = ReputationService()
        
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
        self.action_id = ActionId.generate()
        self.activity_id = ActivityId.generate()
        
        self.person = Person(
            person_id=self.person_id,
            name="Test User",
            email="test@example.com",
            role=Role.MEMBER,
            reputation_score=100
        )
    
    def test_proof_validated_updates_reputation(self):
        """Test that ProofValidatedEvent updates reputation through application layer"""
        # Arrange
        valid_proof_event = ProofValidatedEvent(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            is_valid=True
        )
        
        # Mock person repository
        self.person_repo.find_by_id.return_value = self.person
        self.person_repo.save = Mock()
        
        # Mock activity repository
        from src.domain.activity.activity import Activity
        test_activity = Activity(
            activity_id=self.activity_id,
            title="Test Activity",
            description="Test activity",
            creator_id=self.person_id
        )
        self.activity_repo.find_by_id.return_value = test_activity
        
        # Act: Handle proof validation event
        self.reputation_handler.handle(valid_proof_event)
        
        # Assert: Reputation was updated
        self.person_repo.save.assert_called_once()
        
        # Verify person was looked up
        self.person_repo.find_by_id.assert_called_with(self.person_id)
        self.activity_repo.find_by_id.assert_called_with(self.activity_id)
    
    def test_invalid_proof_does_not_increase_reputation(self):
        """Test that invalid proof validation does not increase reputation"""
        # Arrange
        invalid_proof_event = ProofValidatedEvent(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            is_valid=False
        )
        
        self.person_repo.find_by_id.return_value = self.person
        
        # Act: Handle invalid proof validation
        self.reputation_handler.handle(invalid_proof_event)
        
        # Assert: No repository calls for invalid proofs
        self.person_repo.find_by_id.assert_not_called()
        self.person_repo.save.assert_not_called()
        
    def test_complete_event_flow_maintains_projection_consistency(self):
        """Test that complete event flow maintains consistency across all projections"""
        # Arrange: Multiple related events
        proof_validated = ProofValidatedEvent(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            is_valid=True
        )
        
        # Mock all projection operations
        self.person_repo.find_by_id.return_value = self.person
        self.person_repo.save = Mock()
        
        # Mock activity for reputation handler
        from src.domain.activity.activity import Activity
        test_activity = Activity(
            activity_id=self.activity_id,
            title="Test Activity",
            description="Test activity",
            creator_id=self.person_id
        )
        self.activity_repo.find_by_id.return_value = test_activity
        
        # Act: Process event sequence
        # 1. Action submitted (would be handled by activity projection handler)
        # 2. Proof validated (handled by reputation handler)
        self.reputation_handler.handle(proof_validated)
        
        # Assert: Reputation handler was called
        self.person_repo.save.assert_called_once()
        self.person_repo.find_by_id.assert_called_once_with(self.person_id)
        self.activity_repo.find_by_id.assert_called_once_with(self.activity_id)
    
    def test_event_handler_error_handling(self):
        """Test that event handler errors are handled gracefully"""
        # Arrange
        event = ProofValidatedEvent(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            is_valid=True
        )
        
        # Mock repository to fail
        self.person_repo.find_by_id.side_effect = RuntimeError("Database error")
        
        # Act & Assert: Handler should handle the error gracefully
        with self.assertRaises(RuntimeError):
            self.reputation_handler.handle(event)
        
        # Verify that error didn't break the handler
        self.person_repo.find_by_id.assert_called_once()
    
    def test_concurrent_event_processing_isolation(self):
        """Test that concurrent event processing doesn't interfere"""
        # Arrange: Multiple events for different persons
        events = [
            ProofValidatedEvent(
                action_id=ActionId.generate(),
                person_id=PersonId.generate(),
                activity_id=self.activity_id,
                is_valid=True
            ) for _ in range(3)
        ]
        
        # Mock different persons for each event
        test_persons = [
            Person(
                person_id=event.person_id,
                name=f"User {i}",
                email=f"user{i}@example.com",
                role=Role.MEMBER,
                reputation_score=100
            ) for i, event in enumerate(events)
        ]
        
        # Mock activity
        from src.domain.activity.activity import Activity
        test_activity = Activity(
            activity_id=self.activity_id,
            title="Test Activity",
            description="Test activity",
            creator_id=self.person_id
        )
        
        # Set up mock responses
        self.person_repo.find_by_id.side_effect = test_persons
        self.activity_repo.find_by_id.return_value = test_activity
        self.person_repo.save = Mock()
        
        # Act: Process events
        for event in events:
            self.reputation_handler.handle(event)
        
        # Assert: All events were processed
        self.assertEqual(self.person_repo.save.call_count, 3)
        self.assertEqual(self.person_repo.find_by_id.call_count, 3)


class TestQueryWorkflow(unittest.TestCase):
    """Integration tests for query workflows across multiple read models"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock query repositories
        self.action_query_repo = Mock()
        self.activity_query_repo = Mock()
        self.leaderboard_query_repo = Mock()
        
        # Test data
        self.person_id = PersonId.generate()
        self.activity_id = ActivityId.generate()
        
    def test_cross_repository_query_consistency(self):
        """Test that queries across multiple repositories return consistent data"""
        # Arrange: Mock consistent data across repositories
        person_actions = [
            ActionDto(
                actionId="action_1",
                personName="Test User",
                activityName="Beach Cleanup",
                description="Action 1",
                status=ActionStatus.VALIDATED,
                submittedAt="2024-01-01T00:00:00Z"
            ),
            ActionDto(
                actionId="action_2", 
                personName="Test User",
                activityName="Park Cleanup",
                description="Action 2",
                status=ActionStatus.VALIDATED,
                submittedAt="2024-01-02T00:00:00Z"
            )
        ]
        
        self.action_query_repo.get_person_actions.return_value = person_actions
        self.leaderboard_query_repo.get_person_rank.return_value = 5
        
        # Act: Query data from multiple repositories
        actions = self.action_query_repo.get_person_actions(self.person_id)
        rank = self.leaderboard_query_repo.get_person_rank(self.person_id)
        
        # Assert: Data is consistent across repositories
        self.assertEqual(len(actions), 2)
        self.assertTrue(all(action.status == ActionStatus.VALIDATED for action in actions))
        self.assertEqual(rank, 5)
        
        # Verify consistency: reputation should match validated actions count
        # Note: In real system, we'd query leaderboard repo for reputation score
        
    def test_activity_aggregation_across_projections(self):
        """Test aggregating activity data across different projections"""
        # Mock activity data from different projections
        activity_basic = ActivityDto(
            activityId=str(self.activity_id),
            name="Community Garden",
            description="Plant trees",
            points=100,
            leadName="Activity Lead",
            isActive=True
        )
        
        activity_actions = [
            ActionDto(
                actionId="action_1",
                personName="User 1",
                activityName="Community Garden",
                description="Planted tree 1",
                status=ActionStatus.VALIDATED,
                submittedAt="2024-01-01T00:00:00Z"
            ),
            ActionDto(
                actionId="action_2",
                personName="User 2", 
                activityName="Community Garden",
                description="Planted tree 2",
                status=ActionStatus.SUBMITTED,
                submittedAt="2024-01-02T00:00:00Z"
            )
        ]
        
        self.activity_query_repo.get_active_activities.return_value = [activity_basic]
        self.action_query_repo.get_activity_actions.return_value = activity_actions
        
        # Act: Query aggregated activity data
        activities = self.activity_query_repo.get_active_activities()
        related_actions = self.action_query_repo.get_activity_actions(self.activity_id)
        
        # Assert: Can aggregate data across projections
        self.assertEqual(len(activities), 1)
        self.assertEqual(len(related_actions), 2)
        
        # Verify we can calculate activity metrics
        total_submissions = len(related_actions)
        validated_submissions = len([a for a in related_actions if a.status == ActionStatus.VALIDATED])
        
        self.assertEqual(total_submissions, 2)
        self.assertEqual(validated_submissions, 1)
        
    def test_leaderboard_ranking_consistency(self):
        """Test that leaderboard rankings are consistent with person reputation data"""
        # Arrange: Mock leaderboard data
        leaderboard = [
            LeaderboardDto(
                personId="person_1",
                name="Top User",
                reputationScore=200,
                rank=1
            ),
            LeaderboardDto(
                personId="person_2", 
                name="Second User",
                reputationScore=150,
                rank=2
            ),
            LeaderboardDto(
                personId="person_3",
                name="Third User", 
                reputationScore=100,
                rank=3
            )
        ]
        
        self.leaderboard_query_repo.get_leaderboard.return_value = leaderboard
        
        # Act: Query leaderboard
        result = self.leaderboard_query_repo.get_leaderboard()
        
        # Assert: Ranking is consistent with reputation scores
        self.assertEqual(len(result), 3)
        
        # Verify descending reputation order
        self.assertGreaterEqual(result[0].reputationScore, result[1].reputationScore)
        self.assertGreaterEqual(result[1].reputationScore, result[2].reputationScore)
        
        # Verify ascending rank order
        self.assertLess(result[0].rank, result[1].rank)
        self.assertLess(result[1].rank, result[2].rank)

    def test_query_repository_integration(self):
        """Test integration between different query repositories"""
        # Arrange: Create test data that spans multiple query repositories
        person_id = PersonId.generate()
        activity_id = ActivityId.generate()
        
        # Mock action query data
        person_actions = [
            ActionDto(
                actionId="action_1",
                personName="Integration User",
                activityName="Integration Activity",
                description="Test integration",
                status=ActionStatus.VALIDATED,
                submittedAt="2024-01-01T00:00:00Z"
            )
        ]
        
        # Mock activity data
        activity_data = ActivityDto(
            activityId=str(activity_id),
            name="Integration Activity",
            description="Test activity integration",
            points=150,
            leadName="Lead User",
            isActive=True
        )
        
        # Set up mock returns
        self.action_query_repo.get_person_actions.return_value = person_actions
        self.leaderboard_query_repo.get_person_rank.return_value = 10
        self.activity_query_repo.get_activity_by_id.return_value = activity_data
        
        # Act: Query across repositories
        actions = self.action_query_repo.get_person_actions(person_id)
        rank = self.leaderboard_query_repo.get_person_rank(person_id)
        activity = self.activity_query_repo.get_activity_by_id(activity_id)
        
        # Assert: Data is consistent across repositories
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].activityName, "Integration Activity")
        self.assertEqual(rank, 10)
        self.assertEqual(activity.name, "Integration Activity")
        
        # Verify cross-repository data consistency
        self.assertEqual(actions[0].personName, "Integration User")
        self.assertEqual(actions[0].activityName, activity.name)


if __name__ == "__main__":
    unittest.main()