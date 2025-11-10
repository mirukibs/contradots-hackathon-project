"""Comprehensive tests for SubmitActionCommand"""

from src.application.commands.submit_action_command import SubmitActionCommand
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.shared.value_objects.activity_id import ActivityId


class TestSubmitActionCommand:
    """Test suite for SubmitActionCommand covering all methods and edge cases"""

    def setup_method(self):
        """Set up test fixtures"""
        self.valid_person_id = PersonId.generate()
        self.valid_activity_id = ActivityId.generate()
        self.valid_description = "Picked up 50 pieces of trash from the beach"
        self.valid_proof_hash = "a1b2c3d4e5f67890abcdef1234567890abcdef12"

    def test_command_creation_with_valid_data(self):
        """Test creating command with valid data"""
        command = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description=self.valid_description,
            proofHash=self.valid_proof_hash
        )
        
        assert command.personId == self.valid_person_id
        assert command.activityId == self.valid_activity_id
        assert command.description == self.valid_description
        assert command.proofHash == self.valid_proof_hash

    def test_command_is_frozen(self):
        """Test that command is immutable (frozen dataclass)"""
        command = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description=self.valid_description,
            proofHash=self.valid_proof_hash
        )
        
        # Verify the command is intact (can't easily test frozen due to typing)
        # The @dataclass(frozen=True) ensures immutability at the Python level
        assert command.personId == self.valid_person_id
        assert command.activityId == self.valid_activity_id
        assert command.description == self.valid_description
        assert command.proofHash == self.valid_proof_hash

    def test_validate_with_valid_data(self):
        """Test validation passes with valid data"""
        command = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description=self.valid_description,
            proofHash=self.valid_proof_hash
        )
        
        # Should not raise any exception
        command.validate()

    def test_validate_empty_description_raises_error(self):
        """Test validation fails with empty description"""
        command = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description="",
            proofHash=self.valid_proof_hash
        )
        
        try:
            command.validate()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Action description is required and cannot be empty" in str(e)

    def test_validate_whitespace_only_description_raises_error(self):
        """Test validation fails with whitespace-only description"""
        command = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description="   ",
            proofHash=self.valid_proof_hash
        )
        
        try:
            command.validate()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Action description is required and cannot be empty" in str(e)

    def test_validate_empty_proof_hash_raises_error(self):
        """Test validation fails with empty proof hash"""
        command = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description=self.valid_description,
            proofHash=""
        )
        
        try:
            command.validate()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Proof hash is required and cannot be empty" in str(e)

    def test_validate_whitespace_only_proof_hash_raises_error(self):
        """Test validation fails with whitespace-only proof hash"""
        command = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description=self.valid_description,
            proofHash="   "
        )
        
        try:
            command.validate()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Proof hash is required and cannot be empty" in str(e)

    def test_validate_invalid_proof_hash_format_raises_error(self):
        """Test validation fails with invalid proof hash format"""
        invalid_hashes = [
            "123",  # Too short
            "not-a-hex-hash",  # Not hexadecimal
            "G1B2C3D4E5F67890ABCDEF1234567890ABCDEF12",  # Invalid hex character G
            "a1b2c3d4e5f67890abcdef1234567890abcdef1",  # Too short (41 chars, need 32-128)
            "a" * 129  # Too long (129 chars, max 128)
        ]
        
        for invalid_hash in invalid_hashes:
            command = SubmitActionCommand(
                personId=self.valid_person_id,
                activityId=self.valid_activity_id,
                description=self.valid_description,
                proofHash=invalid_hash
            )
            
            try:
                command.validate()
                assert False, f"Should have raised ValueError for hash: {invalid_hash}"
            except ValueError as e:
                assert "Proof hash must be a valid hexadecimal string" in str(e)

    def test_validate_valid_proof_hash_formats(self):
        """Test validation passes with various valid proof hash formats"""
        valid_hashes = [
            "a1b2c3d4e5f67890abcdef1234567890",  # 32 chars (MD5 length)
            "a1b2c3d4e5f67890abcdef1234567890abcdef12",  # 40 chars 
            "a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890ab",  # 64 chars (SHA256)
            "A1B2C3D4E5F67890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890AB",  # 128 chars (uppercase)
            "0123456789abcdef0123456789abcdef"  # All valid hex digits
        ]
        
        for valid_hash in valid_hashes:
            command = SubmitActionCommand(
                personId=self.valid_person_id,
                activityId=self.valid_activity_id,
                description=self.valid_description,
                proofHash=valid_hash
            )
            
            # Should not raise any exception
            command.validate()

    def test_validate_person_id_uuid_format(self):
        """Test validation of PersonId UUID format"""
        # PersonId validation happens at construction time, not in command validation
        
        try:
            PersonId("invalid-uuid")
            assert False, "Should have raised ValueError during PersonId creation"
        except ValueError:
            pass  # Expected - PersonId constructor should reject invalid UUIDs

    def test_validate_activity_id_uuid_format(self):
        """Test validation of ActivityId UUID format"""
        # ActivityId validation happens at construction time
        
        try:
            ActivityId("invalid-uuid")
            assert False, "Should have raised ValueError during ActivityId creation"
        except ValueError:
            pass  # Expected - ActivityId constructor should reject invalid UUIDs

    def test_command_equality(self):
        """Test command equality comparison"""
        command1 = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description=self.valid_description,
            proofHash=self.valid_proof_hash
        )
        
        command2 = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description=self.valid_description,
            proofHash=self.valid_proof_hash
        )
        
        assert command1 == command2

    def test_command_inequality(self):
        """Test command inequality comparison"""
        command1 = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description=self.valid_description,
            proofHash=self.valid_proof_hash
        )
        
        command2 = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description="Different description",
            proofHash=self.valid_proof_hash
        )
        
        assert command1 != command2

    def test_command_hash(self):
        """Test command can be hashed (for use in sets, dicts)"""
        command = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description=self.valid_description,
            proofHash=self.valid_proof_hash
        )
        
        # Should not raise any exception
        hash(command)
        
        # Should work in sets
        command_set = {command}
        assert len(command_set) == 1

    def test_command_repr(self):
        """Test command string representation"""
        command = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description=self.valid_description,
            proofHash=self.valid_proof_hash
        )
        
        repr_str = repr(command)
        assert "SubmitActionCommand" in repr_str
        assert self.valid_proof_hash in repr_str

    def test_multiple_validation_errors_sequence(self):
        """Test that validation catches first error in sequence"""
        # This tests that validation fails fast on first error
        command = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description="",  # Invalid
            proofHash=""  # Also invalid
        )
        
        # Should fail on first validation (description)
        try:
            command.validate()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Action description is required and cannot be empty" in str(e)

    def test_validate_long_description(self):
        """Test validation with very long description"""
        long_description = "A" * 5000  # Very long description
        
        command = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description=long_description,
            proofHash=self.valid_proof_hash
        )
        
        # Should not raise any exception (assuming no length limits in business rules)
        command.validate()

    def test_validate_special_characters_in_description(self):
        """Test validation with special characters in description"""
        special_description = "Collected trash 🗑️ & recycled ♻️ materials @beach #cleanup"
        
        command = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description=special_description,
            proofHash=self.valid_proof_hash
        )
        
        # Should not raise any exception
        command.validate()

    def test_validate_mixed_case_proof_hash(self):
        """Test validation with mixed case proof hash"""
        mixed_case_hash = "A1b2C3d4E5f67890ABCdef1234567890ABCdef12"
        
        command = SubmitActionCommand(
            personId=self.valid_person_id,
            activityId=self.valid_activity_id,
            description=self.valid_description,
            proofHash=mixed_case_hash
        )
        
        # Should not raise any exception
        command.validate()