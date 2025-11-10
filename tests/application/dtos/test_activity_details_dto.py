"""Comprehensive tests for ActivityDetailsDto"""

from typing import Dict, Any
from src.application.dtos.activity_details_dto import ActivityDetailsDto


class TestActivityDetailsDto:
    """Test suite for ActivityDetailsDto covering all methods and edge cases"""

    def setup_method(self):
        """Set up test fixtures"""
        self.valid_activity_id = "550e8400-e29b-41d4-a716-446655440001"
        self.valid_name = "Beach Cleanup Drive"
        self.valid_description = "Community-driven beach cleanup to protect marine life"
        self.valid_points = 50
        self.valid_lead_name = "Jane Smith"
        self.valid_is_active = True
        self.valid_participant_count = 25
        self.valid_total_actions = 47

    def test_dto_creation_with_valid_data(self):
        """Test creating DTO with valid data"""
        dto = ActivityDetailsDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active,
            participantCount=self.valid_participant_count,
            totalActionsSubmitted=self.valid_total_actions
        )
        
        assert dto.activityId == self.valid_activity_id
        assert dto.name == self.valid_name
        assert dto.description == self.valid_description
        assert dto.points == self.valid_points
        assert dto.leadName == self.valid_lead_name
        assert dto.isActive == self.valid_is_active
        assert dto.participantCount == self.valid_participant_count
        assert dto.totalActionsSubmitted == self.valid_total_actions

    def test_to_dict_conversion(self):
        """Test conversion to dictionary"""
        dto = ActivityDetailsDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active,
            participantCount=self.valid_participant_count,
            totalActionsSubmitted=self.valid_total_actions
        )
        
        result_dict = dto.to_dict()
        
        expected_dict: Dict[str, Any] = {
            'activityId': self.valid_activity_id,
            'name': self.valid_name,
            'description': self.valid_description,
            'points': self.valid_points,
            'leadName': self.valid_lead_name,
            'isActive': self.valid_is_active,
            'participantCount': self.valid_participant_count,
            'totalActionsSubmitted': self.valid_total_actions
        }
        
        assert result_dict == expected_dict

    def test_to_dict_includes_all_fields(self):
        """Test that to_dict includes all DTO fields"""
        dto = ActivityDetailsDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active,
            participantCount=self.valid_participant_count,
            totalActionsSubmitted=self.valid_total_actions
        )
        
        result_dict = dto.to_dict()
        
        # Check all fields are present
        expected_fields = [
            'activityId', 'name', 'description', 'points', 
            'leadName', 'isActive', 'participantCount', 'totalActionsSubmitted'
        ]
        
        for field in expected_fields:
            assert field in result_dict
        
        # Check correct number of fields
        assert len(result_dict) == 8

    def test_dto_with_zero_participants(self):
        """Test DTO with zero participants"""
        dto = ActivityDetailsDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active,
            participantCount=0,
            totalActionsSubmitted=0
        )
        
        assert dto.participantCount == 0
        assert dto.totalActionsSubmitted == 0
        result_dict = dto.to_dict()
        assert result_dict['participantCount'] == 0
        assert result_dict['totalActionsSubmitted'] == 0

    def test_dto_with_high_numbers(self):
        """Test DTO with very high participant and action counts"""
        dto = ActivityDetailsDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active,
            participantCount=50000,
            totalActionsSubmitted=150000
        )
        
        assert dto.participantCount == 50000
        assert dto.totalActionsSubmitted == 150000

    def test_dto_equality(self):
        """Test DTO equality comparison"""
        dto1 = ActivityDetailsDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active,
            participantCount=self.valid_participant_count,
            totalActionsSubmitted=self.valid_total_actions
        )
        
        dto2 = ActivityDetailsDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active,
            participantCount=self.valid_participant_count,
            totalActionsSubmitted=self.valid_total_actions
        )
        
        assert dto1 == dto2

    def test_dto_inequality(self):
        """Test DTO inequality comparison"""
        dto1 = ActivityDetailsDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active,
            participantCount=self.valid_participant_count,
            totalActionsSubmitted=self.valid_total_actions
        )
        
        dto2 = ActivityDetailsDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active,
            participantCount=100,  # Different count
            totalActionsSubmitted=self.valid_total_actions
        )
        
        assert dto1 != dto2

    def test_dto_field_types(self):
        """Test that DTO fields have correct types"""
        dto = ActivityDetailsDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active,
            participantCount=self.valid_participant_count,
            totalActionsSubmitted=self.valid_total_actions
        )
        
        assert isinstance(dto.activityId, str)
        assert isinstance(dto.name, str)
        assert isinstance(dto.description, str)
        assert isinstance(dto.points, int)
        assert isinstance(dto.leadName, str)
        assert isinstance(dto.isActive, bool)
        assert isinstance(dto.participantCount, int)
        assert isinstance(dto.totalActionsSubmitted, int)

    def test_serialization_deserialization_round_trip(self):
        """Test that DTO can be serialized and deserialized consistently"""
        original_dto = ActivityDetailsDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active,
            participantCount=self.valid_participant_count,
            totalActionsSubmitted=self.valid_total_actions
        )
        
        # Convert to dict (serialization)
        dto_dict = original_dto.to_dict()
        
        # Recreate from dict (deserialization)
        recreated_dto = ActivityDetailsDto(
            activityId=dto_dict['activityId'],
            name=dto_dict['name'],
            description=dto_dict['description'],
            points=dto_dict['points'],
            leadName=dto_dict['leadName'],
            isActive=dto_dict['isActive'],
            participantCount=dto_dict['participantCount'],
            totalActionsSubmitted=dto_dict['totalActionsSubmitted']
        )
        
        assert original_dto == recreated_dto

    def test_dto_with_no_activity(self):
        """Test DTO representing an inactive activity with no participation"""
        dto = ActivityDetailsDto(
            activityId=self.valid_activity_id,
            name="Canceled Event",
            description="This event was canceled due to weather",
            points=0,
            leadName="John Doe",
            isActive=False,
            participantCount=0,
            totalActionsSubmitted=0
        )
        
        assert dto.isActive == False
        assert dto.participantCount == 0
        assert dto.totalActionsSubmitted == 0
        assert dto.points == 0

    def test_dto_hash(self):
        """Test DTO can be hashed"""
        dto = ActivityDetailsDto(
            activityId=self.valid_activity_id,
            name=self.valid_name,
            description=self.valid_description,
            points=self.valid_points,
            leadName=self.valid_lead_name,
            isActive=self.valid_is_active,
            participantCount=self.valid_participant_count,
            totalActionsSubmitted=self.valid_total_actions
        )
        
        # Should not raise any exception
        hash(dto)
        
        # Should work in sets
        dto_set = {dto}
        assert len(dto_set) == 1