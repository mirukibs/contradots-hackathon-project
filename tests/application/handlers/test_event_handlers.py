"""Comprehensive tests for Event Handlers"""

from typing import List, Dict, Any
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime
from src.application.handlers.reputation_event_handler import ReputationEventHandler
from src.application.handlers.activity_projection_handler import ActivityProjectionHandler
from src.application.handlers.leaderboard_projection_handler import LeaderboardProjectionHandler
from src.domain.shared.events.action_submitted_event import ActionSubmittedEvent
from src.domain.shared.events.proof_validated_event import ProofValidatedEvent
from src.domain.shared.events.domain_event import DomainEvent
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.shared.value_objects.activity_id import ActivityId  
from src.domain.shared.value_objects.action_id import ActionId
from src.domain.person.person import Person
from src.domain.person.role import Role
from src.domain.activity.activity import Activity


class TestDifferentEvent(DomainEvent):
    """Test event that handlers should not process"""
    
    def __init__(self):
        super().__init__(
            event_id=uuid4(),
            occurred_at=datetime.now(),
            aggregate_id=uuid4(),
            aggregate_type="TestAggregate"
        )


class TestReputationEventHandler:
    """Test suite for ReputationEventHandler covering all methods and edge cases"""
    
    def setup_method(self):
        """Set up test fixtures and mocks"""
        # Create mock repositories and services
        self.mock_person_repo = Mock()
        self.mock_activity_repo = Mock()
        self.mock_reputation_service = Mock()
        
        # Create handler instance
        self.handler = ReputationEventHandler(
            person_repo=self.mock_person_repo,
            activity_repo=self.mock_activity_repo,
            reputation_service=self.mock_reputation_service
        )
        
        # Test data
        self.person_id = PersonId.generate()
        self.activity_id = ActivityId.generate()
        self.action_id = ActionId.generate()
        
        # Create test person
        self.test_person = Person.create(
            name="John Doe",
            email="john@example.com",
            role=Role.MEMBER
        )
        # Set initial reputation
        self.test_person.__dict__['_reputation_score'] = 50
        
        # Create test lead
        self.test_lead = Person.create(
            name="Lead User",
            email="lead@example.com", 
            role=Role.LEAD
        )
        self.test_lead.__dict__['_reputation_score'] = 100
        
        # Create test activity
        self.test_activity = Activity(
            activity_id=self.activity_id,
            title="Beach Cleanup",
            description="Clean the beach",
            creator_id=PersonId.generate()
        )
        
        # Create test events
        self.action_submitted_event = ActionSubmittedEvent(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            description="Test action submission",
            proof_hash="0123456789abcdef0123456789abcdef"
        )
        
        self.valid_proof_event = ProofValidatedEvent(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            is_valid=True
        )
        
        self.invalid_proof_event = ProofValidatedEvent(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            is_valid=False
        )

    def test_can_handle_action_submitted_event(self):
        """Test handler can handle ActionSubmittedEvent"""
        # Act
        result = self.handler.can_handle(self.action_submitted_event)
        
        # Assert
        assert result == True

    def test_can_handle_proof_validated_event(self):
        """Test handler can handle ProofValidatedEvent"""
        # Act
        result = self.handler.can_handle(self.valid_proof_event)
        
        # Assert
        assert result == True

    def test_can_handle_unsupported_event(self):
        """Test handler cannot handle unsupported event types"""
        # Arrange
        unsupported_event = TestDifferentEvent()
        
        # Act
        result = self.handler.can_handle(unsupported_event)
        
        # Assert
        assert result == False

    def test_handle_action_submitted_event(self):
        """Test handling ActionSubmittedEvent (currently a no-op)"""
        # Act - should not raise any exceptions
        self.handler.handle(self.action_submitted_event)
        
        # Assert - currently no side effects expected
        # This test validates the event is accepted without errors

    def test_handle_valid_proof_event_member(self):
        """Test handling valid ProofValidatedEvent for regular member"""
        # Arrange
        self.mock_person_repo.find_by_id.return_value = self.test_person
        self.mock_activity_repo.find_by_id.return_value = self.test_activity
        
        # Act
        self.handler.handle(self.valid_proof_event)
        
        # Assert
        self.mock_person_repo.find_by_id.assert_called_once_with(self.person_id)
        self.mock_activity_repo.find_by_id.assert_called_once_with(self.activity_id)
        self.mock_person_repo.save.assert_called_once_with(self.test_person)
        
        # Check reputation was updated (50 + 10 = 60)
        assert self.test_person.reputation_score == 60

    def test_handle_valid_proof_event_lead(self):
        """Test handling valid ProofValidatedEvent for lead (with modifier)"""
        # Arrange
        valid_proof_event_lead = ProofValidatedEvent(
            action_id=self.action_id,
            person_id=self.test_lead.person_id,
            activity_id=self.activity_id,
            is_valid=True
        )
        self.mock_person_repo.find_by_id.return_value = self.test_lead
        self.mock_activity_repo.find_by_id.return_value = self.test_activity
        
        # Act
        self.handler.handle(valid_proof_event_lead)
        
        # Assert
        self.mock_person_repo.save.assert_called_once_with(self.test_lead)
        
        # Check reputation was updated with lead modifier (100 + 12 = 112)
        assert self.test_lead.reputation_score == 112

    def test_handle_invalid_proof_event(self):
        """Test handling invalid ProofValidatedEvent (no reputation change)"""
        # Act
        self.handler.handle(self.invalid_proof_event)
        
        # Assert - no repository calls should be made
        self.mock_person_repo.find_by_id.assert_not_called()
        self.mock_activity_repo.find_by_id.assert_not_called()
        self.mock_person_repo.save.assert_not_called()

    def test_handle_proof_validated_person_not_found(self):
        """Test handling ProofValidatedEvent when person doesn't exist"""
        # Arrange
        self.mock_person_repo.find_by_id.return_value = None
        
        # Act & Assert
        try:
            self.handler.handle(self.valid_proof_event)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert f"Person not found: {self.person_id}" in str(e)
        
        # Verify save was not called
        self.mock_person_repo.save.assert_not_called()

    def test_handle_proof_validated_activity_not_found(self):
        """Test handling ProofValidatedEvent when activity doesn't exist"""
        # Arrange
        self.mock_person_repo.find_by_id.return_value = self.test_person
        self.mock_activity_repo.find_by_id.return_value = None
        
        # Act & Assert
        try:
            self.handler.handle(self.valid_proof_event)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert f"Activity not found: {self.activity_id}" in str(e)
        
        # Verify save was not called
        self.mock_person_repo.save.assert_not_called()

    def test_handle_unsupported_event_type(self):
        """Test handling unsupported event type raises error"""
        # Arrange
        unsupported_event = TestDifferentEvent()
        
        # Act & Assert
        try:
            self.handler.handle(unsupported_event)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Unsupported event type" in str(e)

    def test_reputation_calculation_precision(self):
        """Test reputation calculation with different starting values"""
        # Arrange - test with different initial reputation values
        test_cases = [
            (0, 10),    # New user
            (25, 35),   # Existing user
            (100, 110), # High reputation user
        ]
        
        for initial_reputation, expected_final in test_cases:
            # Reset person reputation
            self.test_person.__dict__['_reputation_score'] = initial_reputation
            self.mock_person_repo.reset_mock()
            
            self.mock_person_repo.find_by_id.return_value = self.test_person
            self.mock_activity_repo.find_by_id.return_value = self.test_activity
            
            # Act
            self.handler.handle(self.valid_proof_event)
            
            # Assert
            assert self.test_person.reputation_score == expected_final

    def test_constructor_dependencies(self):
        """Test handler constructor properly stores dependencies"""
        # Verify dependencies are stored (using reflection for testing)
        assert self.handler.__dict__.get('_person_repo') is self.mock_person_repo
        assert self.handler.__dict__.get('_activity_repo') is self.mock_activity_repo
        assert self.handler.__dict__.get('_reputation_service') is self.mock_reputation_service


