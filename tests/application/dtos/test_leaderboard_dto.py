"""Comprehensive tests for LeaderboardDto"""

from typing import Dict, Any
from src.application.dtos.leaderboard_dto import LeaderboardDto


class TestLeaderboardDto:
    """Test suite for LeaderboardDto covering all methods and edge cases"""

    def setup_method(self):
        """Set up test fixtures"""
        self.valid_person_id = "550e8400-e29b-41d4-a716-446655440000"
        self.valid_name = "John Doe"
        self.valid_reputation_score = 85
        self.valid_rank = 5

    def test_dto_creation_with_valid_data(self):
        """Test creating DTO with valid data"""
        dto = LeaderboardDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            reputationScore=self.valid_reputation_score,
            rank=self.valid_rank
        )
        
        assert dto.personId == self.valid_person_id
        assert dto.name == self.valid_name
        assert dto.reputationScore == self.valid_reputation_score
        assert dto.rank == self.valid_rank

    def test_to_dict_conversion(self):
        """Test conversion to dictionary"""
        dto = LeaderboardDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            reputationScore=self.valid_reputation_score,
            rank=self.valid_rank
        )
        
        result_dict = dto.to_dict()
        
        expected_dict: Dict[str, Any] = {
            'personId': self.valid_person_id,
            'name': self.valid_name,
            'reputationScore': self.valid_reputation_score,
            'rank': self.valid_rank
        }
        
        assert result_dict == expected_dict

    def test_dto_with_first_rank(self):
        """Test DTO for first place in leaderboard"""
        dto = LeaderboardDto(
            personId=self.valid_person_id,
            name="Top Performer",
            reputationScore=1000,
            rank=1
        )
        
        assert dto.rank == 1
        assert dto.reputationScore == 1000

    def test_dto_with_zero_score(self):
        """Test DTO with zero reputation score"""
        dto = LeaderboardDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            reputationScore=0,
            rank=100
        )
        
        assert dto.reputationScore == 0
        result_dict = dto.to_dict()
        assert result_dict['reputationScore'] == 0

    def test_dto_with_negative_score(self):
        """Test DTO with negative reputation score"""
        dto = LeaderboardDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            reputationScore=-50,
            rank=150
        )
        
        assert dto.reputationScore == -50
        result_dict = dto.to_dict()
        assert result_dict['reputationScore'] == -50

    def test_dto_equality(self):
        """Test DTO equality comparison"""
        dto1 = LeaderboardDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            reputationScore=self.valid_reputation_score,
            rank=self.valid_rank
        )
        
        dto2 = LeaderboardDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            reputationScore=self.valid_reputation_score,
            rank=self.valid_rank
        )
        
        assert dto1 == dto2

    def test_dto_inequality(self):
        """Test DTO inequality comparison"""
        dto1 = LeaderboardDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            reputationScore=self.valid_reputation_score,
            rank=5
        )
        
        dto2 = LeaderboardDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            reputationScore=self.valid_reputation_score,
            rank=10  # Different rank
        )
        
        assert dto1 != dto2

    def test_dto_field_types(self):
        """Test that DTO fields have correct types"""
        dto = LeaderboardDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            reputationScore=self.valid_reputation_score,
            rank=self.valid_rank
        )
        
        assert isinstance(dto.personId, str)
        assert isinstance(dto.name, str)
        assert isinstance(dto.reputationScore, int)
        assert isinstance(dto.rank, int)

    def test_serialization_deserialization_round_trip(self):
        """Test that DTO can be serialized and deserialized consistently"""
        original_dto = LeaderboardDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            reputationScore=self.valid_reputation_score,
            rank=self.valid_rank
        )
        
        # Convert to dict (serialization)
        dto_dict = original_dto.to_dict()
        
        # Recreate from dict (deserialization)
        recreated_dto = LeaderboardDto(
            personId=dto_dict['personId'],
            name=dto_dict['name'],
            reputationScore=dto_dict['reputationScore'],
            rank=dto_dict['rank']
        )
        
        assert original_dto == recreated_dto

    def test_dto_hash(self):
        """Test DTO can be hashed"""
        dto = LeaderboardDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            reputationScore=self.valid_reputation_score,
            rank=self.valid_rank
        )
        
        # Should not raise any exception
        hash(dto)
        
        # Should work in sets
        dto_set = {dto}
        assert len(dto_set) == 1

    def test_dto_with_special_characters_in_name(self):
        """Test DTO with special characters in name"""
        special_name = "José María O'Connor-Smith"
        dto = LeaderboardDto(
            personId=self.valid_person_id,
            name=special_name,
            reputationScore=self.valid_reputation_score,
            rank=self.valid_rank
        )
        
        assert dto.name == special_name
        result_dict = dto.to_dict()
        assert result_dict['name'] == special_name

    def test_dto_leaderboard_ranking_scenarios(self):
        """Test various leaderboard ranking scenarios"""
        # Top performer
        top_dto = LeaderboardDto(
            personId="top-id",
            name="Top Player",
            reputationScore=2000,
            rank=1
        )
        
        # Middle performer  
        mid_dto = LeaderboardDto(
            personId="mid-id", 
            name="Average Player",
            reputationScore=500,
            rank=50
        )
        
        # Bottom performer
        bottom_dto = LeaderboardDto(
            personId="bottom-id",
            name="New Player",
            reputationScore=10,
            rank=200
        )
        
        assert top_dto.rank < mid_dto.rank < bottom_dto.rank
        assert top_dto.reputationScore > mid_dto.reputationScore > bottom_dto.reputationScore

    def test_dto_in_collections(self):
        """Test DTO behavior in collections"""
        dto1 = LeaderboardDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            reputationScore=self.valid_reputation_score,
            rank=self.valid_rank
        )
        
        dto2 = LeaderboardDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            reputationScore=self.valid_reputation_score,
            rank=self.valid_rank
        )
        
        different_dto = LeaderboardDto(
            personId="different-id",
            name="Different Person",
            reputationScore=100,
            rank=10
        )
        
        # Test in set (should deduplicate)
        dto_set = {dto1, dto2, different_dto}
        assert len(dto_set) == 2

    def test_dto_with_very_high_rank(self):
        """Test DTO with very high rank number"""
        dto = LeaderboardDto(
            personId=self.valid_person_id,
            name=self.valid_name,
            reputationScore=1,
            rank=999999
        )
        
        assert dto.rank == 999999
        result_dict = dto.to_dict()
        assert result_dict['rank'] == 999999