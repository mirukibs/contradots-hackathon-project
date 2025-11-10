"""
Tests for ActionStatus enum.
Covers all enum values and methods for ActionStatus.
"""
from src.domain.action.action_status import ActionStatus


class TestActionStatus:
    """Test ActionStatus enum implementation."""
    
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
    
    def test_action_status_comparison(self):
        """Test ActionStatus comparison operations."""
        assert ActionStatus.SUBMITTED == ActionStatus.SUBMITTED
        assert ActionStatus.SUBMITTED != ActionStatus.VALIDATED
        assert ActionStatus.VALIDATED != ActionStatus.REJECTED
    
    def test_action_status_membership(self):
        """Test ActionStatus can be used in collections."""
        statuses = {ActionStatus.SUBMITTED, ActionStatus.VALIDATED, ActionStatus.REJECTED}
        assert len(statuses) == 3
        assert ActionStatus.SUBMITTED in statuses
        assert ActionStatus.VALIDATED in statuses
        assert ActionStatus.REJECTED in statuses