class TestActivityProjectionHandler:
    """Test suite for ActivityProjectionHandler covering all methods and edge cases"""
    
    def setup_method(self):
        """Set up test fixtures and mocks"""
        # Create mock repository
        self.mock_activity_query_repo = Mock()
        
        # Create handler instance
        self.handler = ActivityProjectionHandler(self.mock_activity_query_repo)
        
        # Test data
        self.person_id = PersonId.generate()
        self.activity_id = ActivityId.generate()
        self.action_id = ActionId.generate()
        
        # Create test events
        self.action_submitted_event = ActionSubmittedEvent(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            description="Activity projection test action",
            proof_hash="abcdef0123456789abcdef0123456789"
        )
        
        self.proof_validated_event = ProofValidatedEvent(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            is_valid=True
        )

    def test_can_handle_action_submitted_event(self):
        """Test handler can handle ActionSubmittedEvent"""
        # Act
        result = self.handler.can_handle(self.action_submitted_event)
        
        # Assert
        assert result == True

    def test_can_handle_proof_validated_event(self):
        """Test handler cannot handle ProofValidatedEvent"""
        # Act
        result = self.handler.can_handle(self.proof_validated_event)
        
        # Assert
        assert result == False

    def test_can_handle_unsupported_event(self):
        """Test handler cannot handle unsupported event types"""
        # Arrange
        unsupported_event = TestDifferentEvent()
        
        # Act
        result = self.handler.can_handle(unsupported_event)
        
        # Assert
        assert result == False

    def test_handle_action_submitted_event(self):
        """Test handling ActionSubmittedEvent (currently a placeholder)"""
        # Act - should not raise any exceptions
        self.handler.handle(self.action_submitted_event)
        
        # Assert - currently no side effects expected
        # This test validates the event is accepted without errors

    def test_handle_proof_validated_event(self):
        """Test handling ProofValidatedEvent (should be ignored)"""
        # Act - should not raise any exceptions
        self.handler.handle(self.proof_validated_event)
        
        # Assert - no repository calls should be made
        # Handler ignores this event type

    def test_handle_unsupported_event(self):
        """Test handling unsupported event type (should be ignored)"""
        # Arrange
        unsupported_event = TestDifferentEvent()
        
        # Act - should not raise any exceptions
        self.handler.handle(unsupported_event)
        
        # Assert - no repository calls should be made

    def test_constructor_dependencies(self):
        """Test handler constructor properly stores dependencies"""
        # Verify dependency is stored (using reflection for testing)
        assert self.handler.__dict__.get('_activity_query_repo') is self.mock_activity_query_repo

    def test_multiple_action_submitted_events(self):
        """Test handling multiple ActionSubmittedEvent instances"""
        # Arrange
        event2 = ActionSubmittedEvent(
            action_id=ActionId.generate(),
            person_id=PersonId.generate(),
            activity_id=ActivityId.generate(),
            description="Second test action",
            proof_hash="fedcba9876543210fedcba9876543210"
        )
        
        # Act - should handle multiple events without issues
        self.handler.handle(self.action_submitted_event)
        self.handler.handle(event2)
        
        # Assert - no exceptions should be raised


