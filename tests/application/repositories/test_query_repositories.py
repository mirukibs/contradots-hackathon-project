"""Unit tests for Query Repository implementations"""

from typing import Dict, List
from abc import ABC

from src.domain.shared.value_objects.person_id import PersonId
from src.domain.shared.value_objects.activity_id import ActivityId
from src.application.repositories.action_query_repository import ActionQueryRepository
from src.application.repositories.activity_query_repository import ActivityQueryRepository
from src.application.repositories.leaderboard_query_repository import LeaderboardQueryRepository
from src.application.dtos.action_dto import ActionDto
from src.application.dtos.activity_dto import ActivityDto
from src.application.dtos.activity_details_dto import ActivityDetailsDto
from src.application.dtos.leaderboard_dto import LeaderboardDto
from src.domain.action.action_status import ActionStatus


class ConcreteActionQueryRepository(ActionQueryRepository):
    """Concrete implementation for testing ActionQueryRepository interface"""
    
    def __init__(self):
        self.actions: List[ActionDto] = []
        self.should_raise_error = False
        self.error_message = ""
        # Store mapping for filtering since DTOs don't have domain IDs
        self.action_person_map: Dict[str, str] = {}  # actionId -> personId
        self.action_activity_map: Dict[str, str] = {}  # actionId -> activityId
    
    def get_pending_validations(self) -> List[ActionDto]:
        """Test implementation of get_pending_validations"""
        if self.should_raise_error:
            raise RuntimeError(self.error_message)
        
        return [action for action in self.actions if action.status == ActionStatus.SUBMITTED]
    
    def get_person_actions(self, person_id: PersonId) -> List[ActionDto]:
        """Test implementation of get_person_actions"""
        if self.should_raise_error:
            raise ValueError(self.error_message)
        
        person_id_str = str(person_id)
        return [action for action in self.actions 
                if self.action_person_map.get(action.actionId) == person_id_str]
    
    def get_activity_actions(self, activity_id: ActivityId) -> List[ActionDto]:
        """Test implementation of get_activity_actions"""
        if self.should_raise_error:
            raise ValueError(self.error_message)
        
        activity_id_str = str(activity_id)
        return [action for action in self.actions 
                if self.action_activity_map.get(action.actionId) == activity_id_str]


class ConcreteActivityQueryRepository(ActivityQueryRepository):
    """Concrete implementation for testing ActivityQueryRepository interface"""
    
    def __init__(self):
        self.activities: List[ActivityDto] = []
        self.activity_details: Dict[str, ActivityDetailsDto] = {}
        self.should_raise_error = False
        self.error_message = ""
    
    def get_active_activities(self) -> List[ActivityDto]:
        """Test implementation of get_active_activities"""
        if self.should_raise_error:
            raise RuntimeError(self.error_message)
        
        return self.activities
    
    def get_activity_details(self, activity_id: ActivityId) -> ActivityDetailsDto:
        """Test implementation of get_activity_details"""
        if self.should_raise_error:
            raise ValueError(self.error_message)
        
        activity_id_str = str(activity_id)
        if activity_id_str not in self.activity_details:
            raise ValueError(f"Activity not found: {activity_id}")
        
        return self.activity_details[activity_id_str]


class ConcreteLeaderboardQueryRepository(LeaderboardQueryRepository):
    """Concrete implementation for testing LeaderboardQueryRepository interface"""
    
    def __init__(self):
        self.leaderboard_entries: List[LeaderboardDto] = []
        self.person_ranks: Dict[str, int] = {}
        self.should_raise_error = False
        self.error_message = ""
    
    def get_leaderboard(self) -> List[LeaderboardDto]:
        """Test implementation of get_leaderboard"""
        if self.should_raise_error:
            raise RuntimeError(self.error_message)
        
        return self.leaderboard_entries
    
    def get_person_rank(self, person_id: PersonId) -> int:
        """Test implementation of get_person_rank"""
        if self.should_raise_error:
            raise ValueError(self.error_message)
        
        person_id_str = str(person_id)
        if person_id_str not in self.person_ranks:
            raise ValueError(f"Person not found: {person_id}")
        
        return self.person_ranks[person_id_str]


