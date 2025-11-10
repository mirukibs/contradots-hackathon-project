"""
Tests for Role enum.
Covers all enum values and methods for Role.
"""
from src.domain.person.role import Role


class TestRole:
    """Test Role enum implementation."""
    
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
    
    def test_role_comparison(self):
        """Test Role comparison operations."""
        assert Role.MEMBER == Role.MEMBER
        assert Role.LEAD == Role.LEAD
        assert Role.MEMBER != Role.LEAD
        assert Role.LEAD != Role.MEMBER
    
    def test_role_membership(self):
        """Test Role can be used in collections."""
        roles = {Role.MEMBER, Role.LEAD}
        assert len(roles) == 2
        assert Role.MEMBER in roles
        assert Role.LEAD in roles
    
    def test_role_iteration(self):
        """Test Role enum can be iterated."""
        all_roles = list(Role)
        assert len(all_roles) == 2
        assert Role.MEMBER in all_roles
        assert Role.LEAD in all_roles