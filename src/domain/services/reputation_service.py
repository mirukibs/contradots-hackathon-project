"""
Reputation Service implementation.
Provides domain services for reputation and activity score calculations.
"""

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..person.person import Person
    from ..activity.activity import Activity
    from ..action.action import Action


class ReputationService:
    """
    Domain service for calculating reputation scores and activity metrics.
    
    This service encapsulates the business logic for reputation calculations
    that spans across multiple aggregates and doesn't naturally belong to
    any single aggregate.
    """
    
    def calculate_person_reputation(self, person: "Person", verified_actions: List["Action"]) -> int:
        """
        Calculate the reputation score for a person based on their verified actions.
        
        Business rules:
        - Each verified action contributes 10 points to reputation
        - Minimum reputation is 0
        - Only VERIFIED actions count toward reputation
        
        Args:
            person: The Person aggregate to calculate reputation for
            verified_actions: List of verified actions by the person
            
        Returns:
            The calculated reputation score as an integer
        """
        if not verified_actions:
            return 0
        
        # Each verified action is worth 10 reputation points
        base_reputation = len(verified_actions) * 10
        
        # Apply role-based modifiers
        role_modifier = self._get_role_reputation_modifier(person)
        final_reputation = int(base_reputation * role_modifier)
        
        # Ensure reputation is never negative
        return max(0, final_reputation)
    
    def calculate_activity_score(self, activity: "Activity", all_actions: List["Action"]) -> int:
        """
        Calculate the engagement score for an activity based on submitted actions.
        
        Business rules:
        - Each submitted action (any status) contributes 1 point
        - Each verified action contributes an additional 2 points (3 total)
        - Minimum score is 0
        
        Args:
            activity: The Activity aggregate to calculate score for
            all_actions: List of all actions associated with the activity
            
        Returns:
            The calculated activity score as an integer
        """
        if not all_actions:
            return 0
        
        score = 0
        
        # Filter actions for this specific activity
        activity_actions = [
            action for action in all_actions 
            if action.activity_id == activity.activity_id
        ]
        
        for action in activity_actions:
            # Base point for any submitted action
            score += 1
            
            # Bonus points for verified actions
            if action.is_verified():
                score += 2
        
        return score
    
    def _get_role_reputation_modifier(self, person: "Person") -> float:
        """
        Get the reputation modifier based on person's role.
        
        Args:
            person: The Person aggregate
            
        Returns:
            Multiplier for reputation calculation based on role
        """
        from ..person.role import Role
        
        if person.role == Role.LEAD:
            return 1.2  # 20% bonus for leads
        else:  # Role.MEMBER
            return 1.0  # Standard modifier for members
    
    def is_person_eligible_for_role_upgrade(self, person: "Person", verified_actions: List["Action"]) -> bool:
        """
        Determine if a person is eligible for role upgrade based on their activity.
        
        Business rules:
        - Members can become leads if they have 50+ verified actions
        - Leads remain leads
        
        Args:
            person: The Person aggregate to check
            verified_actions: List of verified actions by the person
            
        Returns:
            True if the person is eligible for role upgrade, False otherwise
        """
        from ..person.role import Role
        
        # Leads don't need upgrades
        if person.role == Role.LEAD:
            return False
        
        # Members need 50+ verified actions to become leads
        verified_count = len(verified_actions)
        return verified_count >= 50