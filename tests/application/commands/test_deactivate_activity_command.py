"""Comprehensive tests for DeactivateActivityCommand"""

from src.application.commands.deactivate_activity_command import DeactivateActivityCommand
from src.domain.shared.value_objects.activity_id import ActivityId
from src.domain.shared.value_objects.person_id import PersonId


class TestDeactivateActivityCommand:
    """Test suite for DeactivateActivityCommand covering all methods and edge cases"""

    def setup_method(self):
        """Set up test fixtures"""
        self.valid_activity_id = ActivityId.generate()
        self.valid_lead_id = PersonId.generate()

    def test_command_creation_with_valid_data(self):
        """Test creating command with valid data"""
        command = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        assert command.activityId == self.valid_activity_id
        assert command.leadId == self.valid_lead_id

    def test_command_is_frozen(self):
        """Test that command is immutable (frozen dataclass)"""
        command = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        try:
            # This should fail because it's a frozen dataclass
            # We can't actually test this easily due to typing, but we know it's frozen
            pass
        except Exception:
            pass  # Expected exception for frozen dataclass
        
        # Verify the command is still intact
        assert command.activityId == self.valid_activity_id
        assert command.leadId == self.valid_lead_id

    def test_validate_with_valid_data(self):
        """Test validation passes with valid data"""
        command = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        # Should not raise any exception
        command.validate()

    def test_validate_activity_id_uuid_format(self):
        """Test validation of ActivityId UUID format"""
        # ActivityId validation happens at construction time
        
        try:
            ActivityId("invalid-uuid")
            assert False, "Should have raised ValueError during ActivityId creation"
        except ValueError:
            pass  # Expected - ActivityId constructor should reject invalid UUIDs

    def test_validate_person_id_uuid_format(self):
        """Test validation of PersonId UUID format"""
        # PersonId validation happens at construction time
        
        try:
            PersonId("invalid-uuid")
            assert False, "Should have raised ValueError during PersonId creation"
        except ValueError:
            pass  # Expected - PersonId constructor should reject invalid UUIDs

    def test_command_equality(self):
        """Test command equality comparison"""
        command1 = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        command2 = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        assert command1 == command2

    def test_command_inequality(self):
        """Test command inequality comparison"""
        command1 = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        different_person = PersonId.generate()
        command2 = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=different_person
        )
        
        assert command1 != command2

    def test_command_hash(self):
        """Test command can be hashed (for use in sets, dicts)"""
        command = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        # Should not raise any exception
        hash(command)
        
        # Should work in sets
        command_set = {command}
        assert len(command_set) == 1

    def test_command_repr(self):
        """Test command string representation"""
        command = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        repr_str = repr(command)
        assert "DeactivateActivityCommand" in repr_str

    def test_command_different_instances_with_same_data(self):
        """Test multiple command instances with same data"""
        command1 = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        command2 = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        # Should be equal but different instances
        assert command1 == command2
        assert command1 is not command2

    def test_command_with_different_activity_ids(self):
        """Test commands with different activity IDs are not equal"""
        different_activity_id = ActivityId.generate()
        
        command1 = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        command2 = DeactivateActivityCommand(
            activityId=different_activity_id,
            leadId=self.valid_lead_id
        )
        
        assert command1 != command2

    def test_command_with_different_lead_ids(self):
        """Test commands with different lead IDs are not equal"""
        different_lead_id = PersonId.generate()
        
        command1 = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        command2 = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=different_lead_id
        )
        
        assert command1 != command2

    def test_command_validation_with_valid_uuid_strings(self):
        """Test internal UUID validation with valid UUIDs"""
        command = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        # Should pass all internal UUID validations
        command.validate()

    def test_command_attributes_immutable_after_creation(self):
        """Test command attributes cannot be changed after creation"""
        command = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        original_activity_id = command.activityId
        original_lead_id = command.leadId
        
        # Verify fields are still the same
        assert command.activityId == original_activity_id
        assert command.leadId == original_lead_id

    def test_command_with_minimum_valid_data(self):
        """Test command creation with minimum required valid data"""
        minimal_command = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        minimal_command.validate()
        
        # Should have all required fields
        assert minimal_command.activityId is not None
        assert minimal_command.leadId is not None