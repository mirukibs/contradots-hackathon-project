"""
Integration tests for Django repository infrastructure.

This module tests the Django repository implementations to ensure they
correctly implement domain repository interfaces.
"""

import os
import django
from django.test import TestCase
from django.core.management import execute_from_command_line
import uuid
from datetime import datetime, timezone

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.infrastructure.django_app.infrastructure_settings')
django.setup()

from src.infrastructure.persistence.django_repositories import (
    DjangoPersonRepository,
    DjangoActivityRepository, 
    DjangoActionRepository
)
from src.infrastructure.django_app.models import PersonProfile, Activity as ActivityModel, Action as ActionModel
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.shared.value_objects.activity_id import ActivityId
from src.domain.shared.value_objects.action_id import ActionId
from src.domain.person.person import Person
from src.domain.person.role import Role
from src.domain.activity.activity import Activity
from src.domain.action.action import Action
from src.domain.action.action_status import ActionStatus
from django.contrib.auth.models import User
from django.db import transaction


class TestDjangoPersonRepository:
    """Test Django Person repository implementation."""
    
    def setup_method(self):
        """Set up test data."""
        self.repo = DjangoPersonRepository()
        
        # Clean up any existing test data more thoroughly
        PersonProfile.objects.filter(user__email__contains="test").delete()
        User.objects.filter(email__contains="test").delete()
        
        # Test person data with unique email
        self.person_id = PersonId.generate()
        unique_suffix = uuid.uuid4().hex[:8]
        self.test_email = f"test_person_{unique_suffix}@example.com"
        self.test_person = Person(
            person_id=self.person_id,
            name="Test Person",
            email=self.test_email,
            role=Role.MEMBER,
            reputation_score=100
        )
        
    def test_save_and_find_person(self):
        """Test saving and finding a person."""
        # Save person
        self.repo.save(self.test_person)
        
        # Find by ID
        found_person = self.repo.find_by_id(self.person_id)
        
        # Verify person found and properties match
        assert found_person is not None
        assert found_person.person_id == self.test_person.person_id
        assert found_person.name == self.test_person.name
        assert found_person.email == self.test_person.email
        assert found_person.role == self.test_person.role
        assert found_person.reputation_score == self.test_person.reputation_score
        
    def test_find_person_by_email(self):
        """Test finding person by email."""
        # Save person
        self.repo.save(self.test_person)
        
        # Find by email
        found_person = self.repo.find_by_email(self.test_email)
        
        # Verify person found
        assert found_person is not None
        assert found_person.email == self.test_email
        assert found_person.person_id == self.person_id
        
    def test_person_not_found(self):
        """Test handling of non-existent person."""
        non_existent_id = PersonId.generate()
        
        # Should raise ValueError for non-existent person
        try:
            self.repo.find_by_id(non_existent_id)
            assert False, "Expected ValueError for non-existent person"
        except ValueError as e:
            assert "not found" in str(e)
            
    def test_update_person(self):
        """Test updating an existing person."""
        # Save initial person
        self.repo.save(self.test_person)
        
        # Update person properties
        updated_person = Person(
            person_id=self.person_id,
            name="Updated Name",
            email=self.test_email,
            role=Role.LEAD,
            reputation_score=200
        )
        
        # Save updated person
        self.repo.save(updated_person)
        
        # Find updated person
        found_person = self.repo.find_by_id(self.person_id)
        
        # Verify updates
        assert found_person.name == "Updated Name"
        assert found_person.role == Role.LEAD
        assert found_person.reputation_score == 200
        
    def test_get_leaderboard(self):
        """Test getting leaderboard functionality."""
        # Create multiple test persons with different scores
        persons = []
        for i in range(3):
            person_id = PersonId.generate()
            email = f"leader_{i}_{uuid.uuid4().hex[:6]}@example.com"
            person = Person(
                person_id=person_id,
                name=f"Person {i}",
                email=email,
                role=Role.MEMBER,
                reputation_score=(i + 1) * 50  # 50, 100, 150
            )
            persons.append(person)
            self.repo.save(person)
        
        # Get leaderboard
        leaderboard = self.repo.get_leaderboard(limit=5)
        
        # Verify leaderboard order (highest score first)
        assert len(leaderboard) >= 3
        assert leaderboard[0].reputation_score >= leaderboard[1].reputation_score
        assert leaderboard[1].reputation_score >= leaderboard[2].reputation_score


