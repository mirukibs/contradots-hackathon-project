"""Comprehensive tests for DeactivateActivityCommand"""

import unittest
from unittest.mock import patch
from src.application.commands.deactivate_activity_command import DeactivateActivityCommand
from src.domain.shared.value_objects.activity_id import ActivityId
from src.domain.shared.value_objects.person_id import PersonId


class TestDeactivateActivityCommand(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        self.valid_activity_id = ActivityId.generate()
        self.valid_lead_id = PersonId.generate()
        
    def test_validate_with_valid_data(self):
        """Test validation passes with valid data"""
        command = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        # Should not raise any exception
        command.validate()
        
    def test_validate_activity_id_none_type_error(self):
        """Test validation with None activityId to trigger TypeError in UUID validation"""
        command = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        # Mock uuid.UUID to raise TypeError on None input
        with patch('uuid.UUID') as mock_uuid:
            mock_uuid.side_effect = TypeError("int() argument must be a string")
            
            try:
                command.validate()
                assert False, "Should have raised ValueError for invalid activityId format"
            except ValueError as e:
                assert "Activity ID must be a valid UUID" in str(e)

    def test_validate_activity_id_invalid_uuid_format(self):
        """Test validation with invalid UUID format to trigger ValueError in UUID validation"""
        command = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        # Mock uuid.UUID to raise ValueError on invalid input
        with patch('uuid.UUID') as mock_uuid:
            mock_uuid.side_effect = ValueError("badly formed hexadecimal UUID string")
            
            try:
                command.validate()
                assert False, "Should have raised ValueError for invalid activityId format"
            except ValueError as e:
                assert "Activity ID must be a valid UUID" in str(e)

    def test_validate_lead_id_none_type_error(self):
        """Test validation with None leadId to trigger TypeError in UUID validation"""
        command = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        # Mock uuid.UUID to raise TypeError on second call (leadId validation)
        with patch('uuid.UUID') as mock_uuid:
            mock_uuid.side_effect = [None, TypeError("int() argument must be a string")]
            
            try:
                command.validate()
                assert False, "Should have raised ValueError for invalid leadId format"
            except ValueError as e:
                assert "Lead ID must be a valid UUID" in str(e)

    def test_validate_lead_id_invalid_uuid_format(self):
        """Test validation with invalid UUID format to trigger ValueError in UUID validation"""
        command = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        # Mock uuid.UUID to raise ValueError on second call (leadId validation)
        with patch('uuid.UUID') as mock_uuid:
            mock_uuid.side_effect = [None, ValueError("badly formed hexadecimal UUID string")]
            
            try:
                command.validate()
                assert False, "Should have raised ValueError for invalid leadId format"
            except ValueError as e:
                assert "Lead ID must be a valid UUID" in str(e)

    def test_validate_none_lead_id_using_object_setattr(self):
        """Test validation when leadId is None to cover line 31"""
        command = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        # Use object.__setattr__ to bypass frozen dataclass restriction
        object.__setattr__(command, 'leadId', None)
        
        try:
            command.validate()
            assert False, "Should have raised ValueError for None leadId"
        except ValueError as e:
            assert "Lead ID is required" in str(e)

    def test_validate_none_activity_id_coverage(self):
        """Test to ensure line 28 coverage - activity ID validation"""
        command = DeactivateActivityCommand(
            activityId=self.valid_activity_id,
            leadId=self.valid_lead_id
        )
        
        # Use object.__setattr__ to bypass frozen dataclass restriction
        object.__setattr__(command, 'activityId', None)
        
        try:
            command.validate()
            assert False, "Should have raised ValueError for None activityId"
        except ValueError as e:
            assert "Activity ID is required" in str(e)