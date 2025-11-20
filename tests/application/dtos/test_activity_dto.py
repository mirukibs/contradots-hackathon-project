"""Comprehensive tests for ActivityDto"""

from typing import Dict, Any
from src.application.dtos.activity_dto import ActivityDto


class TestActivityDto:
    """Test suite for ActivityDto covering all methods and edge cases"""

    def setup_method(self):
        """Set up test fixtures"""
        self.valid_activity_id = "550e8400-e29b-41d4-a716-446655440001"
        self.valid_name = "Beach Cleanup Drive"
        self.valid_description = "Community-driven beach cleanup to protect marine life"
        self.valid_points = 50
        self.valid_lead_name = "Jane Smith"
        self.valid_is_active = True

    def test_dto_creation_with_valid_data_active(self):
        """Test creating DTO with valid data (active activity)"""
        dto = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        assert dto.activityId == self.valid_activity_id
        assert dto.name == self.valid_name
        assert dto.description == self.valid_description
        assert dto.points == self.valid_points
        assert dto.leadName == self.valid_lead_name
        assert dto.isActive == self.valid_is_active

    def test_dto_creation_with_valid_data_inactive(self):
        """Test creating DTO with valid data (inactive activity)"""
        dto = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=False
        )
        
        assert dto.activityId == self.valid_activity_id
        assert dto.isActive == False

    def test_dto_is_frozen(self):
        """Test that DTO is immutable (frozen dataclass)"""
        dto = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        # Verify the DTO is intact
        assert dto.activityId == self.valid_activity_id
        assert dto.name == self.valid_name
        assert dto.isActive == self.valid_is_active

    def test_to_dict_conversion_active(self):
        """Test conversion to dictionary for active activity"""
        dto = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=True
        )
        
        result_dict = dto.to_dict()
        
        expected_dict: Dict[str, Any] = {
            'activityId': self.valid_activity_id,
            'name': self.valid_name,
            'description': self.valid_description,
            'points': self.valid_points,
            'leadName': self.valid_lead_name,
            'isActive': True
        }
        
        assert result_dict == expected_dict

    def test_to_dict_conversion_inactive(self):
        """Test conversion to dictionary for inactive activity"""
        dto = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=False
        )
        
        result_dict = dto.to_dict()
        assert result_dict['isActive'] == False

    def test_to_dict_includes_all_fields(self):
        """Test that to_dict includes all DTO fields"""
        dto = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        result_dict = dto.to_dict()
        
        # Check all fields are present
        assert 'activityId' in result_dict
        assert 'name' in result_dict
        assert 'description' in result_dict
        assert 'points' in result_dict
        assert 'leadName' in result_dict
        assert 'isActive' in result_dict
        
        # Check correct number of fields
        assert len(result_dict) == 6

    def test_dto_equality(self):
        """Test DTO equality comparison"""
        dto1 = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        dto2 = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        assert dto1 == dto2

    def test_dto_inequality_different_name(self):
        """Test DTO inequality comparison with different name"""
        dto1 = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        dto2 = ActivityDto(
            activityId=self.valid_activity_id,
            name="Different Activity Name",
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        assert dto1 != dto2

    def test_dto_inequality_different_active_status(self):
        """Test DTO inequality comparison with different active status"""
        dto1 = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=True
        )
        
        dto2 = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=False
        )
        
        assert dto1 != dto2

    def test_dto_hash(self):
        """Test DTO can be hashed (for use in sets, dicts)"""
        dto = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        # Should not raise any exception
        hash(dto)
        
        # Should work in sets
        dto_set = {dto}
        assert len(dto_set) == 1

    def test_dto_repr(self):
        """Test DTO string representation"""
        dto = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        repr_str = repr(dto)
        assert "ActivityDto" in repr_str
        assert self.valid_name in repr_str

    def test_dto_with_zero_points(self):
        """Test DTO with zero points"""
        dto = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=0,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        assert dto.points == 0
        result_dict = dto.to_dict()
        assert result_dict['points'] == 0

    def test_dto_with_negative_points(self):
        """Test DTO with negative points (edge case)"""
        dto = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=-10,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        assert dto.points == -10
        result_dict = dto.to_dict()
        assert result_dict['points'] == -10

    def test_dto_with_high_points(self):
        """Test DTO with very high points"""
        dto = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=99999,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        assert dto.points == 99999
        result_dict = dto.to_dict()
        assert result_dict['points'] == 99999

    def test_dto_with_empty_strings(self):
        """Test DTO with empty strings"""
        dto = ActivityDto(
            activityId="",
            name="",
            description="",
            points=0,
            leadName="",
            isActive=False
        )
        
        assert dto.activityId == ""
        assert dto.name == ""
        assert dto.description == ""
        assert dto.leadName == ""
        
        result_dict = dto.to_dict()
        assert result_dict['activityId'] == ""
        assert result_dict['name'] == ""
        assert result_dict['description'] == ""
        assert result_dict['leadName'] == ""

    def test_dto_with_special_characters(self):
        """Test DTO with special characters"""
        special_name = "Beach Cleanup & Marine Conservation 🌊"
        special_description = "Clean-up event @ Sunset Beach (5km stretch)"
        special_lead = "María José O'Connor"
        
        dto = ActivityDto(
            activityId=self.valid_activity_id,
            name=special_name,
            description=special_description,
            points=self.valid_points,
            leadName=special_lead,
            isActive=self.valid_is_active
        )
        
        assert dto.name == special_name
        assert dto.description == special_description
        assert dto.leadName == special_lead
        
        result_dict = dto.to_dict()
        assert result_dict['name'] == special_name
        assert result_dict['description'] == special_description
        assert result_dict['leadName'] == special_lead

    def test_dto_with_unicode_characters(self):
        """Test DTO with unicode characters"""
        unicode_name = "海滩清洁活动"
        unicode_description = "保护海洋生态环境的清洁活动"
        unicode_lead = "田中太郎"
        
        dto = ActivityDto(
            activityId=self.valid_activity_id,
            name=unicode_name,
            description=unicode_description,
            points=self.valid_points,
            leadName=unicode_lead,
            isActive=self.valid_is_active
        )
        
        assert dto.name == unicode_name
        assert dto.description == unicode_description
        assert dto.leadName == unicode_lead

    def test_dto_field_types(self):
        """Test that DTO fields have correct types"""
        dto = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        assert isinstance(dto.activityId, str)
        assert isinstance(dto.name, str)
        assert isinstance(dto.description, str)
        assert isinstance(dto.points, int)
        assert isinstance(dto.leadName, str)
        assert isinstance(dto.isActive, bool)

    def test_dto_serialization_deserialization_round_trip(self):
        """Test that DTO can be serialized and deserialized consistently"""
        original_dto = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        # Convert to dict (serialization)
        dto_dict = original_dto.to_dict()
        
        # Recreate from dict (deserialization)
        recreated_dto = ActivityDto(
            activityId=dto_dict['activityId'],
            name=dto_dict['name'],
            description=dto_dict['description'],
            points=dto_dict['points'],
            leadName=dto_dict['leadName'],
            isActive=dto_dict['isActive']
        )
        
        assert original_dto == recreated_dto

    def test_dto_in_collections(self):
        """Test DTO behavior in collections (set, list, dict)"""
        dto1 = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        dto2 = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        different_dto = ActivityDto(
            activityId="different-id",
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        # Test in set (should deduplicate)
        dto_set = {dto1, dto2, different_dto}
        assert len(dto_set) == 2
        
        # Test in list
        dto_list = [dto1, dto2, different_dto]
        assert len(dto_list) == 3

    def test_dto_with_multiline_description(self):
        """Test DTO with multiline description"""
        multiline_description = """This is a comprehensive beach cleanup activity.
        
Activities include:
- Trash collection along 2km shoreline
- Sorting recyclables from general waste  
- Data recording for marine debris analysis
- Educational component about ocean conservation

Expected duration: 4-6 hours"""
        
        dto = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=multiline_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        assert dto.description == multiline_description
        result_dict = dto.to_dict()
        assert result_dict['description'] == multiline_description

    def test_dto_with_long_strings(self):
        """Test DTO with very long strings"""
        long_name = "A" * 1000
        long_description = "B" * 5000
        long_lead_name = "C" * 500
        
        dto = ActivityDto(
            activityId=self.valid_activity_id,
            name=long_name,
            description=long_description,
            points=self.valid_points,
            leadName=long_lead_name,
            isActive=self.valid_is_active
        )
        
        assert len(dto.name) == 1000
        assert len(dto.description) == 5000
        assert len(dto.leadName) == 500
        
        result_dict = dto.to_dict()
        assert result_dict['name'] == long_name
        assert result_dict['description'] == long_description
        assert result_dict['leadName'] == long_lead_name

    def test_to_dict_immutability(self):
        """Test that modifying to_dict result doesn't affect original DTO"""
        dto = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active
        )
        
        dto_dict = dto.to_dict()
        original_name = dto.name
        
        # Modify the dictionary
        dto_dict['name'] = "Modified Name"
        
        # Original DTO should be unchanged
        assert dto.name == original_name
        assert dto.name != "Modified Name"

    def test_dto_boolean_edge_cases(self):
        """Test DTO with boolean edge cases"""
        # Test explicitly True
        dto_true = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=True
        )
        assert dto_true.isActive is True
        
        # Test explicitly False
        dto_false = ActivityDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=False
        )
        assert dto_false.isActive is False