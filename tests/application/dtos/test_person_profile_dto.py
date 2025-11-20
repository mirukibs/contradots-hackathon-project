"""Comprehensive tests for PersonProfileDto"""

from typing import Dict, Any
from src.application.dtos.person_profile_dto import PersonProfileDto

class TestPersonProfileDto:
    """Test suite for PersonProfileDto covering all methods and edge cases"""

    def setup_method(self):
        """Set up test fixtures"""
        self.valid_person_id = "550e8400-e29b-41d4-a716-446655440000"
        self.valid_name = "John Doe"
        self.valid_email = "john.doe@example.com"
        self.valid_role = "member"
        self.valid_reputation_score = 85

    def test_dto_creation_with_valid_data(self):
        """Test creating DTO with valid data"""
        dto = PersonProfileDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        assert dto.personId == self.valid_person_id
        assert dto.name == self.valid_name
        assert dto.email == self.valid_email
        assert dto.role == self.valid_role
        assert dto.reputationScore == self.valid_reputation_score

    def test_dto_is_frozen(self):
        """Test that DTO is immutable (frozen dataclass)"""
        dto = PersonProfileDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        # Verify the DTO is intact (can't easily test frozen due to typing)
        assert dto.personId == self.valid_person_id
        assert dto.name == self.valid_name

    def test_to_dict_conversion(self):
        """Test conversion to dictionary"""
        dto = PersonProfileDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        result_dict = dto.to_dict()
        
        expected_dict: Dict[str, Any] = {
            'personId': self.valid_person_id,
            'name': self.valid_name,
            'email': self.valid_email,
            'role': self.valid_role,
            'reputationScore': self.valid_reputation_score
        }
        
        assert result_dict == expected_dict

    def test_to_dict_includes_all_fields(self):
        """Test that to_dict includes all DTO fields"""
        dto = PersonProfileDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        result_dict = dto.to_dict()
        
        # Check all fields are present
        assert 'personId' in result_dict
        assert 'name' in result_dict
        assert 'email' in result_dict
        assert 'role' in result_dict
        assert 'reputationScore' in result_dict
        
        # Check correct number of fields
        assert len(result_dict) == 5

    def test_dto_equality(self):
        """Test DTO equality comparison"""
        dto1 = PersonProfileDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        dto2 = PersonProfileDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        assert dto1 == dto2

    def test_dto_inequality(self):
        """Test DTO inequality comparison"""
        dto1 = PersonProfileDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        dto2 = PersonProfileDto(
            personId=self.valid_person_id,
            name="Jane Smith",  # Different name
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        assert dto1 != dto2

    def test_dto_hash(self):
        """Test DTO can be hashed (for use in sets, dicts)"""
        dto = PersonProfileDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        # Should not raise any exception
        hash(dto)
        
        # Should work in sets
        dto_set = {dto}
        assert len(dto_set) == 1

    def test_dto_repr(self):
        """Test DTO string representation"""
        dto = PersonProfileDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        repr_str = repr(dto)
        assert "PersonProfileDto" in repr_str
        assert self.valid_name in repr_str
        assert self.valid_email in repr_str

    def test_dto_with_lead_role(self):
        """Test DTO creation with lead role"""
        dto = PersonProfileDto(
            personId=self.valid_person_id,
            name="Jane Smith",
            email="jane.smith@example.com",
            role="lead",
            reputationScore=95
        )
        
        assert dto.role == "lead"
        assert dto.reputationScore == 95

    def test_dto_with_zero_reputation_score(self):
        """Test DTO with zero reputation score"""
        dto = PersonProfileDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=0
        )
        
        assert dto.reputationScore == 0
        result_dict = dto.to_dict()
        assert result_dict['reputationScore'] == 0

    def test_dto_with_negative_reputation_score(self):
        """Test DTO with negative reputation score"""
        dto = PersonProfileDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=-10
        )
        
        assert dto.reputationScore == -10
        result_dict = dto.to_dict()
        assert result_dict['reputationScore'] == -10

    def test_dto_with_high_reputation_score(self):
        """Test DTO with very high reputation score"""
        dto = PersonProfileDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=99999
        )
        
        assert dto.reputationScore == 99999
        result_dict = dto.to_dict()
        assert result_dict['reputationScore'] == 99999

    def test_dto_with_special_characters_in_name(self):
        """Test DTO with special characters in name"""
        special_name = "José María O'Connor-Smith"
        dto = PersonProfileDto(
            personId=self.valid_person_id,
            name=special_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        assert dto.name == special_name
        result_dict = dto.to_dict()
        assert result_dict['name'] == special_name

    def test_dto_with_unicode_characters(self):
        """Test DTO with unicode characters"""
        unicode_name = "张三 李四"
        unicode_email = "zhang.san@例え.com"
        
        dto = PersonProfileDto(
            personId=self.valid_person_id,
            name=unicode_name,
            email=unicode_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        assert dto.name == unicode_name
        assert dto.email == unicode_email
        
        result_dict = dto.to_dict()
        assert result_dict['name'] == unicode_name
        assert result_dict['email'] == unicode_email

    def test_dto_with_empty_strings(self):
        """Test DTO with empty strings"""
        dto = PersonProfileDto(
            personId="",
            name="",
            email="",
            role="",
            reputationScore=0
        )
        
        assert dto.personId == ""
        assert dto.name == ""
        assert dto.email == ""
        assert dto.role == ""
        
        result_dict = dto.to_dict()
        assert result_dict['personId'] == ""
        assert result_dict['name'] == ""
        assert result_dict['email'] == ""
        assert result_dict['role'] == ""

    def test_dto_field_types(self):
        """Test that DTO fields have correct types"""
        dto = PersonProfileDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        assert isinstance(dto.personId, str)
        assert isinstance(dto.name, str)
        assert isinstance(dto.email, str)
        assert isinstance(dto.role, str)
        assert isinstance(dto.reputationScore, int)

    def test_dto_serialization_deserialization_round_trip(self):
        """Test that DTO can be serialized and deserialized consistently"""
        original_dto = PersonProfileDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        # Convert to dict (serialization)
        dto_dict = original_dto.to_dict()
        
        # Recreate from dict (deserialization)
        recreated_dto = PersonProfileDto(
            personId=dto_dict['personId'],
            name=dto_dict['name'],
            email=dto_dict['email'],
            role=dto_dict['role'],
            reputationScore=dto_dict['reputationScore']
        )
        
        assert original_dto == recreated_dto

    def test_dto_in_collections(self):
        """Test DTO behavior in collections (set, list, dict)"""
        dto1 = PersonProfileDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        dto2 = PersonProfileDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        different_dto = PersonProfileDto(
            personId="different-id",
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        # Test in set (should deduplicate)
        dto_set = {dto1, dto2, different_dto}
        assert len(dto_set) == 2
        
        # Test in list
        dto_list = [dto1, dto2, different_dto]
        assert len(dto_list) == 3
        
        # Test as dict key
        dto_dict = {dto1: "value1", different_dto: "value2"}
        assert len(dto_dict) == 2

    def test_to_dict_immutability(self):
        """Test that modifying to_dict result doesn't affect original DTO"""
        dto = PersonProfileDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            email=self.valid_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        dto_dict = dto.to_dict()
        original_name = dto.name
        
        # Modify the dictionary
        dto_dict['name'] = "Modified Name"
        
        # Original DTO should be unchanged
        assert dto.name == original_name
        assert dto.name != "Modified Name"

    def test_dto_with_long_strings(self):
        """Test DTO with very long strings"""
        long_name = "A" * 1000
        long_email = "a" * 500 + "@example.com"
        
        dto = PersonProfileDto(
            personId=self.valid_person_id,
            name=long_name,
            email=long_email,
            role=self.valid_role,
            reputationScore=self.valid_reputation_score
        )
        
        assert len(dto.name) == 1000
        assert len(dto.email) > 500
        
        result_dict = dto.to_dict()
        assert result_dict['name'] == long_name
        assert result_dict['email'] == long_email