"""LeaderboardQueryRepository - Query-side repository interface for leaderboard operations"""

from abc import ABC, abstractmethod
from typing import List
from src.application.dtos.leaderboard_dto import LeaderboardDto


class LeaderboardQueryRepository(ABC):
    """
    Query-side repository interface for leaderboard operations.
    
    This interface defines read-only operations for leaderboard data,
    following the CQRS pattern for optimized read performance.
    Infrastructure layer implements this with primitive types only.
    """
    
    @abstractmethod
    def get_leaderboard(self) -> List[LeaderboardDto]:
        """
        Get the current leaderboard with all participants ranked by reputation score.
        
        Returns:
            List of LeaderboardDto objects ordered by rank (highest score first)
        """
        pass
    
    @abstractmethod
    def get_person_rank(self, person_id: str) -> int:
        """
        Get the current rank of a specific person in the leaderboard.
        
        Args:
            person_id: The ID of the person to get rank for (as string)
            
        Returns:
            The person's current rank (1-based, 1 = highest score)
            
        Raises:
            ValueError: If person not found
        """
        pass