"""Comprehensive tests for Event Infrastructure"""

from typing import List, Dict, Optional
from unittest.mock import Mock
from uuid import UUID, uuid4
from datetime import datetime
from src.application.events.event_store import EventStore
from src.application.events.event_publisher import EventPublisher  
from src.application.events.event_handler import EventHandler
from src.domain.shared.events.domain_event import DomainEvent


# Test implementations for interface testing
class MockDomainEvent(DomainEvent):
    """Test domain event implementation"""
    
    def __init__(self, aggregate_id: UUID, test_data: str = "test"):
        super().__init__(
            event_id=uuid4(),
            occurred_at=datetime.now(),
            aggregate_id=aggregate_id,
            aggregate_type="TestAggregate"
        )
        self.test_data = test_data


class ConcreteEventStore(EventStore):
    """Concrete test implementation of EventStore for testing purposes"""
    
    def __init__(self):
        self._events: List[DomainEvent] = []
        self._aggregate_events: Dict[UUID, List[DomainEvent]] = {}
        
    def append(self, aggregate_id: Optional[UUID], events: List[DomainEvent]) -> None:
        if aggregate_id is None:
            raise ValueError("Aggregate ID cannot be None")
        if not events:
            raise ValueError("Events list cannot be empty")
            
        for event in events:
            self._events.append(event)
            if aggregate_id not in self._aggregate_events:
                self._aggregate_events[aggregate_id] = []
            self._aggregate_events[aggregate_id].append(event)
    
    def get_events(self, aggregate_id: UUID) -> List[DomainEvent]:
        return self._aggregate_events.get(aggregate_id, [])
    
    def get_all_events(self) -> List[DomainEvent]:
        return self._events.copy()


class ConcreteEventHandler(EventHandler[MockDomainEvent]):
    """Concrete test implementation of EventHandler"""
    
    def __init__(self):
        self.handled_events: List[MockDomainEvent] = []
        
    def handle(self, event: MockDomainEvent) -> None:
        self.handled_events.append(event)
    
    def can_handle(self, event: DomainEvent) -> bool:
        return isinstance(event, MockDomainEvent)


class ConcreteEventPublisher(EventPublisher):
    """Concrete test implementation of EventPublisher"""
    
    def __init__(self, event_store: EventStore):
        self._event_store = event_store
        self._handlers: List[EventHandler[DomainEvent]] = []
        self.published_events: List[DomainEvent] = []
        
    def publish(self, event: DomainEvent) -> None:
        if not event:
            raise ValueError("Event cannot be None")
            
        self.published_events.append(event)
        
        # Store event
        self._event_store.append(event.aggregate_id, [event])
        
        # Notify handlers that can handle this event type
        for handler in self._handlers:
            if handler.can_handle(event):
                # Type checker doesn't know the generic type at runtime
                handler.handle(event)  # type: ignore
    
    def publish_all(self, events: List[DomainEvent]) -> None:
        if not events:
            raise ValueError("Events list cannot be empty")
            
        for event in events:
            self.publish(event)
    
    @property
    def event_store(self) -> EventStore:
        return self._event_store
    
    @property  
    def handlers(self) -> List[EventHandler[DomainEvent]]:
        return self._handlers.copy()
    
    def add_handler(self, handler: EventHandler[DomainEvent]) -> None:
        """Helper method to add handlers for testing"""
        self._handlers.append(handler)


