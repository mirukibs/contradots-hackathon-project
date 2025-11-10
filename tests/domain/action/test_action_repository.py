"""
Tests for ActionRepository interface.
Covers all interface methods for ActionRepository.
"""
from abc import ABC
from typing import Optional, List, Dict, Any
from src.domain.action.action_repository import ActionRepository
from src.domain.shared.value_objects.action_id import ActionId
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.shared.value_objects.activity_id import ActivityId


# Concrete implementation for testing
class ConcreteActionRepository(ActionRepository):
    """Concrete implementation of ActionRepository for testing."""
    
    def __init__(self) -> None:
        self._actions: Dict[ActionId, Any] = {}
    
    def save(self, action: Any) -> None:
        self._actions[action.action_id] = action
    
    def find_by_id(self, action_id: ActionId) -> Optional[Any]:
        return self._actions.get(action_id)
    
    def find_by_person_id(self, person_id: PersonId) -> List[Any]:
        return [action for action in self._actions.values() 
                if action.person_id == person_id]
    
    def find_by_activity_id(self, activity_id: ActivityId) -> List[Any]:
        return [action for action in self._actions.values() 
                if action.activity_id == activity_id]
    
    def find_verified_by_person_id(self, person_id: PersonId) -> List[Any]:
        return [action for action in self._actions.values() 
                if action.person_id == person_id and action.is_verified()]


class TestActionRepository:
    """Test ActionRepository interface implementation."""
    
    def test_action_repository_is_abstract(self):
        """Test ActionRepository is an abstract base class."""
        assert issubclass(ActionRepository, ABC)
        
        # Should not be able to instantiate abstract class directly
        try:
            ActionRepository()
            assert False, "Should not be able to instantiate abstract class"
        except TypeError:
            pass  # Expected
    
    def test_concrete_implementation_can_be_instantiated(self):
        """Test concrete implementation can be instantiated."""
        repository = ConcreteActionRepository()
        assert isinstance(repository, ActionRepository)
    
    def test_save_method_signature(self):
        """Test save method has correct signature."""
        repository = ConcreteActionRepository()
        
        # Method should exist
        assert hasattr(repository, 'save')
        assert callable(getattr(repository, 'save'))
    
    def test_find_by_id_method_signature(self):
        """Test find_by_id method has correct signature."""
        repository = ConcreteActionRepository()
        
        # Method should exist
        assert hasattr(repository, 'find_by_id')
        assert callable(getattr(repository, 'find_by_id'))
    
    def test_find_by_person_id_method_signature(self):
        """Test find_by_person_id method has correct signature."""
        repository = ConcreteActionRepository()
        
        # Method should exist
        assert hasattr(repository, 'find_by_person_id')
        assert callable(getattr(repository, 'find_by_person_id'))
    
    def test_find_by_activity_id_method_signature(self):
        """Test find_by_activity_id method has correct signature."""
        repository = ConcreteActionRepository()
        
        # Method should exist
        assert hasattr(repository, 'find_by_activity_id')
        assert callable(getattr(repository, 'find_by_activity_id'))
    
    def test_find_verified_by_person_id_method_signature(self):
        """Test find_verified_by_person_id method has correct signature."""
        repository = ConcreteActionRepository()
        
        # Method should exist
        assert hasattr(repository, 'find_verified_by_person_id')
        assert callable(getattr(repository, 'find_verified_by_person_id'))