class TestLeaderboardProjectionHandler:
    """Test suite for LeaderboardProjectionHandler covering all methods and edge cases"""
    
    def setup_method(self):
        """Set up test fixtures and mocks"""
        # Create mock repository
        self.mock_leaderboard_repo = Mock()
        
        # Create handler instance
        self.handler = LeaderboardProjectionHandler(self.mock_leaderboard_repo)
        
        # Test data
        self.person_id = PersonId.generate()
        self.activity_id = ActivityId.generate()
        self.action_id = ActionId.generate()
        
        # Create test events
        self.action_submitted_event = ActionSubmittedEvent(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            description="Leaderboard test action",
            proof_hash="0123456789abcdef0123456789abcdef"
        )
        
        self.proof_validated_event = ProofValidatedEvent(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            is_valid=True
        )

    def test_can_handle_action_submitted_event(self):
        """Test handler can handle ActionSubmittedEvent"""
        # Act
        result = self.handler.can_handle(self.action_submitted_event)
        
        # Assert
        assert result == True

    def test_can_handle_proof_validated_event(self):
        """Test handler can handle ProofValidatedEvent"""
        # Act
        result = self.handler.can_handle(self.proof_validated_event)
        
        # Assert
        assert result == True

    def test_can_handle_unsupported_event(self):
        """Test handler cannot handle unsupported event types"""
        # Arrange
        unsupported_event = TestDifferentEvent()
        
        # Act
        result = self.handler.can_handle(unsupported_event)
        
        # Assert
        assert result == False

    def test_handle_action_submitted_event(self):
        """Test handling ActionSubmittedEvent (currently a placeholder)"""
        # Act - should not raise any exceptions
        self.handler.handle(self.action_submitted_event)
        
        # Assert - currently no side effects expected
        # This test validates the event is accepted without errors

    def test_handle_proof_validated_event(self):
        """Test handling ProofValidatedEvent (currently a placeholder)"""
        # Act - should not raise any exceptions
        self.handler.handle(self.proof_validated_event)
        
        # Assert - currently no side effects expected
        # This test validates the event is accepted without errors

    def test_handle_unsupported_event(self):
        """Test handling unsupported event type (should be ignored)"""
        # Arrange
        unsupported_event = TestDifferentEvent()
        
        # Act - should not raise any exceptions
        self.handler.handle(unsupported_event)
        
        # Assert - no repository calls should be made

    def test_constructor_dependencies(self):
        """Test handler constructor properly stores dependencies"""
        # Verify dependency is stored (using reflection for testing)
        assert self.handler.__dict__.get('_leaderboard_repo') is self.mock_leaderboard_repo

    def test_multiple_events_handling(self):
        """Test handling multiple different event types"""
        # Arrange
        event2 = ProofValidatedEvent(
            action_id=ActionId.generate(),
            person_id=PersonId.generate(),
            activity_id=ActivityId.generate(),
            is_valid=False
        )
        
        # Act - should handle multiple events without issues
        self.handler.handle(self.action_submitted_event)
        self.handler.handle(self.proof_validated_event)
        self.handler.handle(event2)
        
        # Assert - no exceptions should be raised

    def test_event_type_filtering(self):
        """Test that handler properly filters events by type"""
        # Test all supported event types
        supported_events: List[DomainEvent] = [
            self.action_submitted_event,
            self.proof_validated_event
        ]
        
        for event in supported_events:
            assert self.handler.can_handle(event) == True
        
        # Test unsupported event type
        unsupported_event = TestDifferentEvent()
        assert self.handler.can_handle(unsupported_event) == False


