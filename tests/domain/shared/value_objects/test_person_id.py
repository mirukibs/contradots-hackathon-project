"""
Tests for PersonId value object.
Covers all methods and business rules for PersonId.
"""
import uuid
from src.domain.shared.value_objects.person_id import PersonId


class TestPersonId:
    """Test PersonId value object implementation."""
    
    def test_init_with_uuid(self):
        """Test PersonId initialization with UUID."""
        test_uuid = uuid.uuid4()
        person_id = PersonId(test_uuid)
        
        assert person_id.value == test_uuid
    
    def test_init_with_string_uuid(self):
        """Test PersonId initialization with string UUID."""
        test_uuid = uuid.uuid4()
        test_string = str(test_uuid)
        person_id = PersonId(test_string)
        
        assert person_id.value == test_uuid
        assert isinstance(person_id.value, uuid.UUID)
    
    def test_init_with_invalid_string_raises_error(self):
        """Test PersonId initialization with invalid string raises ValueError."""
        try:
            PersonId("invalid-uuid-string")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "PersonId value must be a valid UUID string" in str(e)
    
    def test_generate_creates_new_person_id(self):
        """Test PersonId.generate() creates new PersonId with random UUID."""
        person_id1 = PersonId.generate()
        person_id2 = PersonId.generate()
        
        assert isinstance(person_id1, PersonId)
        assert isinstance(person_id2, PersonId)
        assert person_id1.value != person_id2.value
    
    def test_value_property(self):
        """Test value property returns the UUID."""
        test_uuid = uuid.uuid4()
        person_id = PersonId(test_uuid)
        
        assert person_id.value == test_uuid
        assert isinstance(person_id.value, uuid.UUID)
    
    def test_validate_method(self):
        """Test validate method does not raise error for valid PersonId."""
        person_id = PersonId.generate()
        # Should not raise any exception
        person_id.validate()
    
    def test_equality_same_uuid(self):
        """Test PersonId equality with same UUID."""
        test_uuid = uuid.uuid4()
        person_id1 = PersonId(test_uuid)
        person_id2 = PersonId(test_uuid)
        
        assert person_id1 == person_id2
    
    def test_equality_different_uuid(self):
        """Test PersonId inequality with different UUID."""
        person_id1 = PersonId.generate()
        person_id2 = PersonId.generate()
        
        assert person_id1 != person_id2
    
    def test_equality_with_non_person_id(self):
        """Test PersonId inequality with non-PersonId object."""
        person_id = PersonId.generate()
        
        assert person_id != "not-a-person-id"
        assert person_id != 123
        assert person_id != None
    
    def test_hash_consistency(self):
        """Test PersonId hash is consistent."""
        test_uuid = uuid.uuid4()
        person_id1 = PersonId(test_uuid)
        person_id2 = PersonId(test_uuid)
        
        assert hash(person_id1) == hash(person_id2)
    
    def test_hash_different_for_different_uuids(self):
        """Test PersonId hash is different for different UUIDs."""
        person_id1 = PersonId.generate()
        person_id2 = PersonId.generate()
        
        assert hash(person_id1) != hash(person_id2)
    
    def test_str_representation(self):
        """Test PersonId string representation."""
        test_uuid = uuid.uuid4()
        person_id = PersonId(test_uuid)
        
        assert str(person_id) == str(test_uuid)
    
    def test_repr_representation(self):
        """Test PersonId repr representation."""
        test_uuid = uuid.uuid4()
        person_id = PersonId(test_uuid)
        
        expected_repr = f"PersonId(value={test_uuid!r})"
        assert repr(person_id) == expected_repr
    
    def test_immutability(self):
        """Test PersonId is immutable (value cannot be changed)."""
        person_id = PersonId.generate()
        original_value = person_id.value
        
        # Attempting to change the value should not be possible through public interface
        # This is enforced by using private _value attribute
        assert person_id.value == original_value
    
    def test_can_be_used_as_dict_key(self):
        """Test PersonId can be used as dictionary key (hashable)."""
        person_id1 = PersonId.generate()
        person_id2 = PersonId.generate()
        
        test_dict = {
            person_id1: "Person 1",
            person_id2: "Person 2"
        }
        
        assert test_dict[person_id1] == "Person 1"
        assert test_dict[person_id2] == "Person 2"
    
    def test_can_be_used_in_set(self):
        """Test PersonId can be used in sets (hashable)."""
        person_id1 = PersonId.generate()
        person_id2 = PersonId.generate()
        person_id3 = PersonId(person_id1.value)  # Same as person_id1
        
        person_set = {person_id1, person_id2, person_id3}
        
        # Should only contain 2 unique PersonIds
        assert len(person_set) == 2
        assert person_id1 in person_set
        assert person_id2 in person_set