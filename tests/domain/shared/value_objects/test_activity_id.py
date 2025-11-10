"""
Tests for ActivityId value object.
Covers all methods and business rules for ActivityId.
"""
import uuid
from src.domain.shared.value_objects.activity_id import ActivityId


class TestActivityId:
    """Test ActivityId value object implementation."""
    
    def test_init_with_uuid(self):
        """Test ActivityId initialization with UUID."""
        test_uuid = uuid.uuid4()
        activity_id = ActivityId(test_uuid)
        
        assert activity_id.value == test_uuid
    
    def test_init_with_string_uuid(self):
        """Test ActivityId initialization with string UUID."""
        test_uuid = uuid.uuid4()
        test_string = str(test_uuid)
        activity_id = ActivityId(test_string)
        
        assert activity_id.value == test_uuid
        assert isinstance(activity_id.value, uuid.UUID)
    
    def test_init_with_invalid_string_raises_error(self):
        """Test ActivityId initialization with invalid string raises ValueError."""
        try:
            ActivityId("invalid-uuid-string")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "ActivityId value must be a valid UUID string" in str(e)
    
    def test_generate_creates_new_activity_id(self):
        """Test ActivityId.generate() creates new ActivityId with random UUID."""
        activity_id1 = ActivityId.generate()
        activity_id2 = ActivityId.generate()
        
        assert isinstance(activity_id1, ActivityId)
        assert isinstance(activity_id2, ActivityId)
        assert activity_id1.value != activity_id2.value
    
    def test_value_property(self):
        """Test value property returns the UUID."""
        test_uuid = uuid.uuid4()
        activity_id = ActivityId(test_uuid)
        
        assert activity_id.value == test_uuid
        assert isinstance(activity_id.value, uuid.UUID)
    
    def test_validate_method(self):
        """Test validate method does not raise error for valid ActivityId."""
        activity_id = ActivityId.generate()
        # Should not raise any exception
        activity_id.validate()
    
    def test_equality_same_uuid(self):
        """Test ActivityId equality with same UUID."""
        test_uuid = uuid.uuid4()
        activity_id1 = ActivityId(test_uuid)
        activity_id2 = ActivityId(test_uuid)
        
        assert activity_id1 == activity_id2
    
    def test_equality_different_uuid(self):
        """Test ActivityId inequality with different UUID."""
        activity_id1 = ActivityId.generate()
        activity_id2 = ActivityId.generate()
        
        assert activity_id1 != activity_id2
    
    def test_equality_with_non_activity_id(self):
        """Test ActivityId inequality with non-ActivityId object."""
        activity_id = ActivityId.generate()
        
        assert activity_id != "not-an-activity-id"
        assert activity_id != 123
        assert activity_id != None
    
    def test_hash_consistency(self):
        """Test ActivityId hash is consistent."""
        test_uuid = uuid.uuid4()
        activity_id1 = ActivityId(test_uuid)
        activity_id2 = ActivityId(test_uuid)
        
        assert hash(activity_id1) == hash(activity_id2)
    
    def test_str_representation(self):
        """Test ActivityId string representation."""
        test_uuid = uuid.uuid4()
        activity_id = ActivityId(test_uuid)
        
        assert str(activity_id) == str(test_uuid)
    
    def test_repr_representation(self):
        """Test ActivityId repr representation."""
        test_uuid = uuid.uuid4()
        activity_id = ActivityId(test_uuid)
        
        expected_repr = f"ActivityId(value={test_uuid!r})"
        assert repr(activity_id) == expected_repr