class TestDjangoActivityRepository:
    """Test Django Activity repository implementation."""
    
    def setup_method(self):
        """Set up test data."""
        self.repo = DjangoActivityRepository()
        
        # Clean up existing test data
        ActivityModel.objects.filter(name__contains="Test Activity").delete()
        User.objects.filter(email__contains="activity_test").delete()
        
        # Create a test person first (required for activity creation)
        self.person_id = PersonId.generate()
        self.test_email = f"activity_test_{uuid.uuid4().hex[:8]}@example.com"
        test_user = User.objects.create_user(
            username=self.test_email,
            email=self.test_email,
            first_name="Activity Test Person"
        )
        PersonProfile.objects.create(
            user=test_user,
            person_id=self.person_id.value,
            role='LEAD',
            full_name="Activity Test Person",
            reputation_score=0
        )
        
        # Test activity data
        self.activity_id = ActivityId.generate()
        self.test_activity = Activity(
            activity_id=self.activity_id,
            title="Test Activity",
            description="Test activity description",
            creator_id=self.person_id
        )
        
    def test_save_and_find_activity(self):
        """Test saving and finding an activity."""
        # Save activity
        self.repo.save(self.test_activity)
        
        # Find by ID
        found_activity = self.repo.find_by_id(self.activity_id)
        
        # Verify activity found and properties match
        assert found_activity is not None
        assert found_activity.activity_id == self.test_activity.activity_id
        assert found_activity.title == self.test_activity.title
        assert found_activity.description == self.test_activity.description
        assert found_activity.creator_id == self.test_activity.creator_id
        
    def test_find_active_activities(self):
        """Test finding active activities."""
        # Save activity
        self.repo.save(self.test_activity)
        
        # Find active activities
        active_activities = self.repo.find_all_active()
        
        # Verify activity is in active list
        activity_ids = [activity.activity_id for activity in active_activities]
        assert self.activity_id in activity_ids
        
    def test_find_activities_by_creator(self):
        """Test finding activities by creator person."""
        # Save activity
        self.repo.save(self.test_activity)
        
        # Find activities by creator
        creator_activities = self.repo.find_by_creator_id(self.person_id)
        
        # Verify activity is in creator's activities
        assert len(creator_activities) >= 1
        activity_ids = [activity.activity_id for activity in creator_activities]
        assert self.activity_id in activity_ids


class TestDjangoActionRepository:
    """Test Django Action repository implementation."""
    
    def setup_method(self):
        """Set up test data."""
        self.repo = DjangoActionRepository()
        
        # Clean up existing test data
        ActionModel.objects.filter(description__contains="Test Action").delete()
        
        # Create test person and activity
        self.person_id = PersonId.generate()
        self.activity_id = ActivityId.generate()
        
        # Create Django user and person profile
        test_email = f"action_test_{uuid.uuid4().hex[:8]}@example.com"
        test_user = User.objects.create_user(
            username=test_email,
            email=test_email,
            first_name="Action Test Person"
        )
        PersonProfile.objects.create(
            user=test_user,
            person_id=self.person_id.value,
            role='MEMBER',
            full_name="Action Test Person",
            reputation_score=0
        )
        
        # Create test activity
        ActivityModel.objects.create(
            activity_id=self.activity_id.value,
            name="Test Activity for Actions",
            description="Test activity for action testing",
            points=50,
            lead_person=PersonProfile.objects.get(person_id=self.person_id.value),
            is_active=True
        )
        
        # Test action data
        self.action_id = ActionId.generate()
        self.test_action = Action(
            action_id=self.action_id,
            person_id=self.person_id,
            activity_id=self.activity_id,
            proof="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            status=ActionStatus.SUBMITTED
        )
        
    def test_save_and_find_action(self):
        """Test saving and finding an action."""
        # Save action
        self.repo.save(self.test_action)
        
        # Find by ID
        found_action = self.repo.find_by_id(self.action_id)
        
        # Verify action found and properties match
        assert found_action is not None
        assert found_action.action_id == self.test_action.action_id
        assert found_action.person_id == self.test_action.person_id
        assert found_action.activity_id == self.test_action.activity_id
        assert found_action.proof == self.test_action.proof
        assert found_action.status == self.test_action.status
        
    def test_find_actions_by_person(self):
        """Test finding actions by person."""
        # Save action
        self.repo.save(self.test_action)
        
        # Find actions by person
        person_actions = self.repo.find_actions_by_person(self.person_id)
        
        # Verify action is in person's actions
        assert len(person_actions) >= 1
        action_ids = [action.action_id for action in person_actions]
        assert self.action_id in action_ids
        
    def test_find_actions_by_activity(self):
        """Test finding actions by activity."""
        # Save action
        self.repo.save(self.test_action)
        
        # Find actions by activity
        activity_actions = self.repo.find_actions_by_activity(self.activity_id)
        
        # Verify action is in activity's actions
        assert len(activity_actions) >= 1
        action_ids = [action.action_id for action in activity_actions]
        assert self.action_id in action_ids
        
    def test_find_pending_actions(self):
        """Test finding pending actions."""
        # Save action (default status is SUBMITTED)
        self.repo.save(self.test_action)
        
        # Find pending actions
        pending_actions = self.repo.find_pending_actions()
        
        # Verify action is in pending list
        action_ids = [action.action_id for action in pending_actions]
        assert self.action_id in action_ids