class TestEventStoreImplementation:
    """Test suite for EventStore interface and implementations"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.event_store = ConcreteEventStore()
        self.aggregate_id = uuid4()
        self.test_event1 = MockDomainEvent(self.aggregate_id, "event1")
        self.test_event2 = MockDomainEvent(self.aggregate_id, "event2")
        
    def test_event_store_append_single_event(self):
        """Test appending a single event to the store"""
        # Act
        self.event_store.append(self.aggregate_id, [self.test_event1])
        
        # Assert
        stored_events = self.event_store.get_events(self.aggregate_id)
        assert len(stored_events) == 1
        assert stored_events[0] == self.test_event1
        
        all_events = self.event_store.get_all_events()
        assert len(all_events) == 1
        assert all_events[0] == self.test_event1
    
    def test_event_store_append_multiple_events(self):
        """Test appending multiple events to the store"""
        # Act
        self.event_store.append(self.aggregate_id, [self.test_event1, self.test_event2])
        
        # Assert
        stored_events = self.event_store.get_events(self.aggregate_id)
        assert len(stored_events) == 2
        assert stored_events[0] == self.test_event1
        assert stored_events[1] == self.test_event2
    
    def test_event_store_multiple_aggregates(self):
        """Test storing events for multiple aggregates"""
        # Arrange
        aggregate_id2 = uuid4()
        event3 = MockDomainEvent(aggregate_id2, "event3")
        
        # Act
        self.event_store.append(self.aggregate_id, [self.test_event1])
        self.event_store.append(aggregate_id2, [event3])
        
        # Assert
        events1 = self.event_store.get_events(self.aggregate_id)
        events2 = self.event_store.get_events(aggregate_id2)
        
        assert len(events1) == 1
        assert len(events2) == 1
        assert events1[0] == self.test_event1
        assert events2[0] == event3
        
        all_events = self.event_store.get_all_events()
        assert len(all_events) == 2
    
    def test_event_store_append_empty_events_list(self):
        """Test appending empty events list raises error"""
        # Act & Assert
        try:
            self.event_store.append(self.aggregate_id, [])
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Events list cannot be empty" in str(e)
    
    def test_event_store_append_none_aggregate_id(self):
        """Test appending with None aggregate ID raises error"""
        # Act & Assert
        try:
            self.event_store.append(None, [self.test_event1])  # type: ignore
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Aggregate ID cannot be None" in str(e)
    
    def test_event_store_get_events_nonexistent_aggregate(self):
        """Test getting events for nonexistent aggregate returns empty list"""
        # Arrange
        nonexistent_id = uuid4()
        
        # Act
        events = self.event_store.get_events(nonexistent_id)
        
        # Assert
        assert events == []
    
    def test_event_store_get_all_events_empty(self):
        """Test getting all events when store is empty"""
        # Act
        events = self.event_store.get_all_events()
        
        # Assert
        assert events == []
    
    def test_event_store_events_isolation(self):
        """Test that returned events list doesn't affect internal storage"""
        # Arrange
        self.event_store.append(self.aggregate_id, [self.test_event1])
        
        # Act
        events = self.event_store.get_all_events()
        events.clear()  # Modify returned list
        
        # Assert - internal storage should be unaffected
        stored_events = self.event_store.get_all_events()
        assert len(stored_events) == 1
        assert stored_events[0] == self.test_event1


