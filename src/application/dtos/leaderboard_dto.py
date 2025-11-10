"""LeaderboardDto - Data transfer object for leaderboard entry information"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class LeaderboardDto:
    """
    Data Transfer Object for leaderboard entry information.
    
    This DTO is used for read operations to return leaderboard data
    optimized for display in leaderboard views.
    
    Attributes:
        personId: Unique identifier of the person (as string)
        name: Full name of the person
        reputationScore: Current reputation score of the person
        rank: Position in the leaderboard (1-based ranking)
    """
    personId: str
    name: str
    reputationScore: int
    rank: int
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the DTO to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the leaderboard entry
        """
        return {
            'personId': self.personId,
            'name': self.name,
            'reputationScore': self.reputationScore,
            'rank': self.rank
        }