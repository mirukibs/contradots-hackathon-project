"""
Tests for ActionId value object.
Covers all methods and business rules for ActionId.
"""
import uuid
from src.domain.shared.value_objects.action_id import ActionId


class TestActionId:
    """Test ActionId value object implementation."""
    
    def test_init_with_uuid(self):
        """Test ActionId initialization with UUID."""
        test_uuid = uuid.uuid4()
        action_id = ActionId(test_uuid)
        
        assert action_id.value == test_uuid
    
    def test_init_with_string_uuid(self):
        """Test ActionId initialization with string UUID."""
        test_uuid = uuid.uuid4()
        test_string = str(test_uuid)
        action_id = ActionId(test_string)
        
        assert action_id.value == test_uuid
        assert isinstance(action_id.value, uuid.UUID)
    
    def test_init_with_invalid_string_raises_error(self):
        """Test ActionId initialization with invalid string raises ValueError."""
        try:
            ActionId("invalid-uuid-string")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "ActionId value must be a valid UUID string" in str(e)
    
    def test_generate_creates_new_action_id(self):
        """Test ActionId.generate() creates new ActionId with random UUID."""
        action_id1 = ActionId.generate()
        action_id2 = ActionId.generate()
        
        assert isinstance(action_id1, ActionId)
        assert isinstance(action_id2, ActionId)
        assert action_id1.value != action_id2.value
    
    def test_value_property(self):
        """Test value property returns the UUID."""
        test_uuid = uuid.uuid4()
        action_id = ActionId(test_uuid)
        
        assert action_id.value == test_uuid
        assert isinstance(action_id.value, uuid.UUID)
    
    def test_validate_method(self):
        """Test validate method does not raise error for valid ActionId."""
        action_id = ActionId.generate()
        # Should not raise any exception
        action_id.validate()
    
    def test_equality_same_uuid(self):
        """Test ActionId equality with same UUID."""
        test_uuid = uuid.uuid4()
        action_id1 = ActionId(test_uuid)
        action_id2 = ActionId(test_uuid)
        
        assert action_id1 == action_id2
    
    def test_equality_different_uuid(self):
        """Test ActionId inequality with different UUID."""
        action_id1 = ActionId.generate()
        action_id2 = ActionId.generate()
        
        assert action_id1 != action_id2
    
    def test_str_representation(self):
        """Test ActionId string representation."""
        test_uuid = uuid.uuid4()
        action_id = ActionId(test_uuid)
        
        assert str(action_id) == str(test_uuid)
    
    def test_repr_representation(self):
        """Test ActionId repr representation."""
        test_uuid = uuid.uuid4()
        action_id = ActionId(test_uuid)
        
        expected_repr = f"ActionId(value={test_uuid!r})"
        assert repr(action_id) == expected_repr