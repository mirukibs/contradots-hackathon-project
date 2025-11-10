"""
Tests for DomainEvent base class.
Covers all methods and properties of the abstract base class.
"""
import uuid
from datetime import datetime, timezone
from src.domain.shared.events.domain_event import DomainEvent


class ConcreteDomainEvent(DomainEvent):
    """Concrete implementation for testing the abstract base class."""
    
    def __init__(self, event_id: uuid.UUID, occurred_at: datetime, aggregate_id: uuid.UUID, aggregate_type: str):
        super().__init__(event_id, occurred_at, aggregate_id, aggregate_type)


class TestDomainEvent:
    """Test DomainEvent base class implementation."""
    
    def test_init_with_all_parameters(self):
        """Test DomainEvent initialization with all parameters."""
        event_id = uuid.uuid4()
        occurred_at = datetime.now(timezone.utc)
        aggregate_id = uuid.uuid4()
        aggregate_type = "TestAggregate"
        
        event = ConcreteDomainEvent(event_id, occurred_at, aggregate_id, aggregate_type)
        
        assert event.event_id == event_id
        assert event.occurred_at == occurred_at
        assert event.aggregate_id == aggregate_id
        assert event.aggregate_type == aggregate_type
    
    def test_event_id_property(self):
        """Test event_id property returns the event ID."""
        event_id = uuid.uuid4()
        event = ConcreteDomainEvent(event_id, datetime.now(timezone.utc), uuid.uuid4(), "Test")
        
        assert event.event_id == event_id
    
    def test_occurred_at_property(self):
        """Test occurred_at property returns the timestamp."""
        occurred_at = datetime.now(timezone.utc)
        event = ConcreteDomainEvent(uuid.uuid4(), occurred_at, uuid.uuid4(), "Test")
        
        assert event.occurred_at == occurred_at
    
    def test_aggregate_id_property(self):
        """Test aggregate_id property returns the aggregate ID."""
        aggregate_id = uuid.uuid4()
        event = ConcreteDomainEvent(uuid.uuid4(), datetime.now(timezone.utc), aggregate_id, "Test")
        
        assert event.aggregate_id == aggregate_id
    
    def test_aggregate_type_property(self):
        """Test aggregate_type property returns the aggregate type."""
        aggregate_type = "TestAggregate"
        event = ConcreteDomainEvent(uuid.uuid4(), datetime.now(timezone.utc), uuid.uuid4(), aggregate_type)
        
        assert event.aggregate_type == aggregate_type
    
    def test_equality_same_event_id(self):
        """Test DomainEvent equality based on event ID."""
        event_id = uuid.uuid4()
        occurred_at = datetime.now(timezone.utc)
        aggregate_id = uuid.uuid4()
        
        event1 = ConcreteDomainEvent(event_id, occurred_at, aggregate_id, "Test")
        event2 = ConcreteDomainEvent(event_id, datetime.now(timezone.utc), uuid.uuid4(), "Other")
        
        assert event1 == event2
    
    def test_equality_different_event_id(self):
        """Test DomainEvent inequality with different event IDs."""
        event1 = ConcreteDomainEvent(uuid.uuid4(), datetime.now(timezone.utc), uuid.uuid4(), "Test")
        event2 = ConcreteDomainEvent(uuid.uuid4(), datetime.now(timezone.utc), uuid.uuid4(), "Test")
        
        assert event1 != event2
    
    def test_equality_with_non_domain_event(self):
        """Test DomainEvent inequality with non-DomainEvent object."""
        event = ConcreteDomainEvent(uuid.uuid4(), datetime.now(timezone.utc), uuid.uuid4(), "Test")
        
        assert event != "not-a-domain-event"
        assert event != 123
        assert event != None
    
    def test_hash_consistency(self):
        """Test DomainEvent hash is consistent."""
        event_id = uuid.uuid4()
        occurred_at = datetime.now(timezone.utc)
        aggregate_id = uuid.uuid4()
        
        event1 = ConcreteDomainEvent(event_id, occurred_at, aggregate_id, "Test")
        event2 = ConcreteDomainEvent(event_id, datetime.now(timezone.utc), uuid.uuid4(), "Other")
        
        assert hash(event1) == hash(event2)
    
    def test_hash_different_for_different_event_ids(self):
        """Test DomainEvent hash is different for different event IDs."""
        event1 = ConcreteDomainEvent(uuid.uuid4(), datetime.now(timezone.utc), uuid.uuid4(), "Test")
        event2 = ConcreteDomainEvent(uuid.uuid4(), datetime.now(timezone.utc), uuid.uuid4(), "Test")
        
        assert hash(event1) != hash(event2)
    
    def test_repr_representation(self):
        """Test DomainEvent repr representation."""
        event_id = uuid.uuid4()
        occurred_at = datetime.now(timezone.utc)
        aggregate_id = uuid.uuid4()
        aggregate_type = "TestAggregate"
        
        event = ConcreteDomainEvent(event_id, occurred_at, aggregate_id, aggregate_type)
        
        expected_repr = (f"ConcreteDomainEvent(event_id={event_id!r}, "
                        f"occurred_at={occurred_at!r}, aggregate_id={aggregate_id!r}, "
                        f"aggregate_type={aggregate_type!r})")
        assert repr(event) == expected_repr
    
    def test_can_be_used_as_dict_key(self):
        """Test DomainEvent can be used as dictionary key (hashable)."""
        event1 = ConcreteDomainEvent(uuid.uuid4(), datetime.now(timezone.utc), uuid.uuid4(), "Test1")
        event2 = ConcreteDomainEvent(uuid.uuid4(), datetime.now(timezone.utc), uuid.uuid4(), "Test2")
        
        test_dict = {
            event1: "Event 1",
            event2: "Event 2"
        }
        
        assert test_dict[event1] == "Event 1"
        assert test_dict[event2] == "Event 2"