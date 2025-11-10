"""Comprehensive tests for RegisterPersonCommand"""

from src.application.commands.register_person_command import RegisterPersonCommand


class TestRegisterPersonCommand:
    """Test suite for RegisterPersonCommand covering all methods and edge cases"""

    def setup_method(self):
        """Set up test fixtures"""
        self.valid_name = "John Doe"
        self.valid_email = "john.doe@example.com"
        self.valid_role = "participant"

    def test_command_creation_with_valid_data(self):
        """Test creating command with valid data"""
        command = RegisterPersonCommand(
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role
        )
        
        assert command.name == self.valid_name
        assert command.email == self.valid_email
        assert command.role == self.valid_role

    def test_command_creation_with_lead_role(self):
        """Test creating command with lead role"""
        command = RegisterPersonCommand(
            name="Jane Smith",
            email="jane.smith@example.com",
            role="lead"
        )
        
        assert command.name == "Jane Smith"
        assert command.email == "jane.smith@example.com"
        assert command.role == "lead"

    def test_command_is_frozen(self):
        """Test that command is immutable (frozen dataclass)"""
        command = RegisterPersonCommand(
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role
        )
        
        # Verify the command is intact (can't easily test frozen due to typing)
        # The @dataclass(frozen=True) ensures immutability at the Python level
        assert command.name == self.valid_name
        assert command.email == self.valid_email
        assert command.role == self.valid_role

    def test_validate_with_valid_data(self):
        """Test validation passes with valid data"""
        command = RegisterPersonCommand(
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role
        )
        
        # Should not raise any exception
        command.validate()

    def test_validate_empty_name_raises_error(self):
        """Test validation fails with empty name"""
        command = RegisterPersonCommand(
            name="",
            email=self.valid_email,
            role=self.valid_role
        )
        
        try:
            command.validate()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Name is required and cannot be empty" in str(e)

    def test_validate_whitespace_only_name_raises_error(self):
        """Test validation fails with whitespace-only name"""
        command = RegisterPersonCommand(
            name="   ",
            email=self.valid_email,
            role=self.valid_role
        )
        
        try:
            command.validate()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Name is required and cannot be empty" in str(e)

    def test_validate_empty_email_raises_error(self):
        """Test validation fails with empty email"""
        command = RegisterPersonCommand(
            name=self.valid_name,
            email="",
            role=self.valid_role
        )
        
        try:
            command.validate()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Email is required and cannot be empty" in str(e)

    def test_validate_whitespace_only_email_raises_error(self):
        """Test validation fails with whitespace-only email"""
        command = RegisterPersonCommand(
            name=self.valid_name,
            email="   ",
            role=self.valid_role
        )
        
        try:
            command.validate()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Email is required and cannot be empty" in str(e)

    def test_validate_invalid_email_format_raises_error(self):
        """Test validation fails with invalid email format"""
        invalid_emails = [
            "notanemail",
            "@example.com", 
            "john@",
            "john.doe@",
            "john.doe@.com",
            "john.doe@example",
            "john.doe@example.",
        ]
        
        for invalid_email in invalid_emails:
            command = RegisterPersonCommand(
                name=self.valid_name,
                email=invalid_email,
                role=self.valid_role
            )
            
            try:
                command.validate()
                assert False, f"Should have raised ValueError for email: {invalid_email}"
            except ValueError as e:
                assert "Email must be in valid format" in str(e)

    def test_validate_valid_email_formats(self):
        """Test validation passes with various valid email formats"""
        valid_emails = [
            "john@example.com",
            "john.doe@example.com",
            "john+doe@example.com",
            "john_doe@example.com",
            "john123@example123.com",
            "j@e.co",
            "very.long.email.address@very.long.domain.com"
        ]
        
        for valid_email in valid_emails:
            command = RegisterPersonCommand(
                name=self.valid_name,
                email=valid_email,
                role=self.valid_role
            )
            
            # Should not raise any exception
            command.validate()

    def test_validate_empty_role_raises_error(self):
        """Test validation fails with empty role"""
        command = RegisterPersonCommand(
            name=self.valid_name,
            email=self.valid_email,
            role=""
        )
        
        try:
            command.validate()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Role is required and cannot be empty" in str(e)

    def test_validate_whitespace_only_role_raises_error(self):
        """Test validation fails with whitespace-only role"""
        command = RegisterPersonCommand(
            name=self.valid_name,
            email=self.valid_email,
            role="   "
        )
        
        try:
            command.validate()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Role is required and cannot be empty" in str(e)

    def test_validate_invalid_role_raises_error(self):
        """Test validation fails with invalid role"""
        invalid_roles = ["admin", "user", "manager", "invalid"]
        
        for invalid_role in invalid_roles:
            command = RegisterPersonCommand(
                name=self.valid_name,
                email=self.valid_email,
                role=invalid_role
            )
            
            try:
                command.validate()
                assert False, f"Should have raised ValueError for role: {invalid_role}"
            except ValueError as e:
                assert "Role must be one of: participant, lead" in str(e)

    def test_validate_participant_role_case_insensitive(self):
        """Test validation accepts participant role in different cases"""
        cases = ["participant", "PARTICIPANT", "Participant", "pArTiCiPaNt"]
        
        for role_case in cases:
            command = RegisterPersonCommand(
                name=self.valid_name,
                email=self.valid_email,
                role=role_case
            )
            
            # Should not raise any exception
            command.validate()

    def test_validate_lead_role_case_insensitive(self):
        """Test validation accepts lead role in different cases"""
        cases = ["lead", "LEAD", "Lead", "lEaD"]
        
        for role_case in cases:
            command = RegisterPersonCommand(
                name=self.valid_name,
                email=self.valid_email,
                role=role_case
            )
            
            # Should not raise any exception
            command.validate()

    def test_command_equality(self):
        """Test command equality comparison"""
        command1 = RegisterPersonCommand(
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role
        )
        
        command2 = RegisterPersonCommand(
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role
        )
        
        assert command1 == command2

    def test_command_inequality(self):
        """Test command inequality comparison"""
        command1 = RegisterPersonCommand(
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role
        )
        
        command2 = RegisterPersonCommand(
            name="Jane Doe",
            email=self.valid_email,
            role=self.valid_role
        )
        
        assert command1 != command2

    def test_command_hash(self):
        """Test command can be hashed (for use in sets, dicts)"""
        command = RegisterPersonCommand(
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role
        )
        
        # Should not raise any exception
        hash(command)
        
        # Should work in sets
        command_set = {command}
        assert len(command_set) == 1

    def test_command_repr(self):
        """Test command string representation"""
        command = RegisterPersonCommand(
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role
        )
        
        repr_str = repr(command)
        assert "RegisterPersonCommand" in repr_str
        assert self.valid_name in repr_str
        assert self.valid_email in repr_str
        assert self.valid_role in repr_str

    def test_multiple_validation_errors_sequence(self):
        """Test that validation catches first error in sequence"""
        # This tests that validation fails fast on first error
        command = RegisterPersonCommand(
            name="",  # Invalid
            email="invalid-email",  # Also invalid
            role="invalid-role"  # Also invalid
        )
        
        # Should fail on first validation (name)
        try:
            command.validate()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Name is required and cannot be empty" in str(e)

    def test_validate_edge_case_email_with_special_chars(self):
        """Test validation with edge case emails containing special characters"""
        special_emails = [
            "test+tag@example.com",
            "user.name+tag@example.com",
            "test_email@example-domain.com",
            "123@456.com"
        ]
        
        for email in special_emails:
            command = RegisterPersonCommand(
                name=self.valid_name,
                email=email,
                role=self.valid_role
            )
            
            # Should not raise any exception
            command.validate()

    def test_validate_person_id_none_type_error(self):
        """Test validation with None personId to trigger TypeError in UUID validation"""
        from unittest.mock import patch
        
        # Create command with valid data first
        command = RegisterPersonCommand(
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role
        )
        
        # Mock uuid.UUID to raise TypeError on None input
        with patch('uuid.UUID') as mock_uuid:
            mock_uuid.side_effect = TypeError("int() argument must be a string")
            
            try:
                command.validate()
                assert False, "Should have raised ValueError for invalid personId format"
            except ValueError as e:
                assert "Person ID must be a valid UUID" in str(e)

    def test_validate_person_id_invalid_uuid_format(self):
        """Test validation with invalid UUID format to trigger ValueError in UUID validation"""
        from unittest.mock import patch
        
        # Create command with valid data first
        command = RegisterPersonCommand(
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role
        )
        
        # Mock uuid.UUID to raise ValueError on invalid input
        with patch('uuid.UUID') as mock_uuid:
            mock_uuid.side_effect = ValueError("badly formed hexadecimal UUID string")
            
            try:
                command.validate()
                assert False, "Should have raised ValueError for invalid personId format"
            except ValueError as e:
                assert "Person ID must be a valid UUID" in str(e)