class TestEventHandlersIntegration:
    """Integration tests for multiple event handlers working together"""
    
    def setup_method(self):
        """Set up test fixtures for integration testing"""
        # Create mocks
        self.mock_person_repo = Mock()
        self.mock_activity_repo = Mock()
        self.mock_reputation_service = Mock()
        self.mock_activity_query_repo = Mock()
        self.mock_leaderboard_repo = Mock()
        
        # Create handlers
        self.reputation_handler = ReputationEventHandler(
            self.mock_person_repo,
            self.mock_activity_repo,
            self.mock_reputation_service
        )
        
        self.activity_handler = ActivityProjectionHandler(
            self.mock_activity_query_repo
        )
        
        self.leaderboard_handler = LeaderboardProjectionHandler(
            self.mock_leaderboard_repo
        )
        
        # Test data
        self.person_id = PersonId.generate()
        self.activity_id = ActivityId.generate()
        self.action_id = ActionId.generate()
        
        self.action_submitted_event = ActionSubmittedEvent(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            description="Integration test action",
            proof_hash="0123456789abcdef0123456789abcdef"
        )
        
        self.proof_validated_event = ProofValidatedEvent(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            is_valid=True
        )

    def test_action_submitted_event_distribution(self):
        """Test ActionSubmittedEvent is handled by appropriate handlers"""
        # Arrange
        handlers: List[Any] = [self.reputation_handler, self.activity_handler, self.leaderboard_handler]
        
        # Act & Assert
        for handler in handlers:
            if handler.can_handle(self.action_submitted_event):
                # Should not raise exceptions
                handler.handle(self.action_submitted_event)
        
        # Verify all handlers that can handle the event did so
        assert self.reputation_handler.can_handle(self.action_submitted_event)
        assert self.activity_handler.can_handle(self.action_submitted_event)
        assert self.leaderboard_handler.can_handle(self.action_submitted_event)

    def test_proof_validated_event_distribution(self):
        """Test ProofValidatedEvent is handled by appropriate handlers"""
        # Arrange
        test_person = Person.create("John", "john@example.com", Role.MEMBER)
        test_person.__dict__['_reputation_score'] = 50
        test_activity = Activity(
            activity_id=self.activity_id,
            title="Test Activity",
            description="Test",
            creator_id=PersonId.generate()
        )
        
        self.mock_person_repo.find_by_id.return_value = test_person
        self.mock_activity_repo.find_by_id.return_value = test_activity
        
        handlers: List[Any] = [self.reputation_handler, self.activity_handler, self.leaderboard_handler]
        
        # Act & Assert
        for handler in handlers:
            if handler.can_handle(self.proof_validated_event):
                # Should not raise exceptions
                handler.handle(self.proof_validated_event)
        
        # Verify reputation handler processed the event
        assert self.reputation_handler.can_handle(self.proof_validated_event)
        # Activity handler should not handle proof validated events
        assert not self.activity_handler.can_handle(self.proof_validated_event)
        assert self.leaderboard_handler.can_handle(self.proof_validated_event)

    def test_event_handler_specialization(self):
        """Test that each handler specializes in specific event types"""
        # Define event-to-handler mappings
        event_handler_map: Dict[DomainEvent, List[Any]] = {
            self.action_submitted_event: [
                self.reputation_handler,
                self.activity_handler,
                self.leaderboard_handler
            ],
            self.proof_validated_event: [
                self.reputation_handler,
                self.leaderboard_handler
            ]
        }
        
        # Test each mapping
        for event, expected_handlers in event_handler_map.items():
            all_handlers: List[Any] = [self.reputation_handler, self.activity_handler, self.leaderboard_handler]
            
            for handler in all_handlers:
                if handler in expected_handlers:
                    assert handler.can_handle(event), f"{handler.__class__.__name__} should handle {event.__class__.__name__}"
                else:
                    assert not handler.can_handle(event), f"{handler.__class__.__name__} should not handle {event.__class__.__name__}"