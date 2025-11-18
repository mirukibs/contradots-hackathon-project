"""Comprehensive tests for ActionApplicationService"""

from typing import List
from unittest.mock import Mock
from src.application.services.action_application_service import ActionApplicationService
from src.application.commands.submit_action_command import SubmitActionCommand
from src.application.commands.validate_proof_command import ValidateProofCommand
from src.application.dtos.action_dto import ActionDto
from src.application.security.authentication_context import AuthenticationContext
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.shared.value_objects.activity_id import ActivityId
from src.domain.shared.value_objects.action_id import ActionId
from src.domain.action.action import Action
from src.domain.activity.activity import Activity
from src.domain.shared.events.proof_validated_event import ProofValidatedEvent


class TestActionApplicationService:
    """Test suite for ActionApplicationService covering all methods and edge cases"""

    def setup_method(self):
        """Set up test fixtures and mocks"""
        # Create mock repositories and event publisher
        self.mock_action_repo = Mock()
        self.mock_action_query_repo = Mock()
        self.mock_activity_repo = Mock()
        self.mock_event_publisher = Mock()
        self.mock_authorization_service = Mock()
        
        # Test data
        self.valid_person_id = PersonId.generate()
        self.valid_activity_id = ActivityId.generate()
        self.valid_action_id = ActionId.generate()
        
        # Create mock authentication context
        self.mock_auth_context = Mock(spec=AuthenticationContext)
        self.mock_auth_context.is_authenticated = True
        self.mock_auth_context.current_user_id = self.valid_person_id  # Use same person_id for consistency
        self.mock_auth_context.email = "test@example.com"
        
        # Create service instance
        self.service = ActionApplicationService(
            action_repo=self.mock_action_repo,
            action_query_repo=self.mock_action_query_repo,
            activity_repo=self.mock_activity_repo,
            event_publisher=self.mock_event_publisher,
            authorization_service=self.mock_authorization_service
        )
        
        # Create test activity
        self.test_activity = Activity(
            activity_id=self.valid_activity_id,
            title="Beach Cleanup",
            description="Clean the beach",
            creator_id=PersonId.generate(),
            points=100
        )
        
        # Create test action
        self.test_action = Action.submit(
            action_id=self.valid_action_id,
            person_id=self.valid_person_id,
            activity_id=self.valid_activity_id,
            proof="Cleaned 50 meters of beach [Hash: abc123]"
        )
        
        self.valid_submit_command = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description="Cleaned 50 meters of beach",
            proofHash="abc123def456789abc123def456789ab"  # Valid 32-character hex
        )
        
        self.valid_validate_command = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=True
        )

    def test_submit_action_success(self):
        """Test successful action submission"""
        # Arrange
        self.mock_activity_repo.find_by_id.return_value = self.test_activity
        
        # Act
        result = self.service.submit_action(self.valid_submit_command, self.mock_auth_context)
        
        # Assert
        assert isinstance(result, ActionId)
        self.mock_activity_repo.find_by_id.assert_called_once_with(self.valid_activity_id)
        self.mock_action_repo.save.assert_called_once()
        self.mock_event_publisher.publish.assert_called()
        
        # Verify the action passed to save has correct attributes
        saved_action = self.mock_action_repo.save.call_args[0][0]
        assert saved_action.person_id == self.valid_person_id
        assert saved_action.activity_id == self.valid_activity_id
        assert "Cleaned 50 meters of beach" in saved_action.proof
        assert "abc123def456789abc123def456789ab" in saved_action.proof

    def test_submit_action_activity_not_found(self):
        """Test action submission when activity doesn't exist"""
        # Arrange
        self.mock_activity_repo.find_by_id.return_value = None
        
        # Act & Assert
        try:
            self.service.submit_action(self.valid_submit_command, self.mock_auth_context)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert f"Activity not found: {self.valid_activity_id}" in str(e)
        
        # Verify repository calls
        self.mock_activity_repo.find_by_id.assert_called_once_with(self.valid_activity_id)
        self.mock_action_repo.save.assert_not_called()
        self.mock_event_publisher.publish.assert_not_called()

    def test_submit_action_invalid_command(self):
        """Test action submission with invalid command"""
        # Arrange
        invalid_command = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description="",  # Invalid empty description
            proofHash="abc123def456789abc123def456789ab"
        )
        
        # Act & Assert
        try:
            self.service.submit_action(invalid_command, self.mock_auth_context)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Description is required and cannot be empty" in str(e)
        
        # Verify repositories weren't called
        self.mock_activity_repo.find_by_id.assert_not_called()
        self.mock_action_repo.save.assert_not_called()
        self.mock_event_publisher.publish.assert_not_called()

    def test_submit_action_with_long_description(self):
        """Test action submission with very long description"""
        # Arrange
        long_description = "A" * 2000  # Very long description
        long_command = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description=long_description,
            proofHash="abc123def456789abc123def456789ab"
        )
        self.mock_activity_repo.find_by_id.return_value = self.test_activity
        
        # Act
        result = self.service.submit_action(long_command, self.mock_auth_context)
        
        # Assert
        assert isinstance(result, ActionId)
        saved_action = self.mock_action_repo.save.call_args[0][0]
        assert long_description in saved_action.proof
        assert len(saved_action.proof) > 2000

    def test_submit_action_with_special_characters(self):
        """Test action submission with special characters"""
        # Arrange
        special_command = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description="Limpié 50 metros de playa 🌊 & recolecté 25kg de basura",
            proofHash="abc123def456789abc123def456789ab"
        )
        self.mock_activity_repo.find_by_id.return_value = self.test_activity
        
        # Act
        result = self.service.submit_action(special_command, self.mock_auth_context)
        
        # Assert
        assert isinstance(result, ActionId)
        saved_action = self.mock_action_repo.save.call_args[0][0]
        assert "Limpié 50 metros de playa 🌊" in saved_action.proof
        assert "abc123def456789abc123def456789ab" in saved_action.proof

    def test_submit_action_events_published(self):
        """Test that domain events are published after action submission"""
        # Arrange
        self.mock_activity_repo.find_by_id.return_value = self.test_activity
        
        # Create a mock action that has domain events
        mock_action = Mock()
        mock_action.action_id = self.valid_action_id
        mock_action.person_id = self.valid_person_id
        mock_action.activity_id = self.valid_activity_id
        
        # Mock domain events
        mock_event1 = Mock()
        mock_event2 = Mock()
        mock_action.domain_events = [mock_event1, mock_event2]
        mock_action.clear_domain_events = Mock()
        
        # Mock Action.submit to return our mock
        original_submit = Action.submit
        Action.submit = Mock(return_value=mock_action)
        
        try:
            # Act
            result = self.service.submit_action(self.valid_submit_command, self.mock_auth_context)
            
            # Assert
            assert result == self.valid_action_id
            self.mock_action_repo.save.assert_called_once_with(mock_action)
            
            # Verify events were published
            assert self.mock_event_publisher.publish.call_count == 2
            self.mock_event_publisher.publish.assert_any_call(mock_event1)
            self.mock_event_publisher.publish.assert_any_call(mock_event2)
            
            # Verify events were cleared
            mock_action.clear_domain_events.assert_called_once()
            
        finally:
            # Restore original method
            Action.submit = original_submit
    
    def test_get_pending_validations_success(self):
        """Test successful retrieval of pending validations"""
        # Arrange
        expected_actions = [
            ActionDto(
                actionId=str(ActionId.generate()),
                personName="Person One",
                activityName="Beach Cleanup",
                description="First action",
                status="pending",
                submittedAt="2025-01-01T10:00:00Z"
            ),
            ActionDto(
                actionId=str(ActionId.generate()),
                personName="Person Two",
                activityName="Tree Planting",
                description="Second action",
                status="pending",
                submittedAt="2025-01-01T11:00:00Z"
            )
        ]
        self.mock_action_query_repo.get_pending_validations.return_value = expected_actions
        
        # Act
        result = self.service.get_pending_validations(self.mock_auth_context)
        
        # Assert
        assert result == expected_actions
        assert len(result) == 2
        assert all(action.status == "pending" for action in result)
        self.mock_action_query_repo.get_pending_validations.assert_called_once()

    def test_get_pending_validations_empty(self):
        """Test retrieval when no pending validations exist"""
        # Arrange
        self.mock_action_query_repo.get_pending_validations.return_value = []
        
        # Act
        result = self.service.get_pending_validations(self.mock_auth_context)
        
        # Assert
        assert result == []
        assert len(result) == 0
        self.mock_action_query_repo.get_pending_validations.assert_called_once()

    def test_get_person_actions_success(self):
        """Test successful retrieval of person's actions"""
        # Arrange
        expected_actions = [
            ActionDto(
                actionId=str(ActionId.generate()),
                personName="John Doe",
                activityName="Beach Cleanup",
                description="My first action",
                status="validated",
                submittedAt="2025-01-01T10:00:00Z"
            ),
            ActionDto(
                actionId=str(ActionId.generate()),
                personName="John Doe",
                activityName="Tree Planting",
                description="My second action",
                status="pending",
                submittedAt="2025-01-01T11:00:00Z"
            )
        ]
        self.mock_action_query_repo.get_person_actions.return_value = expected_actions
        
        # Act
        result = self.service.get_person_actions(self.valid_person_id, self.mock_auth_context)
        
        # Assert
        assert result == expected_actions
        assert len(result) == 2
        assert all(action.personName == "John Doe" for action in result)
        self.mock_action_query_repo.get_person_actions.assert_called_once_with(self.valid_person_id)

    def test_get_person_actions_empty(self):
        """Test retrieval when person has no actions"""
        # Arrange
        self.mock_action_query_repo.get_person_actions.return_value = []
        
        # Act
        result = self.service.get_person_actions(self.valid_person_id, self.mock_auth_context)
        
        # Assert
        assert result == []
        assert len(result) == 0
        self.mock_action_query_repo.get_person_actions.assert_called_once_with(self.valid_person_id)

    def test_simulate_proof_validation_success_valid(self):
        """Test successful proof validation (valid proof)"""
        # Arrange
        self.mock_action_repo.find_by_id.return_value = self.test_action
        
        # Act
        self.service.simulate_proof_validation(self.valid_validate_command, self.mock_auth_context)
        
        # Assert
        self.mock_action_repo.find_by_id.assert_called_once_with(self.valid_action_id)
        # Verify publish was called (may include domain events from action creation)
        assert self.mock_event_publisher.publish.call_count >= 1
        
        # Verify the last published event is ProofValidatedEvent
        last_call_args = self.mock_event_publisher.publish.call_args_list[-1]
        published_event = last_call_args[0][0]
        assert isinstance(published_event, ProofValidatedEvent)
        assert published_event.action_id == self.test_action.action_id
        assert published_event.person_id == self.test_action.person_id
        assert published_event.activity_id == self.test_action.activity_id
        assert published_event.is_valid == True

    def test_simulate_proof_validation_success_invalid(self):
        """Test successful proof validation (invalid proof)"""
        # Arrange
        invalid_command = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=False
        )
        self.mock_action_repo.find_by_id.return_value = self.test_action
        
        # Act
        self.service.simulate_proof_validation(invalid_command, self.mock_auth_context)
        
        # Assert
        self.mock_action_repo.find_by_id.assert_called_once_with(self.valid_action_id)
        self.mock_event_publisher.publish.assert_called_once()
        
        # Verify the published event
        published_event = self.mock_event_publisher.publish.call_args[0][0]
        assert isinstance(published_event, ProofValidatedEvent)
        assert published_event.is_valid == False

    def test_simulate_proof_validation_action_not_found(self):
        """Test proof validation when action doesn't exist"""
        # Arrange
        self.mock_action_repo.find_by_id.return_value = None
        
        # Act & Assert
        try:
            self.service.simulate_proof_validation(self.valid_validate_command, self.mock_auth_context)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert f"Action not found: {self.valid_action_id}" in str(e)
        
        # Verify repository calls
        self.mock_action_repo.find_by_id.assert_called_once_with(self.valid_action_id)
        self.mock_event_publisher.publish.assert_not_called()

    def test_simulate_proof_validation_invalid_command(self):
        """Test proof validation with invalid command"""
        # Arrange
        invalid_command = ValidateProofCommand(
            actionId=ActionId.generate(),  # Use valid ActionId for testing
            isValid=True
        )
        # Force validation to fail by clearing required fields after creation
        invalid_command.__dict__['actionId'] = None
        
        # Act & Assert
        try:
            self.service.simulate_proof_validation(invalid_command, self.mock_auth_context)
            assert False, "Should have raised ValueError"
        except ValueError:
            # Command validation should fail
            pass
        
        # Verify repositories weren't called
        self.mock_action_repo.find_by_id.assert_not_called()
        self.mock_event_publisher.publish.assert_not_called()

    def test_service_constructor_with_dependencies(self):
        """Test service constructor properly stores dependencies"""
        # Create new service instance
        service = ActionApplicationService(
            action_repo=self.mock_action_repo,
            action_query_repo=self.mock_action_query_repo,
            activity_repo=self.mock_activity_repo,
            event_publisher=self.mock_event_publisher,
            authorization_service=self.mock_authorization_service
        )
        
        # Verify dependencies are stored (using reflection for testing)
        assert service.__dict__.get('_action_repo') is self.mock_action_repo
        assert service.__dict__.get('_action_query_repo') is self.mock_action_query_repo
        assert service.__dict__.get('_activity_repo') is self.mock_activity_repo
        assert service.__dict__.get('_event_publisher') is self.mock_event_publisher
        assert service.__dict__.get('_authorization_service') is self.mock_authorization_service

    def test_submit_action_repository_exception_handling(self):
        """Test handling of repository exceptions during action submission"""
        # Arrange
        self.mock_activity_repo.find_by_id.return_value = self.test_activity
        self.mock_action_repo.save.side_effect = Exception("Database connection error")
        
        # Act & Assert
        try:
            self.service.submit_action(self.valid_submit_command, self.mock_auth_context)
            assert False, "Should have raised Exception"
        except Exception as e:
            assert "Database connection error" in str(e)

    def test_get_pending_validations_repository_exception_handling(self):
        """Test handling of repository exceptions during pending validations retrieval"""
        # Arrange
        self.mock_action_query_repo.get_pending_validations.side_effect = Exception("Query service unavailable")
        
        # Act & Assert
        try:
            self.service.get_pending_validations(self.mock_auth_context)
            assert False, "Should have raised Exception"
        except Exception as e:
            assert "Query service unavailable" in str(e)

    def test_get_person_actions_repository_exception_handling(self):
        """Test handling of repository exceptions during person actions retrieval"""
        # Arrange
        self.mock_action_query_repo.get_person_actions.side_effect = Exception("Database error")
        
        # Act & Assert
        try:
            self.service.get_person_actions(self.valid_person_id, self.mock_auth_context)
            assert False, "Should have raised Exception"
        except Exception as e:
            assert "Database error" in str(e)

    def test_simulate_proof_validation_repository_exception_handling(self):
        """Test handling of repository exceptions during proof validation"""
        # Arrange
        self.mock_action_repo.find_by_id.return_value = self.test_action
        self.mock_event_publisher.publish.side_effect = Exception("Event publisher error")
        
        # Act & Assert
        try:
            self.service.simulate_proof_validation(self.valid_validate_command, self.mock_auth_context)
            assert False, "Should have raised Exception"
        except Exception as e:
            assert "Event publisher error" in str(e)

    def test_submit_multiple_actions_same_activity(self):
        """Test submitting multiple actions for the same activity"""
        # Arrange
        self.mock_activity_repo.find_by_id.return_value = self.test_activity
        
        commands = [
            SubmitActionCommand(
                personId=self.valid_person_id,  # Use the authenticated user's ID
                activityId=self.valid_activity_id,
                description="Action 1: Cleaned north section",
                proofHash="abc123def456789abc123def456789ab"
            ),
            SubmitActionCommand(
                personId=self.valid_person_id,  # Use the authenticated user's ID
                activityId=self.valid_activity_id,
                description="Action 2: Cleaned south section", 
                proofHash="def456789abc123def456789abc123de"
            ),
            SubmitActionCommand(
                personId=self.valid_person_id,  # Use the authenticated user's ID
                activityId=self.valid_activity_id,
                description="Action 3: Organized trash sorting",
                proofHash="123456789abcdef123456789abcdef12"
            )
        ]
        
        # Act
        results: List[ActionId] = []
        for command in commands:
            result = self.service.submit_action(command, self.mock_auth_context)
            results.append(result)
            assert isinstance(result, ActionId)
        
        # Assert
        assert len(results) == 3
        assert len(set(str(r) for r in results)) == 3  # All different IDs
        assert self.mock_action_repo.save.call_count == 3
        # Should find the same activity each time
        assert self.mock_activity_repo.find_by_id.call_count == 3

    def test_event_publisher_called_for_each_event(self):
        """Test that event publisher is called for each domain event"""
        # Arrange
        self.mock_activity_repo.find_by_id.return_value = self.test_activity
        
        # Create a mock action with multiple events
        mock_action = Mock()
        mock_action.action_id = self.valid_action_id
        mock_event1 = Mock()
        mock_event2 = Mock()
        mock_event3 = Mock()
        mock_action.domain_events = [mock_event1, mock_event2, mock_event3]
        mock_action.clear_domain_events = Mock()
        
        # Mock Action.submit to return our mock
        original_submit = Action.submit
        Action.submit = Mock(return_value=mock_action)
        
        try:
            # Act
            self.service.submit_action(self.valid_submit_command, self.mock_auth_context)
            
            # Assert
            assert self.mock_event_publisher.publish.call_count == 3
            self.mock_event_publisher.publish.assert_any_call(mock_event1)
            self.mock_event_publisher.publish.assert_any_call(mock_event2)
            self.mock_event_publisher.publish.assert_any_call(mock_event3)
            mock_action.clear_domain_events.assert_called_once()
            
        finally:
            # Restore original method
            Action.submit = original_submit

    def test_proof_validation_event_content(self):
        """Test that proof validation event contains correct data"""
        # Arrange
        test_action = Action.submit(
            action_id=ActionId.generate(),
            person_id=PersonId.generate(),
            activity_id=ActivityId.generate(),
            proof="Test proof content"
        )
        self.mock_action_repo.find_by_id.return_value = test_action
        
        validate_command = ValidateProofCommand(
            actionId=test_action.action_id,
            isValid=True
        )
        
        # Act
        self.service.simulate_proof_validation(validate_command, self.mock_auth_context)
        
        # Assert
        published_event = self.mock_event_publisher.publish.call_args[0][0]
        assert published_event.action_id == test_action.action_id
        assert published_event.person_id == test_action.person_id
        assert published_event.activity_id == test_action.activity_id
        assert published_event.is_valid == True

    def test_hash_formats_in_proof_combination(self):
        """Test different valid proof hash formats are properly combined"""
        # Arrange
        hash_formats = [
            "a1b2c3d4e5f67890a1b2c3d4e5f67890",  # 32 chars (MD5)
            "A1B2C3D4E5F67890A1B2C3D4E5F67890DEF456AB",  # 40 chars (SHA-1)
            "a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890",  # 64 chars (SHA-256)
            "A1B2C3D4E5F67890A1B2C3D4E5F67890A1B2C3D4E5F67890A1B2C3D4E5F67890A1B2C3D4E5F67890A1B2C3D4E5F67890A1B2C3D4E5F67890A1B2C3D4E5F67890",  # 128 chars (SHA-512)
            "fedcba9876543210fedcba9876543210"  # 32 chars (different pattern)
        ]
        
        self.mock_activity_repo.find_by_id.return_value = self.test_activity
        
        for i, hash_format in enumerate(hash_formats):
            command = SubmitActionCommand(
                personId=self.valid_person_id,  # Use the authenticated user's ID
                activityId=self.valid_activity_id,
                description=f"Test action {i+1}",
                proofHash=hash_format
            )
            
            # Act
            result = self.service.submit_action(command, self.mock_auth_context)
            
            # Assert
            assert isinstance(result, ActionId)
            saved_action = self.mock_action_repo.save.call_args[0][0]
            assert f"Test action {i+1}" in saved_action.proof
            assert hash_format in saved_action.proof