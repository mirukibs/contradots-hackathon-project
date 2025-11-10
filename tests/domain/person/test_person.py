"""
Tests for Person aggregate root.
Covers all methods and business rules for Person aggregate.
"""
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.person.person import Person
from src.domain.person.role import Role


class TestPerson:
    """Test Person aggregate root implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.person_id = PersonId.generate()
        self.name = "John Doe"
        self.email = "john.doe@example.com"
    
    def test_init_with_all_parameters(self):
        """Test Person initialization with all parameters."""
        person = Person(
            person_id=self.person_id,
            name=self.name,
            email=self.email,
            role=Role.LEAD,
            reputation_score=100
        )
        
        assert person.person_id == self.person_id
        assert person.name == self.name
        assert person.email == self.email
        assert person.role == Role.LEAD
        assert person.reputation_score == 100
    
    def test_init_with_default_values(self):
        """Test Person initialization with default reputation score."""
        person = Person(
            person_id=self.person_id,
            name=self.name,
            email=self.email,
            role=Role.MEMBER
        )
        
        assert person.reputation_score == 0
    
    def test_init_with_empty_name_raises_error(self):
        """Test Person initialization with empty name raises ValueError."""
        try:
            Person(self.person_id, "", self.email, Role.MEMBER)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Person name cannot be empty" in str(e)
        
        try:
            Person(self.person_id, "   ", self.email, Role.MEMBER)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Person name cannot be empty" in str(e)
    
    def test_init_with_empty_email_raises_error(self):
        """Test Person initialization with empty email raises ValueError."""
        try:
            Person(self.person_id, self.name, "", Role.MEMBER)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Person email cannot be empty" in str(e)
        
        try:
            Person(self.person_id, self.name, "   ", Role.MEMBER)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Person email cannot be empty" in str(e)
    
    def test_init_with_invalid_email_raises_error(self):
        """Test Person initialization with invalid email raises ValueError."""
        try:
            Person(self.person_id, self.name, "invalid-email", Role.MEMBER)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Person email must be a valid email address" in str(e)
    
    def test_init_with_negative_reputation_raises_error(self):
        """Test Person initialization with negative reputation raises ValueError."""
        try:
            Person(self.person_id, self.name, self.email, Role.MEMBER, -1)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Person reputation score cannot be negative" in str(e)
    
    def test_create_class_method_with_all_parameters(self):
        """Test Person.create() class method with all parameters."""
        person = Person.create(
            name=self.name,
            email=self.email,
            role=Role.LEAD,
            person_id=self.person_id
        )
        
        assert person.person_id == self.person_id
        assert person.name == self.name
        assert person.email == self.email
        assert person.role == Role.LEAD
        assert person.reputation_score == 0
    
    def test_create_class_method_generates_id(self):
        """Test Person.create() generates PersonId when not provided."""
        person = Person.create(
            name=self.name,
            email=self.email,
            role=Role.MEMBER
        )
        
        assert isinstance(person.person_id, PersonId)
        assert person.name == self.name
        assert person.email == self.email
        assert person.role == Role.MEMBER
        assert person.reputation_score == 0
    
    def test_register_method(self):
        """Test register() method does not raise error."""
        person = Person.create(self.name, self.email, Role.MEMBER)
        
        # Should not raise any exception
        person.register()
    
    def test_update_reputation_positive(self):
        """Test update_reputation() with positive points."""
        person = Person.create(self.name, self.email, Role.MEMBER)
        initial_score = person.reputation_score
        
        person.update_reputation(50)
        
        assert person.reputation_score == initial_score + 50
    
    def test_update_reputation_negative(self):
        """Test update_reputation() with negative points."""
        person = Person(self.person_id, self.name, self.email, Role.MEMBER, 100)
        
        person.update_reputation(-30)
        
        assert person.reputation_score == 70
    
    def test_update_reputation_to_negative_clamped_to_zero(self):
        """Test update_reputation() clamps negative results to zero."""
        person = Person(self.person_id, self.name, self.email, Role.MEMBER, 20)
        
        person.update_reputation(-50)
        
        # Based on the Person implementation, reputation is clamped to 0
        assert person.reputation_score == 0
    
    def test_can_create_activities_member_false(self):
        """Test canCreateActivities() returns False for MEMBER role."""
        person = Person.create(self.name, self.email, Role.MEMBER)
        
        assert person.can_create_activities() == False
    
    def test_can_create_activities_lead_true(self):
        """Test canCreateActivities() returns True for LEAD role."""
        person = Person.create(self.name, self.email, Role.LEAD)
        
        assert person.can_create_activities() == True
    
    def test_equality_same_person_id(self):
        """Test Person equality based on person ID."""
        person1 = Person(self.person_id, self.name, self.email, Role.MEMBER)
        person2 = Person(self.person_id, "Different Name", "different@email.com", Role.LEAD, 100)
        
        assert person1 == person2
    
    def test_equality_different_person_id(self):
        """Test Person inequality with different person IDs."""
        person1 = Person.create(self.name, self.email, Role.MEMBER)
        person2 = Person.create(self.name, self.email, Role.MEMBER)
        
        assert person1 != person2
    
    def test_equality_with_non_person(self):
        """Test Person inequality with non-Person object."""
        person = Person.create(self.name, self.email, Role.MEMBER)
        
        assert person != "not-a-person"
        assert person != 123
        assert person != None
    
    def test_hash_consistency(self):
        """Test Person hash is consistent and based on person ID."""
        person1 = Person(self.person_id, self.name, self.email, Role.MEMBER)
        person2 = Person(self.person_id, "Different Name", "different@email.com", Role.LEAD)
        
        assert hash(person1) == hash(person2)
    
    def test_repr_representation(self):
        """Test Person repr representation."""
        person = Person(self.person_id, self.name, self.email, Role.MEMBER, 50)
        
        expected_repr = (f"Person(person_id={self.person_id!r}, name='{self.name}', "
                        f"email='{self.email}', role={Role.MEMBER!r}, "
                        f"reputation_score=50)")
        
        assert repr(person) == expected_repr


class TestRole:
    """Test Role enum."""
    
    def test_role_values(self):
        """Test Role enum values match domain model."""
        assert Role.MEMBER.value == "MEMBER"
        assert Role.LEAD.value == "LEAD"
    
    def test_role_str_representation(self):
        """Test Role string representation."""
        assert str(Role.MEMBER) == "MEMBER"
        assert str(Role.LEAD) == "LEAD"
    
    def test_role_repr_representation(self):
        """Test Role repr representation."""
        assert repr(Role.MEMBER) == "Role.MEMBER"
        assert repr(Role.LEAD) == "Role.LEAD"