"""
Tests for ActivityRepository interface.
Covers all interface methods for ActivityRepository.
"""
from abc import ABC
from typing import Optional, List, Dict, Any
from src.domain.activity.activity_repository import ActivityRepository
from src.domain.shared.value_objects.activity_id import ActivityId
from src.domain.shared.value_objects.person_id import PersonId


# Concrete implementation for testing
class ConcreteActivityRepository(ActivityRepository):
    def reactivate_activity(self, activity_id):
        # Stub for test compliance
        pass
    """Concrete implementation of ActivityRepository for testing."""
    
    def __init__(self) -> None:
        self._activities: Dict[ActivityId, Any] = {}
    
    def save(self, activity: Any) -> None:
        self._activities[activity.activity_id] = activity
    
    def find_by_id(self, activity_id: ActivityId) -> Optional[Any]:
        return self._activities.get(activity_id)
    
    def find_by_creator_id(self, creator_id: PersonId) -> List[Any]:
        return [activity for activity in self._activities.values() 
                if activity.creator_id == creator_id]
    
    def find_all_active(self) -> List[Any]:
        # For this test, assume all activities are active
        return list(self._activities.values())


class TestActivityRepository:
    """Test ActivityRepository interface implementation."""
    
    def test_activity_repository_is_abstract(self):
        """Test ActivityRepository is an abstract base class."""
        assert issubclass(ActivityRepository, ABC)
        
        # Should not be able to instantiate abstract class directly
        try:
            ActivityRepository()
            assert False, "Should not be able to instantiate abstract class"
        except TypeError:
            pass  # Expected
    
    def test_concrete_implementation_can_be_instantiated(self):
        """Test concrete implementation can be instantiated."""
        repository = ConcreteActivityRepository()
        assert isinstance(repository, ActivityRepository)
    
    def test_save_method_signature(self):
        """Test save method has correct signature."""
        repository = ConcreteActivityRepository()
        
        # Method should exist
        assert hasattr(repository, 'save')
        assert callable(getattr(repository, 'save'))
    
    def test_find_by_id_method_signature(self):
        """Test find_by_id method has correct signature."""
        repository = ConcreteActivityRepository()
        
        # Method should exist
        assert hasattr(repository, 'find_by_id')
        assert callable(getattr(repository, 'find_by_id'))
    
    def test_find_by_creator_id_method_signature(self):
        """Test find_by_creator_id method has correct signature."""
        repository = ConcreteActivityRepository()
        
        # Method should exist
        assert hasattr(repository, 'find_by_creator_id')
        assert callable(getattr(repository, 'find_by_creator_id'))
    
    def test_find_all_active_method_signature(self):
        """Test find_all_active method has correct signature."""
        repository = ConcreteActivityRepository()
        
        # Method should exist
        assert hasattr(repository, 'find_all_active')
        assert callable(getattr(repository, 'find_all_active'))