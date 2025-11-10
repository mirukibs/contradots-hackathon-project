"""
Tests for Activity aggregate root.
Covers all methods and business rules for Activity aggregate.
"""
from datetime import datetime, timezone
from src.domain.shared.value_objects.activity_id import ActivityId
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.activity.activity import Activity
from src.domain.shared.events.action_submitted_event import ActionSubmittedEvent
from src.domain.shared.value_objects.action_id import ActionId


class TestActivity:
    """Test Activity aggregate root implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.activity_id = ActivityId.generate()
        self.creator_id = PersonId.generate()
        self.title = "Community Cleanup"
        self.description = "Clean up the local park"
    
    def test_init_with_all_parameters(self):
        """Test Activity initialization with all parameters."""
        created_at = datetime.now(timezone.utc)
        
        activity = Activity(
            activity_id=self.activity_id,
            title=self.title,
            description=self.description,
            creator_id=self.creator_id,
            created_at=created_at
        )
        
        assert activity.activity_id == self.activity_id
        assert activity.title == self.title
        assert activity.description == self.description
        assert activity.creator_id == self.creator_id
        assert activity.created_at == created_at
    
    def test_init_with_default_created_at(self):
        """Test Activity initialization with default created_at."""
        activity = Activity(
            activity_id=self.activity_id,
            title=self.title,
            description=self.description,
            creator_id=self.creator_id
        )
        
        assert isinstance(activity.created_at, datetime)
        assert activity.created_at.tzinfo is not None  # Should have timezone
    
    def test_activity_id_property(self):
        """Test activity_id property returns correct value."""
        activity = Activity(self.activity_id, self.title, self.description, self.creator_id)
        
        assert activity.activity_id == self.activity_id
    
    def test_title_property(self):
        """Test title property returns correct value."""
        activity = Activity(self.activity_id, self.title, self.description, self.creator_id)
        
        assert activity.title == self.title
    
    def test_description_property(self):
        """Test description property returns correct value."""
        activity = Activity(self.activity_id, self.title, self.description, self.creator_id)
        
        assert activity.description == self.description
    
    def test_creator_id_property(self):
        """Test creator_id property returns correct value."""
        activity = Activity(self.activity_id, self.title, self.description, self.creator_id)
        
        assert activity.creator_id == self.creator_id
    
    def test_created_at_property(self):
        """Test created_at property returns correct value."""
        activity = Activity(self.activity_id, self.title, self.description, self.creator_id)
        
        assert isinstance(activity.created_at, datetime)
    
    def test_domain_events_property(self):
        """Test domain_events property returns copy of events."""
        activity = Activity(self.activity_id, self.title, self.description, self.creator_id)
        
        events = activity.domain_events
        assert isinstance(events, list)
        assert len(events) == 0
        
        # Modifying returned list should not affect original
        # Create a proper domain event for testing
        fake_event = ActionSubmittedEvent(
            action_id=ActionId.generate(),
            person_id=self.creator_id,
            activity_id=self.activity_id,
            description="Test event",
            proof_hash="test_hash"
        )
        events.append(fake_event)
        assert len(activity.domain_events) == 0
    
    def test_clear_domain_events(self):
        """Test clear_domain_events method."""
        activity = Activity(self.activity_id, self.title, self.description, self.creator_id)
        
        # Should not raise error even with no events
        activity.clear_domain_events()
        assert len(activity.domain_events) == 0
    
    def test_update_title_success(self):
        """Test update_title with valid title."""
        activity = Activity(self.activity_id, self.title, self.description, self.creator_id)
        new_title = "Beach Cleanup"
        
        activity.update_title(new_title)
        
        assert activity.title == new_title
    
    def test_update_title_with_whitespace_trimmed(self):
        """Test update_title trims whitespace."""
        activity = Activity(self.activity_id, self.title, self.description, self.creator_id)
        new_title = "  Trimmed Title  "
        
        activity.update_title(new_title)
        
        assert activity.title == "Trimmed Title"
    
    def test_update_title_empty_raises_error(self):
        """Test update_title with empty title raises ValueError."""
        activity = Activity(self.activity_id, self.title, self.description, self.creator_id)
        
        try:
            activity.update_title("")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Activity title cannot be empty" in str(e)
        
        try:
            activity.update_title("   ")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Activity title cannot be empty" in str(e)
    
    def test_update_description_success(self):
        """Test update_description with valid description."""
        activity = Activity(self.activity_id, self.title, self.description, self.creator_id)
        new_description = "Clean up the beach and collect plastic waste"
        
        activity.update_description(new_description)
        
        assert activity.description == new_description
    
    def test_update_description_with_whitespace_trimmed(self):
        """Test update_description trims whitespace."""
        activity = Activity(self.activity_id, self.title, self.description, self.creator_id)
        new_description = "  Trimmed Description  "
        
        activity.update_description(new_description)
        
        assert activity.description == "Trimmed Description"
    
    def test_update_description_empty_raises_error(self):
        """Test update_description with empty description raises ValueError."""
        activity = Activity(self.activity_id, self.title, self.description, self.creator_id)
        
        try:
            activity.update_description("")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Activity description cannot be empty" in str(e)
        
        try:
            activity.update_description("   ")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Activity description cannot be empty" in str(e)
    
    def test_equality_same_activity_id(self):
        """Test Activity equality based on activity ID."""
        activity1 = Activity(self.activity_id, self.title, self.description, self.creator_id)
        activity2 = Activity(self.activity_id, "Different Title", "Different Desc", PersonId.generate())
        
        assert activity1 == activity2
    
    def test_equality_different_activity_id(self):
        """Test Activity inequality with different activity IDs."""
        activity1 = Activity(self.activity_id, self.title, self.description, self.creator_id)
        activity2 = Activity(ActivityId.generate(), self.title, self.description, self.creator_id)
        
        assert activity1 != activity2
    
    def test_equality_with_non_activity(self):
        """Test Activity inequality with non-Activity object."""
        activity = Activity(self.activity_id, self.title, self.description, self.creator_id)
        
        assert activity != "not-an-activity"
        assert activity != 123
        assert activity != None
    
    def test_hash_consistency(self):
        """Test Activity hash is consistent and based on activity ID."""
        activity1 = Activity(self.activity_id, self.title, self.description, self.creator_id)
        activity2 = Activity(self.activity_id, "Different Title", "Different Desc", PersonId.generate())
        
        assert hash(activity1) == hash(activity2)
    
    def test_hash_different_for_different_activity_ids(self):
        """Test Activity hash is different for different activity IDs."""
        activity1 = Activity(self.activity_id, self.title, self.description, self.creator_id)
        activity2 = Activity(ActivityId.generate(), self.title, self.description, self.creator_id)
        
        assert hash(activity1) != hash(activity2)
    
    def test_repr_representation(self):
        """Test Activity repr representation."""
        activity = Activity(self.activity_id, self.title, self.description, self.creator_id)
        
        expected_repr = (f"Activity(activity_id={self.activity_id}, "
                        f"title='{self.title}', "
                        f"creator_id={self.creator_id}, "
                        f"created_at={activity.created_at})")
        
        assert repr(activity) == expected_repr