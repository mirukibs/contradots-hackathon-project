"""
Tests for Action aggregate root.
Covers all methods and business rules for Action aggregate.
"""
from datetime import datetime, timezone
from src.domain.shared.value_objects.action_id import ActionId
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.shared.value_objects.activity_id import ActivityId
from src.domain.action.action import Action
from src.domain.action.action_status import ActionStatus
from src.domain.shared.domain_events import ActionSubmittedEvent, ProofValidatedEvent


class TestAction:
    """Test Action aggregate root implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.action_id = ActionId.generate()
        self.person_id = PersonId.generate()
        self.activity_id = ActivityId.generate()
        self.test_proof = "blockchain_proof_hash_123"
    
    def test_init_with_all_parameters(self):
        """Test Action initialization with all parameters."""
        submitted_at = datetime.now(timezone.utc)
        
        action = Action(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            proof=self.test_proof,
            status=ActionStatus.SUBMITTED,
            submitted_at=submitted_at
        )
        
        assert action.action_id == self.action_id
        assert action.person_id == self.person_id
        assert action.activity_id == self.activity_id
        assert action.proof == self.test_proof
        assert action.status == ActionStatus.SUBMITTED
        assert action.submitted_at == submitted_at
        assert action.verified_at is None
    
    def test_init_with_default_values(self):
        """Test Action initialization with default values."""
        action = Action(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            proof=self.test_proof
        )
        
        assert action.status == ActionStatus.SUBMITTED
        assert isinstance(action.submitted_at, datetime)
        assert action.verified_at is None
        assert len(action.domain_events) == 0
    
    def test_submit_class_method(self):
        """Test Action.submit() class method creates new Action with event."""
        action = Action.submit(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            proof=self.test_proof
        )
        
        assert action.action_id == self.action_id
        assert action.person_id == self.person_id
        assert action.activity_id == self.activity_id
        assert action.proof == self.test_proof
        assert action.status == ActionStatus.SUBMITTED
        assert len(action.domain_events) == 1
        
        # Check the domain event
        event = action.domain_events[0]
        assert isinstance(event, ActionSubmittedEvent)
        assert event.action_id == self.action_id
        assert event.person_id == self.person_id
        assert event.activity_id == self.activity_id
    
    def test_validate_proof_success(self):
        """Test validate_proof() method for successful validation."""
        action = Action.submit(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            proof=self.test_proof
        )
        
        # Clear the submit event for easier testing
        action.clear_domain_events()
        
        action.validate_proof()
        
        assert action.status == ActionStatus.VALIDATED  # Updated to match domain model
        assert action.verified_at is not None
        assert isinstance(action.verified_at, datetime)
        assert len(action.domain_events) == 1
        
        # Check the domain event
        event = action.domain_events[0]
        assert isinstance(event, ProofValidatedEvent)
        assert event.action_id == self.action_id
        assert event.is_valid == True
    
    def test_validate_proof_when_not_submitted_raises_error(self):
        """Test validate_proof() raises error when action is not in SUBMITTED status."""
        action = Action(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            proof=self.test_proof,
            status=ActionStatus.VALIDATED
        )
        
        try:
            action.validate_proof()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Can only validate proof for actions in SUBMITTED status" in str(e)
    
    def test_is_verified_true(self):
        """Test is_verified() returns True for validated action."""
        action = Action(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            proof=self.test_proof,
            status=ActionStatus.VALIDATED
        )
        
        assert action.is_verified() == True
    
    def test_is_verified_false(self):
        """Test is_verified() returns False for non-validated action."""
        action = Action(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            proof=self.test_proof,
            status=ActionStatus.SUBMITTED
        )
        
        assert action.is_verified() == False
    
    def test_clear_domain_events(self):
        """Test clear_domain_events() removes all events."""
        action = Action.submit(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            proof=self.test_proof
        )
        
        assert len(action.domain_events) == 1
        
        action.clear_domain_events()
        
        assert len(action.domain_events) == 0
    
    def test_domain_events_returns_copy(self):
        """Test domain_events property returns a copy (immutable)."""
        action = Action.submit(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            proof=self.test_proof
        )
        
        events = action.domain_events
        events.clear()  # Modify the returned list
        
        # Original should still have events
        assert len(action.domain_events) == 1
    
    def test_equality_same_action_id(self):
        """Test Action equality based on action ID."""
        action1 = Action(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            proof=self.test_proof
        )
        
        action2 = Action(
            action_id=self.action_id,
            person_id=PersonId.generate(),  # Different person
            activity_id=ActivityId.generate(),  # Different activity
            proof="different_proof"
        )
        
        assert action1 == action2
    
    def test_equality_different_action_id(self):
        """Test Action inequality with different action IDs."""
        action1 = Action(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            proof=self.test_proof
        )
        
        action2 = Action(
            action_id=ActionId.generate(),
            person_id=self.person_id,
            activity_id=self.activity_id,
            proof=self.test_proof
        )
        
        assert action1 != action2
    
    def test_hash_consistency(self):
        """Test Action hash is consistent and based on action ID."""
        action1 = Action(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            proof=self.test_proof
        )
        
        action2 = Action(
            action_id=self.action_id,
            person_id=PersonId.generate(),
            activity_id=ActivityId.generate(),
            proof="different_proof"
        )
        
        assert hash(action1) == hash(action2)
    
    def test_repr_representation(self):
        """Test Action repr representation."""
        action = Action(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            proof=self.test_proof
        )
        
        expected_repr = (f"Action(action_id={self.action_id}, "
                        f"person_id={self.person_id}, "
                        f"activity_id={self.activity_id}, "
                        f"status={ActionStatus.SUBMITTED}, "
                        f"submitted_at={action.submitted_at})")
        
        assert repr(action) == expected_repr


class TestActionStatus:
    """Test ActionStatus enum."""
    
    def test_action_status_values(self):
        """Test ActionStatus enum values match domain model."""
        assert ActionStatus.SUBMITTED.value == "submitted"
        assert ActionStatus.VALIDATED.value == "validated"
        assert ActionStatus.REJECTED.value == "rejected"
    
    def test_action_status_str_representation(self):
        """Test ActionStatus string representation."""
        assert str(ActionStatus.SUBMITTED) == "submitted"
        assert str(ActionStatus.VALIDATED) == "validated"
        assert str(ActionStatus.REJECTED) == "rejected"