class TestActionQueryRepository:
    """Test suite for ActionQueryRepository interface and implementations"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.repository = ConcreteActionQueryRepository()
        
        # Test data - using string IDs for simplicity
        self.person_id_1 = "person_1"
        self.person_id_2 = "person_2"
        self.activity_id_1 = "activity_1"
        self.activity_id_2 = "activity_2"
        
        # Create test actions
        self.action_dto_1 = ActionDto(
            actionId="action_1",
            personName="John Doe",
            activityName="Beach Cleanup",
            description="Action 1",
            status=ActionStatus.SUBMITTED,
            submittedAt="2024-01-01T00:00:00Z"
        )
        
        self.action_dto_2 = ActionDto(
            actionId="action_2",
            personName="Jane Smith",
            activityName="Beach Cleanup",
            description="Action 2",
            status=ActionStatus.VALIDATED,
            submittedAt="2024-01-02T00:00:00Z"
        )
        
        self.action_dto_3 = ActionDto(
            actionId="action_3",
            personName="John Doe",
            activityName="Park Cleanup",
            description="Action 3",
            status=ActionStatus.SUBMITTED,
            submittedAt="2024-01-03T00:00:00Z"
        )
        
        # Add actions to repository
        self.repository.actions = [self.action_dto_1, self.action_dto_2, self.action_dto_3]
        
        # Set up mappings for filtering
        self.repository.action_person_map = {
            "action_1": self.person_id_1,
            "action_2": self.person_id_2,
            "action_3": self.person_id_1,
        }
        self.repository.action_activity_map = {
            "action_1": self.activity_id_1,
            "action_2": self.activity_id_1,
            "action_3": self.activity_id_2,
        }

    def test_interface_is_abstract(self):
        """Test that ActionQueryRepository is an abstract base class"""
        assert issubclass(ActionQueryRepository, ABC)
        
        # Test that abstract methods are properly defined
        abstract_methods = ActionQueryRepository.__abstractmethods__
        expected_methods = {'get_pending_validations', 'get_person_actions', 'get_activity_actions'}
        assert abstract_methods == expected_methods

    def test_get_pending_validations_returns_submitted_actions(self):
        """Test get_pending_validations returns only actions with SUBMITTED status"""
        # Act
        result = self.repository.get_pending_validations()
        
        # Assert
        assert len(result) == 2  # action_dto_1 and action_dto_3 are SUBMITTED
        assert self.action_dto_1 in result
        assert self.action_dto_3 in result
        assert self.action_dto_2 not in result  # VALIDATED status

    def test_get_pending_validations_empty_when_no_submitted(self):
        """Test get_pending_validations returns empty list when no submitted actions"""
        # Arrange - change all actions to non-submitted status
        for action in self.repository.actions:
            action.__dict__['status'] = ActionStatus.VALIDATED
        
        # Act
        result = self.repository.get_pending_validations()
        
        # Assert
        assert len(result) == 0

    def test_get_pending_validations_handles_repository_error(self):
        """Test get_pending_validations handles repository errors"""
        # Arrange
        self.repository.should_raise_error = True
        self.repository.error_message = "Database connection failed"
        
        # Act & Assert
        try:
            self.repository.get_pending_validations()
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "Database connection failed" in str(e)

    def test_get_person_actions_returns_correct_actions(self):
        """Test get_person_actions returns actions for specific person"""
        # Act
        result = self.repository.get_person_actions(PersonId(self.person_id_1))
        
        # Assert
        assert len(result) == 2  # action_dto_1 and action_dto_3
        assert self.action_dto_1 in result
        assert self.action_dto_3 in result
        assert self.action_dto_2 not in result  # Different person

    def test_get_person_actions_with_no_actions_for_person(self):
        """Test get_person_actions returns empty list for person with no actions"""
        # Arrange
        unknown_person_id = "unknown_person"
        
        # Act
        result = self.repository.get_person_actions(PersonId(unknown_person_id))
        
        # Assert
        assert len(result) == 0

    def test_get_person_actions_handles_repository_error(self):
        """Test get_person_actions handles repository errors"""
        # Arrange
        self.repository.should_raise_error = True
        self.repository.error_message = "Person lookup failed"
        
        # Act & Assert
        try:
            self.repository.get_person_actions(PersonId(self.person_id_1))
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Person lookup failed" in str(e)

    def test_get_activity_actions_returns_correct_actions(self):
        """Test get_activity_actions returns actions for specific activity"""
        # Act
        result = self.repository.get_activity_actions(ActivityId(self.activity_id_1))
        
        # Assert
        assert len(result) == 2  # action_dto_1 and action_dto_2
        assert self.action_dto_1 in result
        assert self.action_dto_2 in result
        assert self.action_dto_3 not in result  # Different activity

    def test_get_activity_actions_empty_for_unknown_activity(self):
        """Test get_activity_actions returns empty list for unknown activity"""
        # Arrange
        unknown_activity_id = "unknown_activity"
        
        # Act
        result = self.repository.get_activity_actions(ActivityId(unknown_activity_id))
        
        # Assert
        assert len(result) == 0

    def test_get_activity_actions_handles_repository_error(self):
        """Test get_activity_actions handles repository errors"""
        # Arrange
        self.repository.should_raise_error = True
        self.repository.error_message = "Activity lookup failed"
        
        # Act & Assert
        try:
            self.repository.get_activity_actions(ActivityId(self.activity_id_1))
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Activity lookup failed" in str(e)


class TestActivityQueryRepository:
    """Test suite for ActivityQueryRepository interface and implementations"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.repository = ConcreteActivityQueryRepository()
        
        # Test data - using string IDs for simplicity
        self.activity_id_1 = "activity_1"
        self.activity_id_2 = "activity_2"
        self.creator_id = "creator_1"
        
        # Create test activities
        self.activity_dto_1 = ActivityDto(
            activityId=self.activity_id_1,
            name="Beach Cleanup",
            description="Clean the beach together",
            points=100,
            leadName="Lead User",
            isActive=True
        )
        
        self.activity_dto_2 = ActivityDto(
            activityId=self.activity_id_2,
            name="Park Cleanup",
            description="Clean the park area",
            points=150,
            leadName="Lead User",
            isActive=True
        )
        
        # Create test activity details
        self.activity_details_1 = ActivityDetailsDto(
            activityId=self.activity_id_1,
            name="Beach Cleanup",
            description="Clean the beach together",
            points=100,
            leadName="Lead User",
            isActive=True,
            participantCount=5,
            totalActionsSubmitted=3
        )
        
        # Add data to repository
        self.repository.activities = [self.activity_dto_1, self.activity_dto_2]
        self.repository.activity_details = {self.activity_id_1: self.activity_details_1}

    def test_interface_is_abstract(self):
        """Test that ActivityQueryRepository is an abstract base class"""
        assert issubclass(ActivityQueryRepository, ABC)
        
        # Test that abstract methods are properly defined
        abstract_methods = ActivityQueryRepository.__abstractmethods__
        expected_methods = {'get_active_activities', 'get_activity_details'}
        assert abstract_methods == expected_methods

    def test_get_active_activities_returns_all_activities(self):
        """Test get_active_activities returns all active activities"""
        # Act
        result = self.repository.get_active_activities()
        
        # Assert
        assert len(result) == 2
        assert self.activity_dto_1 in result
        assert self.activity_dto_2 in result

    def test_get_active_activities_empty_when_no_activities(self):
        """Test get_active_activities returns empty list when no activities"""
        # Arrange
        self.repository.activities = []
        
        # Act
        result = self.repository.get_active_activities()
        
        # Assert
        assert len(result) == 0

    def test_get_active_activities_handles_repository_error(self):
        """Test get_active_activities handles repository errors"""
        # Arrange
        self.repository.should_raise_error = True
        self.repository.error_message = "Database query failed"
        
        # Act & Assert
        try:
            self.repository.get_active_activities()
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "Database query failed" in str(e)

    def test_get_activity_details_returns_correct_details(self):
        """Test get_activity_details returns correct activity details"""
        # Act
        result = self.repository.get_activity_details(ActivityId(self.activity_id_1))
        
        # Assert
        assert result == self.activity_details_1
        assert result.activityId == self.activity_id_1
        assert result.name == "Beach Cleanup"
        assert result.participantCount == 5

    def test_get_activity_details_raises_error_for_unknown_activity(self):
        """Test get_activity_details raises error for unknown activity"""
        # Arrange
        unknown_activity_id = "unknown_activity"
        
        # Act & Assert
        try:
            self.repository.get_activity_details(ActivityId(unknown_activity_id))
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Activity not found" in str(e)

    def test_get_activity_details_handles_repository_error(self):
        """Test get_activity_details handles repository errors"""
        # Arrange
        self.repository.should_raise_error = True
        self.repository.error_message = "Details lookup failed"
        
        # Act & Assert
        try:
            self.repository.get_activity_details(ActivityId(self.activity_id_1))
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Details lookup failed" in str(e)


