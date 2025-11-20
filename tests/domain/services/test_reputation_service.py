"""
Tests for ReputationService domain service.
Covers all calculation methods and business rules.
"""
from src.domain.services.reputation_service import ReputationService
from src.domain.person.person import Person
from src.domain.person.role import Role
from src.domain.action.action import Action
from src.domain.action.action_status import ActionStatus
from src.domain.activity.activity import Activity
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.shared.value_objects.action_id import ActionId
from src.domain.shared.value_objects.activity_id import ActivityId


class TestReputationService:
    """Test ReputationService domain service."""
    
    def test_reputation_service_instantiation(self):
        """Test ReputationService can be instantiated."""
        service = ReputationService()
        assert isinstance(service, ReputationService)
    
    def test_calculate_person_reputation_no_actions(self):
        """Test person reputation calculation with no actions."""
        service = ReputationService()
        
        person = Person(
            person_id=PersonId.generate(),
            name="Test User",
            email="test@example.com",
            role=Role.MEMBER
        )
        
        reputation = service.calculate_person_reputation(person, [])
        assert reputation == 0
    
    def test_calculate_person_reputation_member_with_actions(self):
        """Test person reputation calculation for member with verified actions."""
        service = ReputationService()
        
        person = Person(
            person_id=PersonId.generate(),
            name="Test User",
            email="test@example.com",
            role=Role.MEMBER
        )
        
        # Create verified actions
        verified_actions = [
            Action(
                action_id=ActionId.generate(),
                person_id=person.person_id,
                activity_id=ActivityId.generate(),
                proof="proof1",
                status=ActionStatus.VALIDATED
            ),
            Action(
                action_id=ActionId.generate(),
                person_id=person.person_id,
                activity_id=ActivityId.generate(),
                proof="proof2",
                status=ActionStatus.VALIDATED
            )
        ]
        
        reputation = service.calculate_person_reputation(person, verified_actions)
        # 2 actions * 10 points * 1.0 modifier = 20
        assert reputation == 20
    
    def test_calculate_person_reputation_lead_with_actions(self):
        """Test person reputation calculation for lead with verified actions."""
        service = ReputationService()
        
        person = Person(
            person_id=PersonId.generate(),
            name="Test Lead",
            email="lead@example.com",
            role=Role.LEAD
        )
        
        # Create verified actions
        verified_actions = [
            Action(
                action_id=ActionId.generate(),
                person_id=person.person_id,
                activity_id=ActivityId.generate(),
                proof="proof1",
                status=ActionStatus.VALIDATED
            )
        ]
        
        reputation = service.calculate_person_reputation(person, verified_actions)
        # 1 action * 10 points * 1.2 modifier = 12
        assert reputation == 12
    
    def test_calculate_activity_score_no_actions(self):
        """Test activity score calculation with no actions."""
        service = ReputationService()
        activity = Activity(
            activity_id=ActivityId.generate(),
            title="Test Activity",
            description="Test description",
            creator_id=PersonId.generate(),
            points=10
        )
        score = service.calculate_activity_score(activity, [])
        assert score == 0
    
    def test_calculate_activity_score_with_mixed_actions(self):
        """Test activity score calculation with mixed action statuses."""
        service = ReputationService()
        activity_id = ActivityId.generate()
        activity = Activity(
            activity_id=activity_id,
            title="Test Activity",
            description="Test description",
            creator_id=PersonId.generate(),
            points=10
        )
        # Create actions with different statuses
        all_actions = [
            Action(
                action_id=ActionId.generate(),
                person_id=PersonId.generate(),
                activity_id=activity_id,
                proof="proof1",
                status=ActionStatus.SUBMITTED
            ),
            Action(
                action_id=ActionId.generate(),
                person_id=PersonId.generate(),
                activity_id=activity_id,
                proof="proof2",
                status=ActionStatus.VALIDATED
            ),
            Action(
                action_id=ActionId.generate(),
                person_id=PersonId.generate(),
                activity_id=ActivityId.generate(),  # Different activity
                proof="proof3",
                status=ActionStatus.VALIDATED
            )
        ]
        
        score = service.calculate_activity_score(activity, all_actions)
        # 1 submitted (1 point) + 1 validated (1 + 2 = 3 points) = 4 total
        assert score == 4
    
    def test_is_person_eligible_for_role_upgrade_member_not_enough_actions(self):
        """Test role upgrade eligibility for member with insufficient actions."""
        service = ReputationService()
        
        person = Person(
            person_id=PersonId.generate(),
            name="Test User",
            email="test@example.com",
            role=Role.MEMBER
        )
        
        # Create less than 50 verified actions
        verified_actions = [
            Action(
                action_id=ActionId.generate(),
                person_id=person.person_id,
                activity_id=ActivityId.generate(),
                proof=f"proof{i}",
                status=ActionStatus.VALIDATED
            )
            for i in range(10)
        ]
        
        is_eligible = service.is_person_eligible_for_role_upgrade(person, verified_actions)
        assert is_eligible == False
    
    def test_is_person_eligible_for_role_upgrade_member_enough_actions(self):
        """Test role upgrade eligibility for member with sufficient actions."""
        service = ReputationService()
        
        person = Person(
            person_id=PersonId.generate(),
            name="Test User",
            email="test@example.com",
            role=Role.MEMBER
        )
        
        # Create 50+ verified actions
        verified_actions = [
            Action(
                action_id=ActionId.generate(),
                person_id=person.person_id,
                activity_id=ActivityId.generate(),
                proof=f"proof{i}",
                status=ActionStatus.VALIDATED
            )
            for i in range(60)
        ]
        
        is_eligible = service.is_person_eligible_for_role_upgrade(person, verified_actions)
        assert is_eligible == True
    
    def test_is_person_eligible_for_role_upgrade_lead(self):
        """Test role upgrade eligibility for existing lead."""
        service = ReputationService()
        
        person = Person(
            person_id=PersonId.generate(),
            name="Test Lead",
            email="lead@example.com",
            role=Role.LEAD
        )
        
        # Create many verified actions
        verified_actions = [
            Action(
                action_id=ActionId.generate(),
                person_id=person.person_id,
                activity_id=ActivityId.generate(),
                proof=f"proof{i}",
                status=ActionStatus.VALIDATED
            )
            for i in range(100)
        ]
        
        is_eligible = service.is_person_eligible_for_role_upgrade(person, verified_actions)
        assert is_eligible == False  # Leads don't need upgrades