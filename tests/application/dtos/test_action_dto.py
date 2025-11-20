"""Comprehensive tests for ActionDto"""

from src.application.dtos.action_dto import ActionDto


class TestActionDto:
    """Test suite for ActionDto covering all methods and edge cases"""

    def setup_method(self):
        """Set up test fixtures"""
        self.valid_action_id = "550e8400-e29b-41d4-a716-446655440002"
        self.valid_person_name = "John Doe"
        self.valid_activity_name = "Beach Cleanup Drive"
        self.valid_description = "Collected 50 pieces of trash from the beach"
        self.valid_status = "pending"
        self.valid_submitted_at = "2024-01-15T14:30:00Z"

    def test_dto_creation_with_valid_data(self):
        """Test creating DTO with valid data"""
        dto = ActionDto(
            actionId=self.valid_action_id,
            personName=self.valid_person_name,
            activityName=self.valid_activity_name,
            description=self.valid_description,
            status=self.valid_status,
            submittedAt=self.valid_submitted_at
        )
        
        assert dto.actionId == self.valid_action_id
        assert dto.personName == self.valid_person_name
        assert dto.activityName == self.valid_activity_name
        assert dto.description == self.valid_description
        assert dto.status == self.valid_status
        assert dto.submittedAt == self.valid_submitted_at

    def test_to_dict_conversion(self):
        """Test conversion to dictionary"""
        dto = ActionDto(
            actionId=self.valid_action_id,
            personName=self.valid_person_name,
            activityName=self.valid_activity_name,
            description=self.valid_description,
            status=self.valid_status,
            submittedAt=self.valid_submitted_at
        )
        
        result_dict = dto.to_dict()
        
        expected_dict = {
            'actionId': self.valid_action_id,
            'personName': self.valid_person_name,
            'activityName': self.valid_activity_name,
            'description': self.valid_description,
            'status': self.valid_status,
            'submittedAt': self.valid_submitted_at
        }
        
        assert result_dict == expected_dict

    def test_dto_with_different_statuses(self):
        """Test DTO with different action statuses"""
        statuses = ["pending", "validated", "rejected"]
        
        for status in statuses:
            dto = ActionDto(
                actionId=self.valid_action_id,
                personName=self.valid_person_name,
                activityName=self.valid_activity_name,
                description=self.valid_description,
                status=status,
                submittedAt=self.valid_submitted_at
            )
            assert dto.status == status

    def test_dto_equality(self):
        """Test DTO equality comparison"""
        dto1 = ActionDto(
            actionId=self.valid_action_id,
            personName=self.valid_person_name,
            activityName=self.valid_activity_name,
            description=self.valid_description,
            status=self.valid_status,
            submittedAt=self.valid_submitted_at
        )
        
        dto2 = ActionDto(
            actionId=self.valid_action_id,
            personName=self.valid_person_name,
            activityName=self.valid_activity_name,
            description=self.valid_description,
            status=self.valid_status,
            submittedAt=self.valid_submitted_at
        )
        
        assert dto1 == dto2

    def test_dto_inequality(self):
        """Test DTO inequality comparison"""
        dto1 = ActionDto(
            actionId=self.valid_action_id,
            personName=self.valid_person_name,
            activityName=self.valid_activity_name,
            description=self.valid_description,
            status="pending",
            submittedAt=self.valid_submitted_at
        )
        
        dto2 = ActionDto(
            actionId=self.valid_action_id,
            personName=self.valid_person_name,
            activityName=self.valid_activity_name,
            description=self.valid_description,
            status="validated",  # Different status
            submittedAt=self.valid_submitted_at
        )
        
        assert dto1 != dto2

    def test_dto_field_types(self):
        """Test that DTO fields have correct types"""
        dto = ActionDto(
            actionId=self.valid_action_id,
            personName=self.valid_person_name,
            activityName=self.valid_activity_name,
            description=self.valid_description,
            status=self.valid_status,
            submittedAt=self.valid_submitted_at
        )
        
        assert isinstance(dto.actionId, str)
        assert isinstance(dto.personName, str)
        assert isinstance(dto.activityName, str)
        assert isinstance(dto.description, str)
        assert isinstance(dto.status, str)
        assert isinstance(dto.submittedAt, str)

    def test_serialization_deserialization_round_trip(self):
        """Test that DTO can be serialized and deserialized consistently"""
        original_dto = ActionDto(
            actionId=self.valid_action_id,
            personName=self.valid_person_name,
            activityName=self.valid_activity_name,
            description=self.valid_description,
            status=self.valid_status,
            submittedAt=self.valid_submitted_at
        )
        
        # Convert to dict (serialization)
        dto_dict = original_dto.to_dict()
        
        # Recreate from dict (deserialization)
        recreated_dto = ActionDto(
            actionId=dto_dict['actionId'],
            personName=dto_dict['personName'],
            activityName=dto_dict['activityName'],
            description=dto_dict['description'],
            status=dto_dict['status'],
            submittedAt=dto_dict['submittedAt']
        )
        
        assert original_dto == recreated_dto

    def test_dto_hash(self):
        """Test DTO can be hashed"""
        dto = ActionDto(
            actionId=self.valid_action_id,
            personName=self.valid_person_name,
            activityName=self.valid_activity_name,
            description=self.valid_description,
            status=self.valid_status,
            submittedAt=self.valid_submitted_at
        )
        
        # Should not raise any exception
        hash(dto)
        
        # Should work in sets
        dto_set = {dto}
        assert len(dto_set) == 1

    def test_dto_with_special_characters(self):
        """Test DTO with special characters"""
        special_person = "José María O'Connor"
        special_activity = "Beach Cleanup & Conservation 🌊"
        special_description = "Cleaned beach area @ Sunset Point (2hrs work)"
        
        dto = ActionDto(
            actionId=self.valid_action_id,
            personName=special_person,
            activityName=special_activity,
            description=special_description,
            status=self.valid_status,
            submittedAt=self.valid_submitted_at
        )
        
        assert dto.personName == special_person
        assert dto.activityName == special_activity
        assert dto.description == special_description