class TestLeaderboardQueryRepository:
    """Test suite for LeaderboardQueryRepository interface and implementations"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.repository = ConcreteLeaderboardQueryRepository()
        
        # Test data - using string IDs for simplicity
        self.person_id_1 = "person_1"
        self.person_id_2 = "person_2"
        self.person_id_3 = "person_3"
        
        # Create test leaderboard entries (sorted by rank)
        self.leaderboard_entry_1 = LeaderboardDto(
            personId=self.person_id_1,
            name="Alice Smith",
            reputationScore=100,
            rank=1
        )
        
        self.leaderboard_entry_2 = LeaderboardDto(
            personId=self.person_id_2,
            name="Bob Johnson",
            reputationScore=85,
            rank=2
        )
        
        self.leaderboard_entry_3 = LeaderboardDto(
            personId=self.person_id_3,
            name="Charlie Brown",
            reputationScore=70,
            rank=3
        )
        
        # Add data to repository
        self.repository.leaderboard_entries = [
            self.leaderboard_entry_1,
            self.leaderboard_entry_2,
            self.leaderboard_entry_3
        ]
        
        self.repository.person_ranks = {
            self.person_id_1: 1,
            self.person_id_2: 2,
            self.person_id_3: 3
        }

    def test_interface_is_abstract(self):
        """Test that LeaderboardQueryRepository is an abstract base class"""
        assert issubclass(LeaderboardQueryRepository, ABC)
        
        # Test that abstract methods are properly defined
        abstract_methods = LeaderboardQueryRepository.__abstractmethods__
        expected_methods = {'get_leaderboard', 'get_person_rank'}
        assert abstract_methods == expected_methods

    def test_get_leaderboard_returns_sorted_entries(self):
        """Test get_leaderboard returns entries in rank order"""
        # Act
        result = self.repository.get_leaderboard()
        
        # Assert
        assert len(result) == 3
        assert result[0] == self.leaderboard_entry_1  # Rank 1
        assert result[1] == self.leaderboard_entry_2  # Rank 2
        assert result[2] == self.leaderboard_entry_3  # Rank 3
        
        # Verify ordering by reputation score
        assert result[0].reputationScore >= result[1].reputationScore
        assert result[1].reputationScore >= result[2].reputationScore

    def test_get_leaderboard_empty_when_no_entries(self):
        """Test get_leaderboard returns empty list when no entries"""
        # Arrange
        self.repository.leaderboard_entries = []
        
        # Act
        result = self.repository.get_leaderboard()
        
        # Assert
        assert len(result) == 0

    def test_get_leaderboard_handles_repository_error(self):
        """Test get_leaderboard handles repository errors"""
        # Arrange
        self.repository.should_raise_error = True
        self.repository.error_message = "Leaderboard query failed"
        
        # Act & Assert
        try:
            self.repository.get_leaderboard()
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "Leaderboard query failed" in str(e)

    def test_get_person_rank_returns_correct_rank(self):
        """Test get_person_rank returns correct rank for each person"""
        # Test each person's rank
        assert self.repository.get_person_rank(PersonId(self.person_id_1)) == 1
        assert self.repository.get_person_rank(PersonId(self.person_id_2)) == 2
        assert self.repository.get_person_rank(PersonId(self.person_id_3)) == 3

    def test_get_person_rank_raises_error_for_unknown_person(self):
        """Test get_person_rank raises error for unknown person"""
        # Arrange
        unknown_person_id = "unknown_person"
        
        # Act & Assert
        try:
            self.repository.get_person_rank(PersonId(unknown_person_id))
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert f"Person not found: {unknown_person_id}" in str(e)

    def test_get_person_rank_handles_repository_error(self):
        """Test get_person_rank handles repository errors"""
        # Arrange
        self.repository.should_raise_error = True
        self.repository.error_message = "Rank lookup failed"
        
        # Act & Assert
        try:
            self.repository.get_person_rank(PersonId(self.person_id_1))
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Rank lookup failed" in str(e)


class TestQueryRepositoriesIntegration:
    """Integration tests for query repositories working together"""
    
    def setup_method(self):
        """Set up test fixtures for integration testing"""
        self.action_repo = ConcreteActionQueryRepository()
        self.activity_repo = ConcreteActivityQueryRepository()
        self.leaderboard_repo = ConcreteLeaderboardQueryRepository()
        
        # Common test data - using string IDs for simplicity
        self.person_id = "test_person"
        self.activity_id = "test_activity"
        
        # Set up related data across repositories
        self.setup_related_data()

    def setup_related_data(self):
        """Set up related data across all repositories"""
        # Activity data
        activity_dto = ActivityDto(
            activityId=self.activity_id,
            name="Beach Cleanup",
            description="Community beach cleanup",
            points=100,
            leadName="John Doe",
            isActive=True
        )
        self.activity_repo.activities = [activity_dto]
        
        activity_details = ActivityDetailsDto(
            activityId=self.activity_id,
            name="Beach Cleanup",
            description="Community beach cleanup",
            points=100,
            leadName="John Doe",
            isActive=True,
            participantCount=1,
            totalActionsSubmitted=1
        )
        self.activity_repo.activity_details = {self.activity_id: activity_details}
        
        # Action data
        action_dto = ActionDto(
            actionId="test_action",
            personName="John Doe",
            activityName="Beach Cleanup",
            description="Cleaned beach section A",
            status=ActionStatus.VALIDATED,
            submittedAt="2024-01-01T00:00:00Z"
        )
        self.action_repo.actions = [action_dto]
        # Set up action mappings for filtering
        self.action_repo.action_person_map = {"test_action": self.person_id}
        self.action_repo.action_activity_map = {"test_action": self.activity_id}
        
        # Leaderboard data
        leaderboard_entry = LeaderboardDto(
            personId=self.person_id,
            name="John Doe",
            reputationScore=60,  # Base 50 + 10 for validated action
            rank=1
        )
        self.leaderboard_repo.leaderboard_entries = [leaderboard_entry]
        self.leaderboard_repo.person_ranks = {self.person_id: 1}

    def test_query_repositories_data_consistency(self):
        """Test that related data across repositories is consistent"""
        # Get data from each repository
        activities = self.activity_repo.get_active_activities()
        person_actions = self.action_repo.get_person_actions(PersonId(self.person_id))
        activity_actions = self.action_repo.get_activity_actions(ActivityId(self.activity_id))
        leaderboard = self.leaderboard_repo.get_leaderboard()
        person_rank = self.leaderboard_repo.get_person_rank(PersonId(self.person_id))
        
        # Verify data consistency
        assert len(activities) == 1
        assert activities[0].activityId == self.activity_id
        
        assert len(person_actions) == 1
        assert person_actions[0].personName == "John Doe"
        assert person_actions[0].activityName == "Beach Cleanup"
        
        assert len(activity_actions) == 1
        assert activity_actions[0].activityName == "Beach Cleanup"
        assert activity_actions[0].personName == "John Doe"
        
        assert len(leaderboard) == 1
        assert leaderboard[0].personId == self.person_id
        assert leaderboard[0].reputationScore == 60
        
        assert person_rank == 1

    def test_cross_repository_queries(self):
        """Test querying related data across multiple repositories"""
        # Query activity details and related actions
        activity_details = self.activity_repo.get_activity_details(ActivityId(self.activity_id))
        related_actions = self.action_repo.get_activity_actions(ActivityId(self.activity_id))
        
        # Verify consistency
        assert activity_details.totalActionsSubmitted == len(related_actions)
        
        # Query person's actions and rank
        person_actions = self.action_repo.get_person_actions(PersonId(self.person_id))
        person_rank = self.leaderboard_repo.get_person_rank(PersonId(self.person_id))
        
        # Verify person has actions and a rank
        assert len(person_actions) > 0
        assert person_rank >= 1

    def test_query_repositories_handle_empty_data(self):
        """Test query repositories handle empty data gracefully"""
        # Create empty repositories
        empty_action_repo = ConcreteActionQueryRepository()
        empty_activity_repo = ConcreteActivityQueryRepository()
        empty_leaderboard_repo = ConcreteLeaderboardQueryRepository()
        
        # Test empty results
        assert len(empty_action_repo.get_pending_validations()) == 0
        assert len(empty_action_repo.get_person_actions(PersonId(self.person_id))) == 0
        assert len(empty_activity_repo.get_active_activities()) == 0
        assert len(empty_leaderboard_repo.get_leaderboard()) == 0
        
        # Test error cases for empty repositories
        try:
            empty_activity_repo.get_activity_details(ActivityId(self.activity_id))
            assert False, "Should raise ValueError"
        except ValueError:
            pass
        
        try:
            empty_leaderboard_repo.get_person_rank(PersonId(self.person_id))
            assert False, "Should raise ValueError"
        except ValueError:
            pass