class TestEventHandlerImplementation:
    """Test suite for EventHandler interface and implementations"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.handler = ConcreteEventHandler()
        self.aggregate_id = uuid4()
        self.test_event = MockDomainEvent(self.aggregate_id, "test_data")
        
    def test_event_handler_handle_valid_event(self):
        """Test handling a valid event"""
        # Act
        self.handler.handle(self.test_event)
        
        # Assert
        assert len(self.handler.handled_events) == 1
        assert self.handler.handled_events[0] == self.test_event
    
    def test_event_handler_can_handle_valid_event(self):
        """Test can_handle returns True for valid event"""
        # Act
        result = self.handler.can_handle(self.test_event)
        
        # Assert
        assert result is True
    
    def test_event_handler_can_handle_invalid_event(self):
        """Test can_handle returns False for invalid event"""
        # Arrange
        invalid_event = Mock(spec=DomainEvent)
        
        # Act
        result = self.handler.can_handle(invalid_event)
        
        # Assert
        assert result is False
    
    def test_event_handler_handle_multiple_events(self):
        """Test handling multiple events"""
        # Arrange
        event2 = MockDomainEvent(self.aggregate_id, "test_data2")
        event3 = MockDomainEvent(self.aggregate_id, "test_data3")
        
        # Act
        self.handler.handle(self.test_event)
        self.handler.handle(event2)
        self.handler.handle(event3)
        
        # Assert
        assert len(self.handler.handled_events) == 3
        assert self.handler.handled_events[0].test_data == "test_data"
        assert self.handler.handled_events[1].test_data == "test_data2"
        assert self.handler.handled_events[2].test_data == "test_data3"


class TestEventPublisherImplementation:
    """Test suite for EventPublisher interface and implementations"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.event_store = ConcreteEventStore()
        self.publisher = ConcreteEventPublisher(self.event_store)
        self.handler = ConcreteEventHandler()
        self.aggregate_id = uuid4()
        self.test_event = MockDomainEvent(self.aggregate_id, "test_data")
        
    def test_event_publisher_publish_single_event(self):
        """Test publishing a single event"""
        # Arrange
        self.publisher.add_handler(self.handler)  # type: ignore
        
        # Act
        self.publisher.publish(self.test_event)
        
        # Assert
        assert len(self.publisher.published_events) == 1
        assert self.publisher.published_events[0] == self.test_event
        
        # Check event was stored
        stored_events = self.event_store.get_events(self.aggregate_id)
        assert len(stored_events) == 1
        assert stored_events[0] == self.test_event
        
        # Check handler was notified
        assert len(self.handler.handled_events) == 1
        assert self.handler.handled_events[0] == self.test_event
    
    def test_event_publisher_publish_multiple_events(self):
        """Test publishing multiple events"""
        # Arrange
        event2 = MockDomainEvent(self.aggregate_id, "test_data2")
        self.publisher.add_handler(self.handler)  # type: ignore
        
        # Act
        self.publisher.publish_all([self.test_event, event2])
        
        # Assert
        assert len(self.publisher.published_events) == 2
        assert len(self.handler.handled_events) == 2
        
        stored_events = self.event_store.get_all_events()
        assert len(stored_events) == 2
    
    def test_event_publisher_publish_none_event(self):
        """Test publishing None event raises error"""
        # Act & Assert
        try:
            self.publisher.publish(None)  # type: ignore
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Event cannot be None" in str(e)
    
    def test_event_publisher_publish_all_empty_list(self):
        """Test publishing empty events list raises error"""
        # Act & Assert
        try:
            self.publisher.publish_all([])
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Events list cannot be empty" in str(e)
    
    def test_event_publisher_multiple_handlers(self):
        """Test publishing to multiple handlers"""
        # Arrange
        handler2 = ConcreteEventHandler()
        self.publisher.add_handler(self.handler)  # type: ignore
        self.publisher.add_handler(handler2)  # type: ignore
        
        # Act
        self.publisher.publish(self.test_event)
        
        # Assert
        assert len(self.handler.handled_events) == 1
        assert len(handler2.handled_events) == 1
        assert self.handler.handled_events[0] == self.test_event
        assert handler2.handled_events[0] == self.test_event
    
    def test_event_publisher_handler_filtering(self):
        """Test that handlers only receive events they can handle"""
        # Arrange
        class DifferentEvent(DomainEvent):
            def __init__(self):
                super().__init__(
                    event_id=uuid4(),
                    occurred_at=datetime.now(),
                    aggregate_id=uuid4(),
                    aggregate_type="DifferentAggregate"
                )
        
        different_event = DifferentEvent()
        self.publisher.add_handler(self.handler)  # type: ignore
        
        # Act
        self.publisher.publish(different_event)
        
        # Assert
        # Handler should not have handled the different event type
        assert len(self.handler.handled_events) == 0
        # But publisher should still have published it
        assert len(self.publisher.published_events) == 1
    
    def test_event_publisher_event_store_property(self):
        """Test event_store property returns correct store"""
        # Act & Assert
        assert self.publisher.event_store == self.event_store
    
    def test_event_publisher_handlers_property(self):
        """Test handlers property returns copy of handlers list"""
        # Arrange
        self.publisher.add_handler(self.handler)  # type: ignore
        
        # Act
        handlers = self.publisher.handlers
        
        # Assert
        assert len(handlers) == 1
        assert handlers[0] == self.handler
        
        # Modify returned list should not affect internal handlers
        handlers.clear()
        assert len(self.publisher.handlers) == 1
    
    def test_event_publisher_integration_with_event_store(self):
        """Test full integration between publisher and event store"""
        # Arrange
        aggregate_id2 = uuid4()
        event2 = MockDomainEvent(aggregate_id2, "different_aggregate")
        
        # Act
        self.publisher.publish(self.test_event)
        self.publisher.publish(event2)
        
        # Assert
        # Check events are stored separately by aggregate
        events1 = self.event_store.get_events(self.aggregate_id)
        events2 = self.event_store.get_events(aggregate_id2)
        
        assert len(events1) == 1
        assert len(events2) == 1
        assert events1[0] == self.test_event
        assert events2[0] == event2
        
        # Check all events are retrievable
        all_events = self.event_store.get_all_events()
        assert len(all_events) == 2


