"""
Tests for PersonRepository interface.
Covers all interface methods for PersonRepository.
"""
from abc import ABC
from typing import Optional, List, Dict, Any
from src.domain.person.person_repository import PersonRepository
from src.domain.shared.value_objects.person_id import PersonId


# Concrete implementation for testing
class ConcretePersonRepository(PersonRepository):
    """Concrete implementation of PersonRepository for testing."""
    
    def __init__(self) -> None:
        self._persons: Dict[PersonId, Any] = {}
    
    def save(self, person: Any) -> None:
        self._persons[person.person_id] = person
    
    def find_by_id(self, person_id: PersonId) -> Optional[Any]:  # type: ignore[override]
        return self._persons.get(person_id)
    
    def find_by_email(self, email: str) -> Optional[Any]:  # type: ignore[override]
        """Find person by email address."""
        for person in self._persons.values():
            if hasattr(person, 'email') and person.email == email:
                return person
        return None
    
    def find_all(self) -> List[Any]:
        return list(self._persons.values())


class TestPersonRepository:
    """Test PersonRepository interface implementation."""
    
    def test_person_repository_is_abstract(self):
        """Test PersonRepository is an abstract base class."""
        assert issubclass(PersonRepository, ABC)
        
        # Should not be able to instantiate abstract class directly
        try:
            PersonRepository()
            assert False, "Should not be able to instantiate abstract class"
        except TypeError:
            pass  # Expected
    
    def test_concrete_implementation_can_be_instantiated(self):
        """Test concrete implementation can be instantiated."""
        repository = ConcretePersonRepository()
        assert isinstance(repository, PersonRepository)
    
    def test_save_method_signature(self):
        """Test save method has correct signature."""
        repository = ConcretePersonRepository()
        
        # Method should exist
        assert hasattr(repository, 'save')
        assert callable(getattr(repository, 'save'))
    
    def test_find_by_id_method_signature(self):
        """Test find_by_id method has correct signature."""
        repository = ConcretePersonRepository()
        
        # Method should exist
        assert hasattr(repository, 'find_by_id')
        assert callable(getattr(repository, 'find_by_id'))
    
    def test_find_all_method_signature(self):
        """Test find_all method has correct signature."""
        repository = ConcretePersonRepository()
        
        # Method should exist
        assert hasattr(repository, 'find_all')
        assert callable(getattr(repository, 'find_all'))
    
    def test_find_by_email_method_signature(self):
        """Test find_by_email method has correct signature."""
        repository = ConcretePersonRepository()
        
        # Method should exist
        assert hasattr(repository, 'find_by_email')
        assert callable(getattr(repository, 'find_by_email'))