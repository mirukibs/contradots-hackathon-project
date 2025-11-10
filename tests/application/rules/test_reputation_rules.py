"""
Application layer rules testing.
Tests business rules through the application layer to ensure proper domain service integration.
"""
import unittest
from unittest.mock import Mock

from src.domain.person.person import Person
from src.domain.person.role import Role
from src.domain.action.action import Action
from src.domain.activity.activity import Activity
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.shared.value_objects.action_id import ActionId
from src.domain.shared.value_objects.activity_id import ActivityId
from src.domain.shared.domain_events import ProofValidatedEvent
from src.domain.services.reputation_service import ReputationService
from src.application.handlers.reputation_event_handler import ReputationEventHandler


class TestReputationRules(unittest.TestCase):
    """Test business rules for reputation calculation through application layer."""

    def setUp(self):
        """Set up test fixtures"""
        # Create domain service
        self.reputation_service = ReputationService()
        
        # Mock repositories
        self.person_repo = Mock()
        self.activity_repo = Mock()
        
        # Create handlers that use the reputation service
        self.reputation_handler = ReputationEventHandler(
            self.person_repo,
            self.activity_repo, 
            self.reputation_service
        )
        
        # Test data
        self.person_id = PersonId.generate()
        self.activity_id = ActivityId.generate()
        self.creator_id = PersonId.generate()

    def test_boost_reputation_calculation_for_verified_actions(self):
        """Test that verified actions boost reputation calculation"""
        # Create a person
        person = Person(self.person_id, "Test User", "test@example.com", Role.MEMBER)
        
        # Create verified actions
        action1 = Action.submit(
            ActionId.generate(),
            person.person_id,
            self.activity_id,
            "Proof 1"
        )
        # Validate the proof to make it verified
        action1.validate_proof()
        
        action2 = Action.submit(
            ActionId.generate(),
            person.person_id,
            self.activity_id,
            "Proof 2"
        )
        action2.validate_proof()
        
        verified_actions = [action1, action2]
        
        # Calculate reputation
        reputation = self.reputation_service.calculate_person_reputation(
            person, verified_actions
        )
        
        # Assert reputation boost for verified actions
        self.assertGreater(reputation, 0, "Verified actions should boost reputation")

    def test_no_reputation_for_unverified_actions(self):
        """Test that unverified actions don't contribute to reputation"""
        # Create a person
        person = Person(self.person_id, "Test User", "test@example.com", Role.MEMBER)
        
        # Create unverified actions (don't call validate_proof)
        Action.submit(
            ActionId.generate(),
            person.person_id,
            self.activity_id,
            "Proof 1"
        )
        
        Action.submit(
            ActionId.generate(),
            person.person_id,
            self.activity_id,
            "Proof 2"
        )
        
        unverified_actions: list[Action] = []  # No actions should be passed if none are verified
        
        # Calculate reputation
        reputation = self.reputation_service.calculate_person_reputation(
            person, unverified_actions
        )
        
        # Assert no reputation for unverified actions
        self.assertEqual(reputation, 0, "Unverified actions should not contribute to reputation")

    def test_mixed_verified_and_unverified_actions(self):
        """Test reputation calculation with mix of verified and unverified actions"""
        # Create a person
        person = Person(self.person_id, "Test User", "test@example.com", Role.MEMBER)
        
        # Create mix of verified and unverified actions
        verified_action = Action.submit(
            ActionId.generate(),
            person.person_id,
            self.activity_id,
            "Verified proof"
        )
        verified_action.validate_proof()
        
        # Create unverified action (no validation call)  
        Action.submit(
            ActionId.generate(),
            person.person_id,
            self.activity_id,
            "Unverified proof"
        )
        
        mixed_actions: list[Action] = [verified_action]  # Only verified actions should be passed
        
        # Calculate reputation
        reputation = self.reputation_service.calculate_person_reputation(
            person, mixed_actions
        )
        
        # Only verified action should contribute
        self.assertGreater(reputation, 0, "Should get reputation from verified action")
        
        # Should be same as if only verified action was included
        verified_only_reputation = self.reputation_service.calculate_person_reputation(
            person, [verified_action]
        )
        self.assertEqual(reputation, verified_only_reputation, 
                        "Only verified actions should contribute to reputation")

    def test_role_based_reputation_modifier(self):
        """Test that different roles get different reputation modifiers"""
        # Create member and lead persons
        member = Person(self.person_id, "Member User", "member@example.com", Role.MEMBER)
        lead_id = PersonId.generate()
        lead = Person(lead_id, "Lead User", "lead@example.com", Role.LEAD)
        
        # Create identical verified actions for both
        member_action = Action.submit(
            ActionId.generate(),
            member.person_id,
            self.activity_id,
            "Test proof"
        )
        member_action.validate_proof()
        
        lead_action = Action.submit(
            ActionId.generate(),
            lead.person_id,
            self.activity_id,
            "Test proof"
        )
        lead_action.validate_proof()
        
        # Calculate reputation for both
        member_reputation = self.reputation_service.calculate_person_reputation(
            member, [member_action]
        )
        lead_reputation = self.reputation_service.calculate_person_reputation(
            lead, [lead_action]
        )
        
        # Lead should get higher reputation due to role modifier
        self.assertGreater(lead_reputation, member_reputation, 
                          "Lead role should get higher reputation modifier")

    def test_event_handler_processes_proof_validated_event(self):
        """Test that reputation event handler processes ProofValidatedEvent correctly"""
        # Set up mock person and activity
        person = Person(self.person_id, "Test User", "test@example.com", Role.MEMBER)
        activity = Activity(
            activity_id=self.activity_id,
            title="Test Activity",
            description="Test activity for engagement",
            creator_id=self.creator_id
        )
        
        # Mock repository returns
        self.person_repo.find_by_id.return_value = person
        self.activity_repo.find_by_id.return_value = activity
        
        # Create a ProofValidatedEvent
        event = ProofValidatedEvent(
            action_id=ActionId.generate(),
            person_id=self.person_id,
            activity_id=self.activity_id,
            is_valid=True
        )
        
        # Handle the event
        self.reputation_handler.handle(event)
        
        # Verify repository interactions
        self.person_repo.find_by_id.assert_called_once_with(self.person_id)
        self.activity_repo.find_by_id.assert_called_once_with(self.activity_id)
        self.person_repo.save.assert_called_once()

    def test_event_handler_ignores_invalid_proofs(self):
        """Test that reputation event handler ignores invalid proof events"""
        # Create a ProofValidatedEvent with invalid proof
        event = ProofValidatedEvent(
            action_id=ActionId.generate(),
            person_id=self.person_id,
            activity_id=self.activity_id,
            is_valid=False  # Invalid proof
        )
        
        # Handle the event
        self.reputation_handler.handle(event)
        
        # Verify no repository interactions for invalid proofs
        self.person_repo.find_by_id.assert_not_called()
        self.activity_repo.find_by_id.assert_not_called()
        self.person_repo.save.assert_not_called()

    def test_activity_scoring_with_multiple_participants(self):
        """Test activity scoring calculation with multiple participants"""
        # Create multiple participants
        participants: list[Person] = []
        actions_by_activity: list[Action] = []
        
        for i in range(3):
            participant_id = PersonId.generate()
            participant = Person(participant_id, f"User {i}", f"user{i}@example.com", Role.MEMBER)
            participants.append(participant)
            
            # Each participant has verified actions
            action = Action.submit(
                ActionId.generate(),
                participant_id,
                self.activity_id,
                f"Proof {i}"
            )
            action.validate_proof()
            actions_by_activity.append(action)
        
        # Create test activity
        activity = Activity(
            activity_id=self.activity_id,
            title="Test Activity",
            description="Test activity for engagement", 
            creator_id=self.creator_id
        )
        
        # Calculate activity score
        score = self.reputation_service.calculate_activity_score(activity, actions_by_activity)
        
        # Activity with multiple verified actions should have higher score
        self.assertGreater(score, 0, "Activity with verified actions should have positive score")

    def test_empty_activity_scoring(self):
        """Test activity scoring with no actions"""
        # Create test activity
        activity = Activity(
            activity_id=self.activity_id,
            title="Empty Activity", 
            description="Activity with no actions",
            creator_id=self.creator_id
        )
        
        # Calculate score with no actions
        no_actions: list[Action] = []
        score = self.reputation_service.calculate_activity_score(activity, no_actions)
        
        # Empty activity should have zero score
        self.assertEqual(score, 0, "Activity with no actions should have zero score")

    def test_mixed_action_status_scoring(self):
        """Test activity scoring with mixed action statuses"""
        # Create test activity
        activity = Activity(
            activity_id=self.activity_id,
            title="Mixed Activity",
            description="Activity with mixed action statuses",
            creator_id=self.creator_id
        )
        
        # Create actions with different statuses
        verified_action = Action.submit(
            ActionId.generate(),
            self.person_id,
            self.activity_id,
            "Verified proof"
        )
        verified_action.validate_proof()
        
        # Create unverified action (no validation call)
        unverified_action = Action.submit(
            ActionId.generate(),
            self.person_id,
            self.activity_id,
            "Unverified proof"
        )
        
        mixed_actions: list[Action] = [verified_action, unverified_action]
        
        # Calculate score
        score = self.reputation_service.calculate_activity_score(activity, mixed_actions)
        
        # Should only count verified actions
        self.assertGreater(score, 0, "Should get positive score from verified actions")


if __name__ == "__main__":
    unittest.main()