class TestEventInfrastructureIntegration:
    """Integration tests for event infrastructure components working together"""
    
    def setup_method(self):
        """Set up test fixtures for integration testing"""
        self.event_store = ConcreteEventStore()
        self.publisher = ConcreteEventPublisher(self.event_store)
        self.handler = ConcreteEventHandler()
        
        # Test data
        self.aggregate_id = uuid4()
        self.test_event = MockDomainEvent(self.aggregate_id, "integration_test")
    
    def test_full_event_flow_integration(self):
        """Test complete event flow from publishing to handling to storage"""
        # Arrange
        self.publisher.add_handler(self.handler)  # type: ignore
        
        # Act
        self.publisher.publish(self.test_event)
        
        # Assert - event flows through all components
        # 1. Publisher publishes the event
        assert len(self.publisher.published_events) == 1
        assert self.publisher.published_events[0] == self.test_event
        
        # 2. Event is stored in event store
        stored_events = self.event_store.get_events(self.aggregate_id)
        assert len(stored_events) == 1
        assert stored_events[0] == self.test_event
        
        # 3. Handler processes the event
        assert len(self.handler.handled_events) == 1
        assert self.handler.handled_events[0] == self.test_event
    
    def test_event_infrastructure_error_handling(self):
        """Test error handling across event infrastructure components"""
        # Test invalid aggregate ID
        try:
            self.event_store.append(None, [self.test_event])  # type: ignore
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
        
        # Test empty events list
        try:
            self.event_store.append(self.aggregate_id, [])
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
        
        # Test publishing None event
        try:
            self.publisher.publish(None)  # type: ignore
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
    
    def test_event_infrastructure_with_multiple_aggregates(self):
        """Test event infrastructure handling multiple aggregates"""
        # Arrange
        aggregate_id2 = uuid4()
        aggregate_id3 = uuid4()
        
        event1 = MockDomainEvent(self.aggregate_id, "agg1_event")
        event2 = MockDomainEvent(aggregate_id2, "agg2_event")
        event3 = MockDomainEvent(aggregate_id3, "agg3_event")
        
        self.publisher.add_handler(self.handler)  # type: ignore
        
        # Act
        self.publisher.publish_all([event1, event2, event3])
        
        # Assert
        # All events published
        assert len(self.publisher.published_events) == 3
        
        # Events stored by aggregate
        agg1_events = self.event_store.get_events(self.aggregate_id)
        agg2_events = self.event_store.get_events(aggregate_id2)
        agg3_events = self.event_store.get_events(aggregate_id3)
        
        assert len(agg1_events) == 1
        assert len(agg2_events) == 1
        assert len(agg3_events) == 1
        
        # All events handled
        assert len(self.handler.handled_events) == 3
        
        # Total events in store
        all_events = self.event_store.get_all_events()
        assert len(all_events) == 3