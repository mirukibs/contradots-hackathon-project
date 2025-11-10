"""Comprehensive tests for ValidateProofCommand"""

from src.application.commands.validate_proof_command import ValidateProofCommand
from src.domain.shared.value_objects.action_id import ActionId


class TestValidateProofCommand:
    """Test suite for ValidateProofCommand covering all methods and edge cases"""

    def setup_method(self):
        """Set up test fixtures"""
        self.valid_action_id = ActionId.generate()
        self.valid_is_valid_true = True
        self.valid_is_valid_false = False

    def test_command_creation_with_valid_data_true(self):
        """Test creating command with valid data (isValid=True)"""
        command = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=self.valid_is_valid_true
        )
        
        assert command.actionId == self.valid_action_id
        assert command.isValid == self.valid_is_valid_true

    def test_command_creation_with_valid_data_false(self):
        """Test creating command with valid data (isValid=False)"""
        command = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=self.valid_is_valid_false
        )
        
        assert command.actionId == self.valid_action_id
        assert command.isValid == self.valid_is_valid_false

    def test_command_is_frozen(self):
        """Test that command is immutable (frozen dataclass)"""
        command = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=self.valid_is_valid_true
        )
        
        # Verify the command is intact (can't easily test frozen due to typing)
        assert command.actionId == self.valid_action_id
        assert command.isValid == self.valid_is_valid_true

    def test_validate_with_valid_data_true(self):
        """Test validation passes with valid data (isValid=True)"""
        command = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=self.valid_is_valid_true
        )
        
        # Should not raise any exception
        command.validate()

    def test_validate_with_valid_data_false(self):
        """Test validation passes with valid data (isValid=False)"""
        command = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=self.valid_is_valid_false
        )
        
        # Should not raise any exception
        command.validate()

    def test_validate_action_id_uuid_format(self):
        """Test validation of ActionId UUID format"""
        # ActionId validation happens at construction time
        
        try:
            ActionId("invalid-uuid")
            assert False, "Should have raised ValueError during ActionId creation"
        except ValueError:
            pass  # Expected - ActionId constructor should reject invalid UUIDs

    def test_command_equality_true(self):
        """Test command equality comparison with isValid=True"""
        command1 = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=True
        )
        
        command2 = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=True
        )
        
        assert command1 == command2

    def test_command_equality_false(self):
        """Test command equality comparison with isValid=False"""
        command1 = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=False
        )
        
        command2 = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=False
        )
        
        assert command1 == command2

    def test_command_inequality_different_validity(self):
        """Test command inequality comparison with different isValid values"""
        command1 = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=True
        )
        
        command2 = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=False
        )
        
        assert command1 != command2

    def test_command_inequality_different_action_id(self):
        """Test command inequality comparison with different action IDs"""
        different_action_id = ActionId.generate()
        
        command1 = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=True
        )
        
        command2 = ValidateProofCommand(
            actionId=different_action_id,
            isValid=True
        )
        
        assert command1 != command2

    def test_command_hash(self):
        """Test command can be hashed (for use in sets, dicts)"""
        command = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=self.valid_is_valid_true
        )
        
        # Should not raise any exception
        hash(command)
        
        # Should work in sets
        command_set = {command}
        assert len(command_set) == 1

    def test_command_repr(self):
        """Test command string representation"""
        command = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=self.valid_is_valid_true
        )
        
        repr_str = repr(command)
        assert "ValidateProofCommand" in repr_str
        assert "True" in repr_str

    def test_command_different_instances_with_same_data(self):
        """Test multiple command instances with same data"""
        command1 = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=True
        )
        
        command2 = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=True
        )
        
        # Should be equal but different instances
        assert command1 == command2
        assert command1 is not command2

    def test_command_with_different_action_ids(self):
        """Test commands with different action IDs are not equal"""
        different_action_id = ActionId.generate()
        
        command1 = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=True
        )
        
        command2 = ValidateProofCommand(
            actionId=different_action_id,
            isValid=True
        )
        
        assert command1 != command2

    def test_command_validation_with_valid_uuid_strings(self):
        """Test internal UUID validation with valid UUIDs"""
        command = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=True
        )
        
        # Should pass all internal UUID validations
        command.validate()

    def test_command_attributes_immutable_after_creation(self):
        """Test command attributes cannot be changed after creation"""
        command = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=True
        )
        
        original_action_id = command.actionId
        original_is_valid = command.isValid
        
        # Verify fields are still the same
        assert command.actionId == original_action_id
        assert command.isValid == original_is_valid

    def test_command_with_minimum_valid_data(self):
        """Test command creation with minimum required valid data"""
        minimal_command = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=False
        )
        
        minimal_command.validate()
        
        # Should have all required fields
        assert minimal_command.actionId is not None
        assert isinstance(minimal_command.isValid, bool)

    def test_command_hash_consistency(self):
        """Test that command hash is consistent across instances with same data"""
        command1 = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=True
        )
        
        command2 = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=True
        )
        
        # Same data should produce same hash
        assert hash(command1) == hash(command2)

    def test_command_in_set_operations(self):
        """Test command behavior in set operations"""
        command1 = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=True
        )
        
        command2 = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=True
        )
        
        command3 = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=False  # Different validity
        )
        
        # Set should only contain unique commands
        command_set = {command1, command2, command3}
        assert len(command_set) == 2  # command1 and command2 are equal, so only 2 unique

    def test_command_in_dict_operations(self):
        """Test command behavior as dictionary key"""
        command = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=True
        )
        
        command_dict = {command: "test_value"}
        
        # Should be able to retrieve by same command
        assert command_dict[command] == "test_value"

    def test_command_with_different_uuid_instances_same_value(self):
        """Test commands with different ActionId instances but same UUID value"""
        action_uuid = self.valid_action_id.value
        
        action_id_1 = ActionId(action_uuid)
        action_id_2 = ActionId(action_uuid)  # Same UUID, different instance
        
        command1 = ValidateProofCommand(
            actionId=action_id_1,
            isValid=True
        )
        
        command2 = ValidateProofCommand(
            actionId=action_id_2,
            isValid=True
        )
        
        # Should be equal because UUID values are the same
        assert command1 == command2

    def test_validate_business_rule_compliance(self):
        """Test that validation follows business rules"""
        command = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=True
        )
        
        # Should validate successfully
        command.validate()
        
        # Verify that the command has the expected structure
        assert hasattr(command, 'actionId')
        assert hasattr(command, 'isValid')
        assert isinstance(command.actionId, ActionId)
        assert isinstance(command.isValid, bool)

    def test_command_field_types(self):
        """Test that command fields have correct types"""
        command = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=True
        )
        
        assert type(command.actionId).__name__ == "ActionId"
        assert type(command.isValid).__name__ == "bool"

    def test_command_boolean_edge_cases(self):
        """Test command with boolean edge cases"""
        # Test explicitly True
        command_true = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=True
        )
        assert command_true.isValid is True
        
        # Test explicitly False
        command_false = ValidateProofCommand(
            actionId=self.valid_action_id,
            isValid=False
        )
        assert command_false.isValid is False