def run_repository_tests():
    """Run all repository tests manually."""
    print("Running Django repository infrastructure tests...")
    
    # Use transaction rollback for test isolation
    with transaction.atomic():
        # Create a savepoint for rollback
        sid = transaction.savepoint()
        
        try:
            # Test Person Repository
            print("\n🧪 Testing PersonRepository...")
            person_test = TestDjangoPersonRepository()
            person_test.setup_method()
            
            person_test.test_save_and_find_person()
            print("✅ Person save and find test passed")
            
            # Rollback to clean state between tests
            transaction.savepoint_rollback(sid)
            sid = transaction.savepoint()
            
            person_test.setup_method()
            person_test.test_find_person_by_email()
            print("✅ Person find by email test passed")
            
            transaction.savepoint_rollback(sid)
            sid = transaction.savepoint()
            
            person_test.setup_method()
            person_test.test_person_not_found()
            print("✅ Person not found test passed")
            
            transaction.savepoint_rollback(sid)
            sid = transaction.savepoint()
            
            person_test.setup_method()
            person_test.test_update_person()
            print("✅ Person update test passed")
            
            transaction.savepoint_rollback(sid)
            sid = transaction.savepoint()
            
            person_test.setup_method()
            person_test.test_get_leaderboard()
            print("✅ Person leaderboard test passed")
            
            transaction.savepoint_rollback(sid)
            sid = transaction.savepoint()
            
            # Test Activity Repository
            print("\n🧪 Testing ActivityRepository...")
            activity_test = TestDjangoActivityRepository()
            activity_test.setup_method()
            
            activity_test.test_save_and_find_activity()
            print("✅ Activity save and find test passed")
            
            transaction.savepoint_rollback(sid)
            sid = transaction.savepoint()
            
            activity_test.setup_method()
            activity_test.test_find_active_activities()
            print("✅ Activity find active test passed")
            
            transaction.savepoint_rollback(sid)
            sid = transaction.savepoint()
            
            activity_test.setup_method()
            activity_test.test_find_activities_by_creator()
            print("✅ Activity find by creator test passed")
            
            transaction.savepoint_rollback(sid)
            sid = transaction.savepoint()
            
            # Test Action Repository
            print("\n🧪 Testing ActionRepository...")
            action_test = TestDjangoActionRepository()
            action_test.setup_method()
            
            action_test.test_save_and_find_action()
            print("✅ Action save and find test passed")
            
            transaction.savepoint_rollback(sid)
            sid = transaction.savepoint()
            
            action_test.setup_method()
            action_test.test_find_actions_by_person()
            print("✅ Action find by person test passed")
            
            transaction.savepoint_rollback(sid)
            sid = transaction.savepoint()
            
            action_test.setup_method()
            action_test.test_find_actions_by_activity()
            print("✅ Action find by activity test passed")
            
            transaction.savepoint_rollback(sid)
            sid = transaction.savepoint()
            
            action_test.setup_method()
            action_test.test_find_pending_actions()
            print("✅ Action find pending test passed")
            
            print("\n🎉 All Django repository tests passed!")
            
        except Exception as e:
            print(f"❌ Repository test failed: {e}")
            import traceback
            print(traceback.format_exc())
        finally:
            # Always rollback the transaction
            transaction.savepoint_rollback(sid)


if __name__ == "__main__":
    run_repository_tests()